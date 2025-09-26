from pydantic import BaseModel
from uuid import UUID, uuid4
import datetime

from enum import StrEnum

# composio has the idea of toolkits and tools
# toolkits contain a literal shitton of tools, so it is important to only use a subset
# our agents should only have the most relevant tools for the job
# Conlcusion -- tools should be fetched dynamically from the toolkit,
# based on the extracted keywords from the prompt
Toolkit = str


class AgentStatus(StrEnum):
    """Agent deployment status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYED = "deployed"

class SaveAgentResponse(BaseModel):
    success: bool
    agent_id: str | None
