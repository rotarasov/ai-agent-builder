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
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"


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
    id: Optional[str] = Field(None, description="Agent ID")
    config: AgentConfig = Field(..., description="Agent configuration")
    status: AgentStatus = Field(AgentStatus.DRAFT, description="Agent status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    deployment_url: Optional[str] = Field(None, description="Deployment URL if deployed")


class CreateAgentRequest(BaseModel):
    """Request model for creating an agent"""
    config: AgentConfig = Field(..., description="Agent configuration")


class UpdateAgentRequest(BaseModel):
    """Request model for updating an agent"""
    config: Optional[AgentConfig] = Field(None, description="Updated agent configuration")
    status: Optional[AgentStatus] = Field(None, description="Updated agent status")


class AgentResponse(BaseModel):
    """Response model for agent operations"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent: Optional[Agent] = Field(None, description="Agent data")


class AgentListResponse(BaseModel):
    """Response model for listing agents"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agents: List[Agent] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")


# In-memory storage for demo purposes (replace with actual database)
agents_db: dict[str, Agent] = {}

@router.post("/agents", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest):
    """
    Create a new AI agent with the specified configuration.
    
    This endpoint allows you to create a new agent by providing its configuration
    including LLM provider, model, system prompt, and other settings.
    """
    try:
        # Generate unique ID for the agent
        agent_id = str(uuid.uuid4())
        
        # Create agent instance
        agent = Agent(
            id=agent_id,
            config=request.config,
            status=AgentStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deployment_url=None
        )
        
        # Store in database (replace with actual DB operations)
        agents_db[agent_id] = agent
        
        logger.info(f"Created agent {agent_id} with name '{request.config.name}'")
        
        return AgentResponse(
            success=True,
            message=f"Agent '{request.config.name}' created successfully",
            agent=agent
        )
    
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/agents", response_model=AgentListResponse)
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
        # Filter agents by status if provided
        filtered_agents = list(agents_db.values())
        if status:
            filtered_agents = [agent for agent in filtered_agents if agent.status == status]
        
        # Apply pagination
        total = len(filtered_agents)
        agents_page = filtered_agents[skip:skip + limit]
        
        return AgentListResponse(
            success=True,
            message=f"Retrieved {len(agents_page)} agents",
            agents=agents_page,
            total=total
        )
    
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """
    Retrieve a specific agent by its ID.
    
    Returns the complete agent configuration and metadata including
    status, creation time, and deployment information.
    """
    try:
        if agent_id not in agents_db:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents_db[agent_id]
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} retrieved successfully",
            agent=agent
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent: {str(e)}")


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, request: UpdateAgentRequest):
    """
    Update an existing agent's configuration or status.
    
    You can update the agent's configuration, change its status,
    or both. Only provided fields will be updated.
    """
    try:
        if agent_id not in agents_db:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents_db[agent_id]
        
        # Update configuration if provided
        if request.config:
            agent.config = request.config
        
        # Update status if provided
        if request.status:
            agent.status = request.status
        
        # Update timestamp
        agent.updated_at = datetime.now(timezone.utc)
        
        # Save updated agent
        agents_db[agent_id] = agent
        
        logger.info(f"Updated agent {agent_id}")
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} updated successfully",
            agent=agent
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@router.delete("/agents/{agent_id}", response_model=AgentResponse)
async def delete_agent(agent_id: str):
    """
    Delete an agent by its ID.
    
    This will permanently remove the agent and all its associated data.
    Use with caution as this operation cannot be undone.
    """
    try:
        if agent_id not in agents_db:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents_db[agent_id]
        
        # Remove from database
        del agents_db[agent_id]
        
        logger.info(f"Deleted agent {agent_id}")
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} deleted successfully",
            agent=agent
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@router.post("/agents/{agent_id}/deploy", response_model=AgentResponse)
async def deploy_agent(agent_id: str):
    """
    Deploy an agent to make it available for interactions.
    
    This endpoint handles the serverless deployment of the agent,
    including LLM interaction functions and orchestration.
    """
    try:
        if agent_id not in agents_db:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents_db[agent_id]
        
        # Check if agent is ready for deployment
        if agent.status == AgentStatus.DEPLOYED:
            return AgentResponse(
                success=True,
                message=f"Agent {agent_id} is already deployed",
                agent=agent
            )
        
        # TODO: Implement actual deployment logic
        # This would involve:
        # 1. Validating agent configuration
        # 2. Setting up serverless functions
        # 3. Configuring LLM provider connections
        # 4. Setting up orchestration
        
        # For now, simulate deployment
        deployment_url = f"https://api.agents.com/deployed/{agent_id}"
        agent.status = AgentStatus.DEPLOYED
        agent.deployment_url = deployment_url
        agent.updated_at = datetime.now(timezone.utc)
        
        agents_db[agent_id] = agent
        
        logger.info(f"Deployed agent {agent_id} to {deployment_url}")
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} deployed successfully",
            agent=agent
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy agent: {str(e)}")


@router.post("/agents/{agent_id}/undeploy", response_model=AgentResponse)
async def undeploy_agent(agent_id: str):
    """
    Undeploy an agent and make it inactive.
    
    This will stop the agent's serverless functions and make it
    unavailable for new interactions.
    """
    try:
        if agent_id not in agents_db:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents_db[agent_id]
        
        if agent.status != AgentStatus.DEPLOYED:
            return AgentResponse(
                success=True,
                message=f"Agent {agent_id} is not currently deployed",
                agent=agent
            )
        
        # TODO: Implement actual undeployment logic
        # This would involve tearing down serverless functions
        
        agent.status = AgentStatus.INACTIVE
        agent.deployment_url = None
        agent.updated_at = datetime.now(timezone.utc)
        
        agents_db[agent_id] = agent
        
        logger.info(f"Undeployed agent {agent_id}")
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} undeployed successfully",
            agent=agent
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error undeploying agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to undeploy agent: {str(e)}")
