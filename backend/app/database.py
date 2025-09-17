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
    
    # Call functions
    async def insert_call(self, call_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert new call"""
        try:
            result = self.client.table("calls").insert(call_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to insert call: {str(e)}")
            return None
    
    async def update_call_status(self, call_id: str, status: CallStatus, **kwargs) -> Optional[Dict]:
        """Update call status and other fields"""
        try:
            update_data = {"status": status, **kwargs}
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
    
    # Summary functions
    async def insert_summary(self, summary_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert call summary"""
        try:
            # Ensure structured_data has a default if not provided
            if 'structured_data' not in summary_data:
                summary_data['structured_data'] = {}
            
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
    
    # Test functions (updated for refined schema)
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

# Global database instance
db = Database()
