
# backend/app/routers/webhook.py
from fastapi import APIRouter, Request, HTTPException
from ..database import db
from ..services.data_processor import data_processor
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/retell")
async def handle_retell_webhook(request: Request):
    """Handle webhooks from Retell AI based on official documentation"""
    try:
        # Get raw body
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        
        event_type = payload.get("event")
        call_data = payload.get("call", {})
        call_id = call_data.get("call_id")
        
        logger.info(f"Retell webhook received: {event_type} for call {call_id}")
        
        if event_type == "call_started":
            await handle_call_started(call_data)
        elif event_type == "call_ended":
            await handle_call_ended(call_data)
        elif event_type == "call_analyzed":
            await handle_call_analyzed(call_data)
        else:
            logger.warning(f"Unknown webhook event: {event_type}")
        
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        # Return 200 to avoid retries for processing errors
        return {"status": "error", "message": str(e)}

async def handle_call_started(call_data: dict):
    """Handle call started event"""
    try:
        retell_call_id = call_data.get("call_id")
        metadata = call_data.get("metadata", {})
        internal_call_id = metadata.get("call_id")
        
        logger.info(f"Call started - Retell ID: {retell_call_id}, Internal ID: {internal_call_id}")
        
        if internal_call_id:
            # Update call status with additional info
            update_data = {
                "retell_call_id": retell_call_id,
                "from_number": call_data.get("from_number"),
                "to_number": call_data.get("to_number"),
                "start_timestamp": call_data.get("start_timestamp")
            }
            
            await db.update_call_status(internal_call_id, "in_progress", **update_data)
            logger.info(f"Updated call {internal_call_id} to in_progress")
        else:
            logger.warning(f"No internal call ID found in metadata for {retell_call_id}")
        
    except Exception as e:
        logger.error(f"Error handling call_started: {str(e)}")

async def handle_call_ended(call_data: dict):
    """Handle call ended event"""
    try:
        retell_call_id = call_data.get("call_id")
        metadata = call_data.get("metadata", {})
        internal_call_id = metadata.get("call_id")
        
        logger.info(f"Call ended - Retell ID: {retell_call_id}, Internal ID: {internal_call_id}")
        
        if internal_call_id:
            # Extract call information
            transcript = call_data.get("transcript", "")
            call_status = call_data.get("call_status", "completed")
            disconnection_reason = call_data.get("disconnection_reason", "unknown")
            end_timestamp = call_data.get("end_timestamp")
            
            # Determine our internal status based on call outcome
            if disconnection_reason in ["dial_failed", "dial_no_answer", "dial_busy"]:
                internal_status = "failed"
            elif disconnection_reason == "user_hangup":
                internal_status = "completed"
            elif disconnection_reason == "agent_hangup":
                internal_status = "completed"
            else:
                internal_status = "completed"
            
            # Update call record
            update_data = {
                "transcript": transcript,
                "ended_at": end_timestamp,
                "disconnection_reason": disconnection_reason,
                "call_status": call_status
            }
            
            await db.update_call_status(internal_call_id, internal_status, **update_data)
            
            # Process transcript if available and call was successful
            if transcript and internal_status == "completed":
                logger.info(f"Processing transcript for call {internal_call_id}")
                await data_processor.process_completed_call(internal_call_id, transcript)
            else:
                logger.info(f"No transcript to process for call {internal_call_id} (status: {internal_status})")
            
            logger.info(f"Call {internal_call_id} processed successfully")
        else:
            logger.warning(f"No internal call ID found in metadata for {retell_call_id}")
        
    except Exception as e:
        logger.error(f"Error handling call_ended: {str(e)}")

async def handle_call_analyzed(call_data: dict):
    """Handle call analysis completion"""
    try:
        retell_call_id = call_data.get("call_id")
        metadata = call_data.get("metadata", {})
        internal_call_id = metadata.get("call_id")
        
        # Extract analysis data if available
        call_analysis = call_data.get("call_analysis", {})
        
        logger.info(f"Call analyzed - Retell ID: {retell_call_id}, Internal ID: {internal_call_id}")
        
        if internal_call_id and call_analysis:
            # You can store additional analysis data here
            # For now, just log it
            logger.info(f"Call analysis available for {internal_call_id}: {list(call_analysis.keys())}")
            
            # Optionally update the call record with analysis data
            await db.update_call_status(
                internal_call_id, 
                None,  # Don't change status
                call_analysis=call_analysis
            )
        
    except Exception as e:
        logger.error(f"Error handling call_analyzed: {str(e)}")