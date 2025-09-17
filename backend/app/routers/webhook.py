from fastapi import APIRouter, Request, HTTPException
from ..database import db
import logging
import json
from ..services.data_processor import data_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/retell")
async def handle_retell_webhook(request: Request):
    """Handle webhooks from Retell AI"""
    try:
        # Get raw body
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        
        event_type = payload.get("event")
        call_id = payload.get("call_id")
        
        logger.info(f"Retell webhook: {event_type} for call {call_id}")
        
        if event_type == "call_started":
            await handle_call_started(payload)
        elif event_type == "call_ended":
            await handle_call_ended(payload)
        elif event_type == "call_analyzed":
            await handle_call_analyzed(payload)
        else:
            logger.warning(f"Unknown webhook event: {event_type}")
        
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def handle_call_started(payload):
    """Handle call started event"""
    try:
        retell_call_id = payload.get("call_id")
        metadata = payload.get("metadata", {})
        internal_call_id = metadata.get("call_id")
        
        if internal_call_id:
            await db.update_call_status(
                internal_call_id, 
                "in_progress",
                retell_call_id=retell_call_id
            )
            logger.info(f"Call started: {retell_call_id} -> {internal_call_id}")
        
    except Exception as e:
        logger.error(f"Error handling call_started: {str(e)}")

async def handle_call_ended(payload):
    """Handle call ended event"""
    try:
        retell_call_id = payload.get("call_id")
        transcript = payload.get("transcript", "")
        metadata = payload.get("metadata", {})
        internal_call_id = metadata.get("call_id")
        
        if internal_call_id:
            # Update call status
            await db.update_call_status(
                internal_call_id, 
                "completed",
                transcript=transcript,
                ended_at=payload.get("end_timestamp")
            )
            
            # Process transcript for structured data
            if transcript:
                await data_processor.process_completed_call(internal_call_id, transcript)
            
            logger.info(f"Call completed: {retell_call_id} -> {internal_call_id}")
        
    except Exception as e:
        logger.error(f"Error handling call_ended: {str(e)}")


async def handle_call_analyzed(payload):
    """Handle call analysis completion"""
    try:
        retell_call_id = payload.get("call_id")
        analysis = payload.get("analysis", {})
        
        logger.info(f"Call analyzed: {retell_call_id}")
        
        # Additional analysis data can be processed here
        
    except Exception as e:
        logger.error(f"Error handling call_analyzed: {str(e)}")