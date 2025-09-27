from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

from supabase import SupabaseAuthClient

from datetime import datetime

from src.models.agents import (
    Agent,
    AgentResponse,
    AgentSet,
    AgentSetSupabase,
    AgentSetListResponse,
    AgentSetResponse,
    AgentStatus,
    CreateAgentSetRequest,
    UpdateAgentRequest,
    UpdateAgentSetRequest,
)
from src.database.supabase import (
    get_authenticated_client,
    create_agent,
    create_agent_set,
    get_agents_in_set,
    get_agent_set as db_get_agent_set,
    get_agent_set_by_id
)
from src.config import config

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# In-memory storage for demo purposes (replace with actual database)
# agent_sets_db: dict[str, AgentSet] = {}


@router.post("/agent-sets/", response_model=AgentSetResponse)
async def post_agent_set(request: CreateAgentSetRequest):
    """
    Create a new AI agent with the specified configuration.

    This endpoint allows you to create a new agent by providing its configuration
    including LLM provider, model, system prompt, and other settings.
    """
    supabase_client = get_authenticated_client()

    agent_set = AgentSetSupabase()

    success, agent_set_id = create_agent_set(agent_set, supabase_client)

    if not success:
        return AgentSetResponse(
            success=False,
            message="Failed to create agent set.",
            agent_set=None,
        )

    try:
        # Create agent instances
        agents = request.agents

        for agent in agents:
            agent.agent_set = agent_set_id
            success, agent_id = create_agent(agent, supabase_client)
            agent.uuid = agent_id

        logger.info(f"Created agent set: {agent_set_id}")

        new_agent_set = AgentSet(**agent_set.model_dump(), agents=agents, name=request.name)

        return AgentSetResponse(
            success=True,
            message=f"Created {len(agents)} agents.",
            agent_set=new_agent_set,
        )

    except Exception as e:
        logger.error(f"Error creating agent set: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/agent-sets", response_model=AgentSetListResponse)
async def list_agents():
    """
    Retrieve a list of all agents with optional filtering and pagination.

    You can filter agents by status and use pagination parameters to control
    the number of results returned.
    """
    supabase_client = get_authenticated_client()

    try:
        # Filter agent sets by status if provided
        agent_sets = db_get_agent_set(supabase_client)

        return AgentSetListResponse(
            success=True,
            message=f"Retrieved agent sets.",
            agent_sets=agent_sets,
            total=len(agent_sets),
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

    supabase_client = get_authenticated_client()

    agent_set = get_agent_set_by_id(agent_set_id, supabase_client)
    if not agent_set:
        raise HTTPException(
            status_code=404, detail=f"Agent set {agent_set_id} not found"
        )

    agent_set = AgentSet(**agent_set.pop(), agents=[], name="")

    try:
        agents_in_set = get_agents_in_set(agent_set_id, supabase_client)
        print(agents_in_set)

        if not agents_in_set:
            raise HTTPException(
                status_code=404, detail=f"Agent set {agent_set_id} not found"
            )
        
        agent_set.agents = [Agent(**agent) for agent in agents_in_set]

        return AgentSetResponse(
            success=True,
            message=f"Agent set {agent_set_id} retrieved successfully",
            agent_set=agent_set,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent set {agent_set_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve agent: {str(e)}"
        )


# @router.put("/agent-sets/{agent_set_id}", response_model=AgentSetResponse)
# async def update_agent_set(agent_set_id: str, request: UpdateAgentSetRequest):
#     """
#     Update an existing agent set with new configuration.

#     This endpoint allows you to update an agent set's configuration,
#     including adding, removing, or modifying agents within the set.
#     """
#     try:
#         if agent_set_id not in agent_sets_db:
#             raise HTTPException(
#                 status_code=404, detail=f"Agent set {agent_set_id} not found"
#             )

#         if request.agent_set is None:
#             raise HTTPException(
#                 status_code=400, detail="Agent set configuration is required"
#             )

#         # Update the agent set
#         updated_agent_set = request.agent_set.model_copy()
#         updated_agent_set.id = agent_set_id  # Ensure ID consistency
#         updated_agent_set.updated_at = datetime.now(timezone.utc)

#         # Store updated agent set
#         agent_sets_db[agent_set_id] = updated_agent_set

#         logger.info(f"Updated agent set: {agent_set_id}")

#         return AgentSetResponse(
#             success=True,
#             message=f"Agent set {agent_set_id} updated successfully",
#             agent_set=updated_agent_set,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error updating agent set {agent_set_id}: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Failed to update agent set: {str(e)}"
#         )


# @router.delete("/agent-sets/{agent_set_id}", response_model=AgentSetResponse)
# async def delete_agent_set(agent_set_id: str):
#     """
#     Delete an agent set and all its associated agents.

#     This endpoint permanently removes an agent set from the system.
#     This action cannot be undone.
#     """
#     try:
#         if agent_set_id not in agent_sets_db:
#             raise HTTPException(
#                 status_code=404, detail=f"Agent set {agent_set_id} not found"
#             )

#         # Get the agent set before deletion for response
#         agent_set = agent_sets_db[agent_set_id]

#         # Remove from database
#         del agent_sets_db[agent_set_id]

#         logger.info(f"Deleted agent set: {agent_set_id}")

#         return AgentSetResponse(
#             success=True,
#             message=f"Agent set {agent_set_id} deleted successfully",
#             agent_set=agent_set,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error deleting agent set {agent_set_id}: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Failed to delete agent set: {str(e)}"
#         )
