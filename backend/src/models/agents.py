from datetime import datetime
from enum import StrEnum
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class LLMProvider(StrEnum):
    """Supported LLM providers"""
    APERTUS = "apertus"
    OPENAI = "openai"


class AgentStatus(StrEnum):
    """Agent deployment status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYED = "deployed"


class Agent(BaseModel):
    """Agent configuration model"""
    # Will be provided by Piotr
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Agent ID")
    name: str = Field(..., description="Agent name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Agent description", max_length=500)
    model_name: str = Field(..., description="Model name (e.g., gpt-4, claude-3)")
    system_prompt: str = Field(..., description="System prompt for the agent", min_length=1)
    tools: List[str] = Field(default_factory=list, description="Available tools for the agent")
    agent_set: str = Field(default="", description="Reference to the Agent Set UUID")
    context: str = Field(default="")



class AgentSetSupabase(BaseModel):
    """Agent set model"""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Agent set ID")
    name: str = Field(default="unnamed", description="Name of the Agentic System")
    status: AgentStatus = Field(default=AgentStatus.DRAFT, description="Agent set status")
    created_at: str = Field(default=datetime.now().isoformat(), description="Creation timestamp")

class AgentSet(AgentSetSupabase):
    """Agent set model"""
    agents: List[Agent] = Field(..., description="List of agents")
    name: str = Field(..., description="Name of Agentic system")


class CreateAgentSetRequest(BaseModel):
    """Request model for creating an agent"""
    agents: List[Agent] = Field(..., description="Agent configuration")

class UpdateAgentRequest(BaseModel):
    """Request model for updating an agent"""
    config: Optional[Agent] = Field(None, description="Updated agent configuration")


class AgentResponse(BaseModel):
    """Response model for agent operations"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    # agent: Optional[Agent] = Field(None, description="Agent data")


class AgentSetResponse(BaseModel):
    """Response model for listing agents"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent_set: Optional[AgentSet] = Field(..., description="Agent set")


class UpdateAgentSetRequest(BaseModel):
    """Request model for updating an agent set"""
    agent_set: Optional[AgentSet] = Field(None, description="Updated agent set configuration")
    status: Optional[AgentStatus] = Field(None, description="Updated agent status")


class AgentSetListResponse(BaseModel):
    """Response model for listing agent sets"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    agent_sets: list[dict] = Field(..., description="List of agent sets")
    total: int = Field(..., description="Total number of agent sets")
