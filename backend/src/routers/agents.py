from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    APERTUS = "apertus"
    OPENAI = "openai"


class AgentStatus(str, Enum):
    """Agent deployment status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYED = "deployed"


class AgentConfig(BaseModel):
    """Agent configuration model"""
    # Will be provided by Piotr
    name: str = Field(..., description="Agent name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Agent description", max_length=500)
    llm_provider: LLMProvider = Field(..., description="LLM provider")
    model_name: str = Field(..., description="Model name (e.g., gpt-4, claude-3)")
    system_prompt: str = Field(..., description="System prompt for the agent", min_length=1)
    temperature: float = Field(0.7, description="Temperature for LLM", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response", gt=0)
    tools: List[str] = Field(default_factory=list, description="Available tools for the agent")
    context_window: Optional[int] = Field(None, description="Context window size", gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Agent(BaseModel):
    """Agent model with database fields"""    
    id: str = Field(description="Agent ID")
    config: AgentConfig = Field(..., description="Agent configuration")
    status: AgentStatus = Field(AgentStatus.DRAFT, description="Agent status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class AgentSet(BaseModel):
    """Agent set model"""
    id: str = Field(description="Agent set ID")
    agents: List[Agent] = Field(..., description="List of agents")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class CreateAgentSetRequest(BaseModel):
    """Request model for creating an agent"""
    configs: List[AgentConfig] = Field(..., description="Agent configuration")


class UpdateAgentRequest(BaseModel):
    """Request model for updating an agent"""
    config: Optional[AgentConfig] = Field(None, description="Updated agent configuration")
    status: Optional[AgentStatus] = Field(None, description="Updated agent status")


class AgentResponse(BaseModel):
    """Response model for agent operations"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent: Optional[Agent] = Field(None, description="Agent data")


class AgentSetResponse(BaseModel):
    """Response model for listing agents"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent_set: AgentSet = Field(..., description="Agent set")


class UpdateAgentSetRequest(BaseModel):
    """Request model for updating an agent set"""
    agent_set: Optional[AgentSet] = Field(None, description="Updated agent set configuration")


class AgentSetListResponse(BaseModel):
    """Response model for listing agent sets"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent_sets: List[AgentSet] = Field(..., description="List of agent sets")
    total: int = Field(..., description="Total number of agent sets")


# In-memory storage for demo purposes (replace with actual database)
agent_sets_db: dict[str, AgentSet] = {}

@router.post("/agent-sets/", response_model=AgentSetResponse)
async def create_agent_set(request: CreateAgentSetRequest):
    """
    Create a new AI agent with the specified configuration.
    
    This endpoint allows you to create a new agent by providing its configuration
    including LLM provider, model, system prompt, and other settings.
    """
    try:
        agent_set_id = str(uuid.uuid4())
        
        # Create agent instances
        agents = [Agent(
            id=str(uuid.uuid4()),
            config=config,
            status=AgentStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ) for config in request.configs]
        
        # Store in database (replace with actual DB operations)
        agent_sets_db[agent_set_id] = AgentSet(
            id=agent_set_id,
            agents=agents,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        logger.info(f"Created agent set: {agent_set_id}")
        
        return AgentSetResponse(
            success=True,
            message=f"Created {len(agents)} agents.",
            agent_set=agent_sets_db[agent_set_id]
        )
    
    except Exception as e:
        logger.error(f"Error creating agent set: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/agent-sets", response_model=AgentSetResponse)
async def list_agents(
    skip: int = Query(0, ge=0, description="Number of agents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of agents to return"),
    status: Optional[AgentStatus] = Query(None, description="Filter by agent status")
):
    """
    Retrieve a list of all agents with optional filtering and pagination.
    
    You can filter agents by status and use pagination parameters to control
    the number of results returned.
    """
    try:
        # Filter agent sets by status if provided
        filtered_agent_sets = list(agent_sets_db.values())
        if status:
            # Filter agent sets that contain agents with the specified status
            filtered_agent_sets = [
                agent_set for agent_set in filtered_agent_sets 
                if any(agent.status == status for agent in agent_set.agents)
            ]
        
        # Apply pagination
        total = len(filtered_agent_sets)
        agent_sets_page = filtered_agent_sets[skip:skip + limit]
        
        return AgentSetListResponse(
            success=True,
            message=f"Retrieved {len(agent_sets_page)} agent sets",
            agent_sets=agent_sets_page,
            total=total
        )
    
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agent-sets/{agent_set_id}", response_model=AgentSetResponse)
async def get_agent_set(agent_set_id: str):
    """
    Retrieve a specific agent by its ID.
    
    Returns the complete agent configuration and metadata including
    status, creation time, and deployment information.
    """
    try:
        if agent_set_id not in agent_sets_db:
            raise HTTPException(status_code=404, detail=f"Agent set {agent_set_id} not found")
        
        agent_set = agent_sets_db[agent_set_id]
        
        return AgentSetResponse(
            success=True,
            message=f"Agent set {agent_set_id} retrieved successfully",
            agent_set=agent_set
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent set {agent_set_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent: {str(e)}")


@router.put("/agent-sets/{agent_set_id}", response_model=AgentSetResponse)
async def update_agent_set(agent_set_id: str, request: UpdateAgentSetRequest):
    """
    Update an existing agent set with new configuration.
    
    This endpoint allows you to update an agent set's configuration,
    including adding, removing, or modifying agents within the set.
    """
    try:
        if agent_set_id not in agent_sets_db:
            raise HTTPException(status_code=404, detail=f"Agent set {agent_set_id} not found")
        
        if request.agent_set is None:
            raise HTTPException(status_code=400, detail="Agent set configuration is required")
        
        # Update the agent set
        updated_agent_set = request.agent_set.model_copy()
        updated_agent_set.id = agent_set_id  # Ensure ID consistency
        updated_agent_set.updated_at = datetime.now(timezone.utc)
        
        # Store updated agent set
        agent_sets_db[agent_set_id] = updated_agent_set
        
        logger.info(f"Updated agent set: {agent_set_id}")
        
        return AgentSetResponse(
            success=True,
            message=f"Agent set {agent_set_id} updated successfully",
            agent_set=updated_agent_set
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent set {agent_set_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update agent set: {str(e)}")


@router.delete("/agent-sets/{agent_set_id}", response_model=AgentSetResponse)
async def delete_agent_set(agent_set_id: str):
    """
    Delete an agent set and all its associated agents.
    
    This endpoint permanently removes an agent set from the system.
    This action cannot be undone.
    """
    try:
        if agent_set_id not in agent_sets_db:
            raise HTTPException(status_code=404, detail=f"Agent set {agent_set_id} not found")
        
        # Get the agent set before deletion for response
        agent_set = agent_sets_db[agent_set_id]
        
        # Remove from database
        del agent_sets_db[agent_set_id]
        
        logger.info(f"Deleted agent set: {agent_set_id}")
        
        return AgentSetResponse(
            success=True,
            message=f"Agent set {agent_set_id} deleted successfully",
            agent_set=agent_set
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent set {agent_set_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent set: {str(e)}")