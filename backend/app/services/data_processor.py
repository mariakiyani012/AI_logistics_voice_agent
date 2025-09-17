# backend/app/services/data_processor.py
from ..database import db
from .openai_service import openai_service
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    
    async def process_completed_call(self, call_id: str, transcript: str) -> Optional[Dict[str, Any]]:
        """Process completed call transcript and save structured summary"""
        try:
            # Get call details
            call_data = await db.get_call_by_id(call_id)
            if not call_data:
                logger.error(f"Call {call_id} not found")
                return None
            
            # Get agent details to determine scenario type
            agent_data = call_data.get("agents", {})
            scenario_type = agent_data.get("scenario_type", "dispatch")
            
            # Extract structured data using OpenAI
            extraction_result = await openai_service.extract_call_summary(transcript, scenario_type)
            
            # Prepare summary data
            summary_data = {
                "call_id": call_id,
                "structured_data": extraction_result["structured_data"],
                "confidence_score": extraction_result["confidence_score"],
                "processing_errors": extraction_result["processing_errors"]
            }
            
            # Add scenario-specific fields
            structured_data = extraction_result["structured_data"]
            if scenario_type == "dispatch":
                summary_data.update({
                    "call_outcome": structured_data.get("call_outcome"),
                    "driver_status": structured_data.get("driver_status"),
                    "current_location": structured_data.get("current_location"),
                    "eta": structured_data.get("eta")
                })
            elif scenario_type == "emergency":
                summary_data.update({
                    "call_outcome": structured_data.get("call_outcome"),
                    "emergency_type": structured_data.get("emergency_type"),
                    "emergency_location": structured_data.get("emergency_location"),
                    "escalation_status": structured_data.get("escalation_status")
                })
            
            # Save summary to database
            saved_summary = await self.save_call_summary(summary_data)
            
            logger.info(f"Processed call {call_id} summary")
            return saved_summary
            
        except Exception as e:
            logger.error(f"Failed to process call {call_id}: {str(e)}")
            return None
    
    async def save_call_summary(self, summary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save call summary to database"""
        try:
            result = await db.insert_summary(summary_data)
            return result
        except Exception as e:
            logger.error(f"Failed to save summary: {str(e)}")
            return None

# Global processor instance
data_processor = DataProcessor()