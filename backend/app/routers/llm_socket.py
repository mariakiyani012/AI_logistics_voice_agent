# backend/app/routers/llm_websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.openai_service import openai_service
from ..database import db
import json
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/llm-websocket")
async def llm_websocket_handler(websocket: WebSocket):
    """Handle LLM WebSocket connections from Retell AI"""
    await websocket.accept()
    logger.info("LLM WebSocket connection established")
    
    try:
        while True:
            # Receive message from Retell
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            logger.info(f"Received LLM request: {request_data.get('interaction_type', 'unknown')}")
            
            # Handle different interaction types
            interaction_type = request_data.get("interaction_type")
            
            if interaction_type == "ping":
                # Respond to ping
                response = {"response_type": "pong"}
                await websocket.send_text(json.dumps(response))
                
            elif interaction_type == "reminder_required":
                # Handle reminder requests
                response = await handle_reminder_required(request_data)
                await websocket.send_text(json.dumps(response))
                
            elif interaction_type == "response_required":
                # Handle conversation responses
                response = await handle_response_required(request_data)
                await websocket.send_text(json.dumps(response))
                
            elif interaction_type == "update_only":
                # Handle conversation updates (no response needed)
                await handle_update_only(request_data)
                
            else:
                logger.warning(f"Unknown interaction type: {interaction_type}")
                
    except WebSocketDisconnect:
        logger.info("LLM WebSocket disconnected")
    except Exception as e:
        logger.error(f"LLM WebSocket error: {str(e)}")
        try:
            error_response = {
                "response_type": "error",
                "error": str(e)
            }
            await websocket.send_text(json.dumps(error_response))
        except:
            pass

async def handle_reminder_required(request_data: dict) -> dict:
    """Handle reminder_required interaction"""
    try:
        call_id = request_data.get("call_id")
        logger.info(f"Reminder required for call {call_id}")
        
        # Get call context from metadata
        call_details = request_data.get("call", {})
        metadata = call_details.get("metadata", {})
        
        driver_name = metadata.get("driver_name", "Driver")
        load_number = metadata.get("load_number", "Unknown")
        
        # Generate a contextual reminder
        reminder_content = f"Remember, you are speaking with {driver_name} about load {load_number}. Stay focused on getting the required dispatch information."
        
        return {
            "response_type": "reminder_required",
            "content": reminder_content
        }
        
    except Exception as e:
        logger.error(f"Error in handle_reminder_required: {str(e)}")
        return {
            "response_type": "error",
            "error": str(e)
        }

async def handle_response_required(request_data: dict) -> dict:
    """Handle response_required interaction - main conversation logic"""
    try:
        call_id = request_data.get("call_id")
        conversation = request_data.get("conversation", [])
        
        logger.info(f"Response required for call {call_id}")
        
        # Get call context
        call_details = request_data.get("call", {})
        metadata = call_details.get("metadata", {})
        
        # Get agent configuration from our database using metadata
        internal_call_id = metadata.get("call_id")
        agent_config = None
        
        if internal_call_id:
            call_record = await db.get_call_by_id(internal_call_id)
            if call_record:
                agent_config = await db.get_agent_by_id(call_record["agent_id"])
        
        # Use OpenAI to generate response
        response_content = await openai_service.generate_call_response(
            conversation=conversation,
            agent_config=agent_config,
            call_metadata=metadata
        )
        
        return {
            "response_type": "response",
            "content": response_content,
            "content_complete": True,
            "end_call": False
        }
        
    except Exception as e:
        logger.error(f"Error in handle_response_required: {str(e)}")
        return {
            "response_type": "error",
            "error": str(e)
        }

async def handle_update_only(request_data: dict):
    """Handle update_only interaction - conversation logging"""
    try:
        call_id = request_data.get("call_id")
        conversation = request_data.get("conversation", [])
        
        logger.info(f"Conversation update for call {call_id}")
        
        # Log conversation progress
        if conversation:
            last_message = conversation[-1]
            logger.info(f"Last message - {last_message.get('role', 'unknown')}: {last_message.get('content', '')[:100]}...")
        
        # You could store conversation updates in database here if needed
        # For now, just log them
        
    except Exception as e:
        logger.error(f"Error in handle_update_only: {str(e)}")