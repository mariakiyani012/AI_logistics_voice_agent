# backend/app/services/openai_service.py
import openai
from ..config import settings
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

openai.api_key = settings.openai_api_key

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_agent_response(self, 
                                    system_prompt: str, 
                                    user_message: str,
                                    driver_name: str = "",
                                    load_number: str = "") -> str:
        """Generate AI response for live conversation"""
        try:
            # Format system prompt with variables
            formatted_prompt = system_prompt.format(
                driver_name=driver_name,
                load_number=load_number
            )
            
            messages = [
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "I'm sorry, I'm having trouble processing that right now."
    
    async def extract_call_summary(self, transcript: str, scenario_type: str) -> Dict[str, Any]:
        """Extract structured data from call transcript"""
        try:
            prompts = {
                "dispatch": """
                Analyze this driver call transcript and extract the following information in JSON format:
                - call_outcome: "In-Transit Update" OR "Arrival Confirmation" OR "No Update"
                - driver_status: "Driving" OR "Delayed" OR "Arrived" OR "Unknown"
                - current_location: exact location mentioned or "Not provided"
                - eta: estimated time of arrival or "Not provided"
                
                Return only valid JSON. If information is unclear, use the fallback values.
                
                Transcript: {transcript}
                """,
                "emergency": """
                Analyze this emergency call transcript and extract the following information in JSON format:
                - call_outcome: "Emergency Detected"
                - emergency_type: "Accident" OR "Breakdown" OR "Medical" OR "Other"
                - emergency_location: exact location mentioned or "Not provided"
                - escalation_status: "Escalation Flagged"
                
                Return only valid JSON.
                
                Transcript: {transcript}
                """
            }
            
            prompt = prompts.get(scenario_type, prompts["dispatch"])
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt.format(transcript=transcript)}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                structured_data = json.loads(content)
                return {
                    "structured_data": structured_data,
                    "confidence_score": 0.9,
                    "processing_errors": []
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI response as JSON: {content}")
                return {
                    "structured_data": {"error": "Failed to parse response"},
                    "confidence_score": 0.1,
                    "processing_errors": ["JSON parsing failed"]
                }
                
        except Exception as e:
            logger.error(f"OpenAI extraction error: {str(e)}")
            return {
                "structured_data": {"error": "OpenAI API error"},
                "confidence_score": 0.0,
                "processing_errors": [str(e)]
            }

# Global service instance
openai_service = OpenAIService()