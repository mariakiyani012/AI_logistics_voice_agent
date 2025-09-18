# backend/app/database.py
from supabase import create_client, Client
from .config import settings
import logging
from typing import List, Dict, Optional, Any, Literal

logger = logging.getLogger(__name__)

# Type hints for ENUMs
CallStatus = Literal["pending", "in_progress", "completed", "failed", "cancelled"]
ScenarioType = Literal["dispatch", "emergency"]

class Database:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    # Test connection
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.client.table("agents").select("count").execute()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    # Agent functions
    async def insert_agent(self, agent_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert new agent"""
        try:
            result = self.client.table("agents").insert(agent_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to insert agent: {str(e)}")
            return None
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        try:
            result = self.client.table("agents").select("*").eq("id", agent_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get agent: {str(e)}")
            return None
    
    async def get_all_agents(self) -> List[Dict]:
        """Get all active agents"""
        try:
            result = self.client.table("agents").select("*").eq("is_active", True).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to fetch agents: {str(e)}")
            return []
    
    async def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Optional[Dict]:
        """Update agent"""
        try:
            result = self.client.table("agents").update(agent_data).eq("id", agent_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update agent: {str(e)}")
            return None
    
    # Call functions with enhanced Retell support
    async def insert_call(self, call_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert new call"""
        try:
            result = self.client.table("calls").insert(call_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to insert call: {str(e)}")
            return None
    
    async def update_call_status(self, call_id: str, status: CallStatus = None, **kwargs) -> Optional[Dict]:
        """Update call status and other fields"""
        try:
            update_data = {}
            
            # Only update status if provided
            if status is not None:
                update_data["status"] = status
            
            # Add all other fields
            update_data.update(kwargs)
            
            # Don't update if no data to update
            if not update_data:
                return None
            
            result = self.client.table("calls").update(update_data).eq("id", call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update call: {str(e)}")
            return None
    
    async def get_call_by_id(self, call_id: str) -> Optional[Dict]:
        """Get call by ID with agent info"""
        try:
            result = self.client.table("calls").select("*, agents(name, scenario_type)").eq("id", call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get call: {str(e)}")
            return None
    
    async def get_call_by_retell_id(self, retell_call_id: str) -> Optional[Dict]:
        """Get call by Retell call ID"""
        try:
            result = self.client.table("calls").select("*, agents(name, scenario_type)").eq("retell_call_id", retell_call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get call by retell_call_id: {str(e)}")
            return None
    
    async def get_calls_history(self, limit: int = 50) -> List[Dict]:
        """Get calls history with agent info"""
        try:
            result = self.client.table("calls").select(
                "*, agents(name, scenario_type)"
            ).order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get calls history: {str(e)}")
            return []
    
    # Summary functions with enhanced error handling
    async def insert_summary(self, summary_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert call summary"""
        try:
            # Ensure structured_data has a default if not provided
            if 'structured_data' not in summary_data:
                summary_data['structured_data'] = {}
            
            # Ensure confidence_score is a float
            if 'confidence_score' in summary_data:
                summary_data['confidence_score'] = float(summary_data['confidence_score'])
            
            # Ensure processing_errors is a list
            if 'processing_errors' in summary_data:
                if not isinstance(summary_data['processing_errors'], list):
                    summary_data['processing_errors'] = []
            
            result = self.client.table("summaries").insert(summary_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to insert summary: {str(e)}")
            return None
    
    async def get_summary_by_call_id(self, call_id: str) -> Optional[Dict]:
        """Get summary by call ID"""
        try:
            result = self.client.table("summaries").select("*").eq("call_id", call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get summary: {str(e)}")
            return None
    
    async def update_summary(self, call_id: str, summary_data: Dict[str, Any]) -> Optional[Dict]:
        """Update existing summary"""
        try:
            result = self.client.table("summaries").update(summary_data).eq("call_id", call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update summary: {str(e)}")
            return None
    
    # Enhanced test functions
    async def insert_test_agent(self) -> Optional[Dict]:
        """Insert a test agent for verification"""
        try:
            result = self.client.table("agents").insert({
                "name": "Test Agent API",
                "system_prompt": "Hello {driver_name}, I'm calling about load {load_number}. Can you give me an update on your status?",
                "scenario_type": "dispatch",
                "voice_settings": {
                    "voice": "female",
                    "speed": 1.0,
                    "interruption_sensitivity": 0.5
                }
            }).execute()
            
            if result.data:
                logger.info(f"Test agent inserted with ID: {result.data[0]['id']}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to insert test agent: {str(e)}")
            return None
    
    async def get_call_statistics(self) -> Dict[str, Any]:
        """Get call statistics for monitoring"""
        try:
            # Get total calls
            total_calls = self.client.table("calls").select("count").execute()
            
            # Get calls by status
            pending_calls = self.client.table("calls").select("count").eq("status", "pending").execute()
            in_progress_calls = self.client.table("calls").select("count").eq("status", "in_progress").execute()
            completed_calls = self.client.table("calls").select("count").eq("status", "completed").execute()
            failed_calls = self.client.table("calls").select("count").eq("status", "failed").execute()
            
            # Get recent calls
            recent_calls = self.client.table("calls").select("*").order("created_at", desc=True).limit(10).execute()
            
            return {
                "total_calls": len(total_calls.data) if total_calls.data else 0,
                "pending": len(pending_calls.data) if pending_calls.data else 0,
                "in_progress": len(in_progress_calls.data) if in_progress_calls.data else 0,
                "completed": len(completed_calls.data) if completed_calls.data else 0,
                "failed": len(failed_calls.data) if failed_calls.data else 0,
                "recent_calls": recent_calls.data[:5] if recent_calls.data else []
            }
        except Exception as e:
            logger.error(f"Failed to get call statistics: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_old_calls(self, days: int = 30) -> int:
        """Clean up old call records (optional maintenance function)"""
        try:
            # This is a placeholder - implement based on your retention needs
            logger.info(f"Cleanup function called for calls older than {days} days")
            return 0
        except Exception as e:
            logger.error(f"Failed to cleanup old calls: {str(e)}")
            return 0

# Global database instance
db = Database()