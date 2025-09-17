
# backend/app/routers/agent.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import db
from ..models import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse, MessageResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=AgentListResponse)
async def get_all_agents():
    """Get all active agents"""
    try:
        agents_data = await db.get_all_agents()
        agents = [AgentResponse(**agent) for agent in agents_data]
        return AgentListResponse(agents=agents, total=len(agents))
    except Exception as e:
        logger.error(f"Failed to fetch agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agents")

@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent configuration"""
    try:
        # Convert Pydantic model to dict
        agent_dict = agent_data.dict()
        
        # Insert into database
        created_agent = await db.insert_agent(agent_dict)
        
        if not created_agent:
            raise HTTPException(status_code=400, detail="Failed to create agent")
        
        return AgentResponse(**created_agent)
    except ValueError as e:
        # Validation errors from Pydantic
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create agent")

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    try:
        agent_data = await db.get_agent_by_id(agent_id)
        
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(**agent_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent")

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_data: AgentUpdate):
    """Update an existing agent configuration"""
    try:
        # Check if agent exists
        existing_agent = await db.get_agent_by_id(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Convert to dict and filter out None values
        update_dict = {k: v for k, v in agent_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update in database
        updated_agent = await db.update_agent(agent_id, update_dict)
        
        if not updated_agent:
            raise HTTPException(status_code=400, detail="Failed to update agent")
        
        return AgentResponse(**updated_agent)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update agent")

@router.delete("/{agent_id}", response_model=MessageResponse)
async def delete_agent(agent_id: str):
    """Soft delete an agent (set is_active=false)"""
    try:
        # Check if agent exists
        existing_agent = await db.get_agent_by_id(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Soft delete by setting is_active=false
        updated_agent = await db.update_agent(agent_id, {"is_active": False})
        
        if not updated_agent:
            raise HTTPException(status_code=400, detail="Failed to delete agent")
        
        return MessageResponse(message=f"Agent '{existing_agent['name']}' successfully deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")

