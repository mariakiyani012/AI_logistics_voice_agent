
# backend/app/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime

# ENUM types matching database schema
ScenarioType = Literal["dispatch", "emergency"]

# Request Models
class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    system_prompt: str = Field(..., min_length=10, description="System prompt with {driver_name} and {load_number} placeholders")
    scenario_type: ScenarioType = Field(default="dispatch", description="Agent scenario type")
    voice_settings: Dict[str, Any] = Field(default_factory=dict, description="Voice configuration settings")
    
    @validator('system_prompt')
    def validate_prompt_placeholders(cls, v):
        required_placeholders = ["{driver_name}", "{load_number}"]
        missing_placeholders = [p for p in required_placeholders if p not in v]
        if missing_placeholders:
            raise ValueError(f"System prompt must contain placeholders: {missing_placeholders}")
        return v
    
    @validator('voice_settings')
    def validate_voice_settings(cls, v):
        # Optional validation for voice settings structure
        allowed_keys = {"voice", "speed", "interruption_sensitivity", "backchanneling"}
        if v and not all(key in allowed_keys for key in v.keys()):
            unknown_keys = [key for key in v.keys() if key not in allowed_keys]
            raise ValueError(f"Unknown voice settings keys: {unknown_keys}")
        return v

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    system_prompt: Optional[str] = Field(None, min_length=10)
    scenario_type: Optional[ScenarioType] = None
    voice_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    @validator('system_prompt')
    def validate_prompt_placeholders(cls, v):
        if v is not None:
            required_placeholders = ["{driver_name}", "{load_number}"]
            missing_placeholders = [p for p in required_placeholders if p not in v]
            if missing_placeholders:
                raise ValueError(f"System prompt must contain placeholders: {missing_placeholders}")
        return v

# Response Models
class AgentResponse(BaseModel):
    id: str
    name: str
    system_prompt: str
    scenario_type: ScenarioType
    voice_settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int

# Generic response models
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Call Models
CallStatus = Literal["pending", "in_progress", "completed", "failed", "cancelled"]

class CallTrigger(BaseModel):
    agent_id: str = Field(..., description="Agent ID to use for the call")
    driver_name: str = Field(..., min_length=1, max_length=100)
    driver_phone: str = Field(..., regex=r'^\+?1?[0-9]{10,15}$')
    load_number: str = Field(..., min_length=1, max_length=50)

class CallResponse(BaseModel):
    id: str
    agent_id: str
    retell_call_id: Optional[str] = None
    driver_name: str
    driver_phone: str
    load_number: str
    status: CallStatus
    transcript: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CallListResponse(BaseModel):
    calls: list[CallResponse]
    total: int

# Summary Models
class SummaryResponse(BaseModel):
    id: str
    call_id: str
    call_outcome: Optional[str] = None
    driver_status: Optional[str] = None
    current_location: Optional[str] = None
    eta: Optional[str] = None
    emergency_type: Optional[str] = None
    emergency_location: Optional[str] = None
    escalation_status: Optional[str] = None
    structured_data: Dict[str, Any]
    full_transcript: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Generic response models
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None