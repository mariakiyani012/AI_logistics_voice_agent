
# backend/app/services/retell_service.py
import httpx
from ..config import settings
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class RetellService:
    def __init__(self):
        self.api_key = settings.retell_api_key
        self.base_url = "https://api.retellai.com"
        self.webhook_url = f"{settings.webhook_base_url}/webhook/retell"
        self._account_cache = None
        self._phone_cache = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for Retell API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Retell API connection by listing phone numbers"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/list-phone-numbers",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    phone_data = response.json()
                    phone_numbers = phone_data if isinstance(phone_data, list) else [phone_data]
                    
                    status = {
                        "connected": True,
                        "api_key_valid": True,
                        "phone_numbers": phone_numbers,
                        "phone_numbers_count": len(phone_numbers),
                        "primary_phone": phone_numbers[0].get("phone_number") if phone_numbers else None,
                        "can_make_calls": len(phone_numbers) > 0,
                        "webhook_url": self.webhook_url
                    }
                    
                    if not phone_numbers:
                        status["warnings"] = ["No phone numbers found - purchase a phone number in Retell dashboard"]
                    
                    return status
                    
                elif response.status_code == 401:
                    return {
                        "connected": False,
                        "error": "Invalid API key",
                        "can_make_calls": False
                    }
                else:
                    return {
                        "connected": False,
                        "error": f"API returned {response.status_code}: {response.text}",
                        "can_make_calls": False
                    }
                    
        except Exception as e:
            logger.error(f"Error testing connection: {str(e)}")
            return {
                "connected": False,
                "error": str(e),
                "can_make_calls": False
            }
    
    async def get_phone_numbers(self) -> List[Dict[str, Any]]:
        """Get all purchased phone numbers"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/list-phone-numbers",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    phone_data = response.json()
                    return phone_data if isinstance(phone_data, list) else [phone_data]
                else:
                    logger.error(f"Failed to get phone numbers: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching phone numbers: {str(e)}")
            return []
    
    async def create_llm_config(self, agent_config: Dict[str, Any]) -> Optional[str]:
        """Create an LLM configuration and return the LLM ID"""
        try:
            system_prompt = agent_config.get("system_prompt", "You are a helpful logistics assistant.")
            
            payload = {
                "general_prompt": system_prompt,
                "general_tools": [],
                "llm_websocket_url": f"{settings.webhook_base_url}/llm-websocket"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-retell-llm",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=15.0
                )
                
                if response.status_code == 201:
                    result = response.json()
                    llm_id = result.get("llm_id")
                    logger.info(f"LLM configuration created: {llm_id}")
                    return llm_id
                else:
                    logger.error(f"Failed to create LLM config: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating LLM config: {str(e)}")
            return None
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a Retell agent configuration"""
        try:
            # First create LLM configuration
            llm_id = await self.create_llm_config(agent_config)
            if not llm_id:
                return {"error": "Failed to create LLM configuration"}
            
            # Extract voice settings
            voice_settings = agent_config.get("voice_settings", {})
            
            # Map voice settings to Retell format
            voice_id = "11labs-Adrian"  # Default voice that works
            if voice_settings.get("voice") == "male":
                voice_id = "11labs-Adam"
            elif voice_settings.get("voice") == "female":
                voice_id = "11labs-Sophia"
            
            # Use minimal payload that works (from debug test)
            payload = {
                "response_engine": {
                    "type": "retell-llm",
                    "llm_id": llm_id
                },
                "voice_id": voice_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-agent",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=15.0
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Agent created successfully: {result.get('agent_id')}")
                    return result
                else:
                    logger.error(f"Failed to create agent: {response.status_code} - {response.text}")
                    return {"error": f"API Error {response.status_code}", "details": response.text}
                    
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return {"error": "Exception", "details": str(e)}
    
    async def create_retell_call(self, 
                               phone_number: str,
                               agent_config: Dict[str, Any],
                               metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create outbound call using Retell API"""
        try:
            # Get available phone numbers
            phone_numbers = await self.get_phone_numbers()
            
            if not phone_numbers:
                return {"error": "No phone numbers available", "details": "Purchase a phone number first"}
            
            from_number = phone_numbers[0].get("phone_number")
            if not from_number:
                return {"error": "Invalid phone number format", "details": "Phone number not found in response"}
            
            # Create or get agent
            agent_result = await self.create_agent(agent_config)
            if not agent_result or agent_result.get("error"):
                return {"error": "Failed to create agent", "details": agent_result}
            
            agent_id = agent_result.get("agent_id")
            
            # Prepare dynamic variables for the call
            dynamic_variables = {}
            if metadata:
                dynamic_variables["driver_name"] = metadata.get("driver_name", "")
                dynamic_variables["load_number"] = metadata.get("load_number", "")
            
            # Create call payload
            payload = {
                "from_number": from_number,
                "to_number": phone_number,
                "agent_id": agent_id,
                "retell_llm_dynamic_variables": dynamic_variables,
                "metadata": metadata or {}
            }
            
            logger.info(f"Creating call from {from_number} to {phone_number} with agent {agent_id}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-phone-call",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=15.0
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Call created successfully: {result.get('call_id')}")
                    return result
                else:
                    error_text = response.text
                    logger.error(f"Call creation failed: {response.status_code} - {error_text}")
                    return {"error": f"API Error {response.status_code}", "details": error_text}
                    
        except Exception as e:
            logger.error(f"Failed to create call: {str(e)}")
            return {"error": "Exception", "details": str(e)}
    
    async def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call details by call ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-call/{call_id}",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get call details: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting call details: {str(e)}")
            return None

# Global service instance
retell_service = RetellService()