# backend/app/services/retell_service.py
import httpx
from ..config import settings
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RetellService:
    def __init__(self):
        self.api_key = settings.retell_api_key
        self.base_url = "https://api.retellai.com/v2"
        self.webhook_url = f"{settings.webhook_base_url}/api/webhook/retell"
    
    async def create_retell_call(self, 
                               phone_number: str,
                               agent_config: Dict[str, Any],
                               metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create outbound call via Retell AI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from_number": "+1234567890",  # Your Retell phone number
                "to_number": phone_number,
                "override_agent_id": None,  # Use dynamic agent
                "retell_llm_dynamic_variables": {
                    "driver_name": metadata.get("driver_name", "") if metadata else "",
                    "load_number": metadata.get("load_number", "") if metadata else ""
                },
                "metadata": metadata or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-phone-call",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    logger.error(f"Retell API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to create Retell call: {str(e)}")
            return None
    
    async def get_call_status(self, retell_call_id: str) -> Optional[Dict[str, Any]]:
        """Get call status from Retell AI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-call/{retell_call_id}",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get call status: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            return None
    
    async def register_webhook(self) -> bool:
        """Register webhook URL with Retell (if needed)"""
        try:
            # This depends on Retell's webhook registration API
            # For now, return True assuming webhook is configured in dashboard
            logger.info(f"Webhook URL: {self.webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register webhook: {str(e)}")
            return False

# Global service instance  
retell_service = RetellService()