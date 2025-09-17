from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import db
from ..models import CallTrigger, CallResponse, CallListResponse, SummaryResponse, MessageResponse
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["calls"])

@router.post("/trigger", response_model=CallResponse, status_code=201)
async def trigger_call(call_data: CallTrigger):
    """Trigger a new outbound call"""
    try:
        # Check if agent exists
        agent = await db.get_agent_by_id(call_data.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create call record
        call_dict = {
            "id": str(uuid.uuid4()),
            "agent_id": call_data.agent_id,
            "driver_name": call_data.driver_name,
            "driver_phone": call_data.driver_phone,
            "load_number": call_data.load_number,
            "status": "pending"
        }
        
        created_call = await db.insert_call(call_dict)
        
        if not created_call:
            raise HTTPException(status_code=400, detail="Failed to create call")
        
        # TODO: Integrate Retell AI call creation
        logger.info(f"Call triggered: {created_call['id']}")
        
        return CallResponse(**created_call)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger call: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger call")

@router.get("/", response_model=CallListResponse)
async def get_all_calls():
    """Get all calls history"""
    try:
        calls_data = await db.get_calls_history()
        calls = [CallResponse(**call) for call in calls_data]
        return CallListResponse(calls=calls, total=len(calls))
    except Exception as e:
        logger.error(f"Failed to fetch calls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")

@router.get("/{call_id}", response_model=CallResponse)
async def get_call(call_id: str):
    """Get specific call by ID"""
    try:
        call_data = await db.get_call_by_id(call_id)
        
        if not call_data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return CallResponse(**call_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch call")

@router.get("/{call_id}/summary", response_model=SummaryResponse)
async def get_call_summary(call_id: str):
    """Get call summary by call ID"""
    try:
        # Check if call exists
        call_data = await db.get_call_by_id(call_id)
        if not call_data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Get summary
        summary_data = await db.get_summary_by_call_id(call_id)
        if not summary_data:
            raise HTTPException(status_code=404, detail="Call summary not found")
        
        return SummaryResponse(**summary_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch call summary {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch call summary")