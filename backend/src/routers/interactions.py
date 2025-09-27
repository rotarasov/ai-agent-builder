from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import logging
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from src.deps import ComposioClient
from src.services.agent_handlers.orchestrator import orchestrator_create_tasks, orchestrator_execute_next_task, orchestrator_summarize_execution, OrchestratorState
from src.services.agent_handlers.user_agent import user_agent_completion
from src.database.supabase import get_agents_in_set, get_authenticated_client
from src.models.agents import Agent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

class Message(BaseModel):
    """Message model for agent interactions"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    # metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationRequest(BaseModel):
    """Request model for agent interaction"""
    agent_set_id: str = Field(..., description="Agent set ID")
    message: str = Field(..., description="User message", min_length=1)
    # context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class MessageRequest(BaseModel):
    """Request model for sending a message to an existing conversation"""
    message: str = Field(..., description="User message", min_length=1)
    # context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ConversationResponse(BaseModel):
    """Response model for agent interaction"""
    success: bool = Field(..., description="Interaction success status")
    message: str = Field(..., description="Response message")
    agent_response: Optional[str] = Field(None, description="Agent's response")
    conversation_id: str = Field(..., description="Conversation ID")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")


class Conversation(BaseModel):
    """Conversation model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Conversation ID")
    agent_set_id: str = Field(..., description="Agent set ID")
    messages: List[Message] = Field(default_factory=list, description="Conversation messages")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationListResponse(BaseModel):
    """Response model for listing conversations"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    conversations: List[Conversation] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")


class ActionLog(BaseModel):
    """Action log model for agent context management"""
    id: Optional[str] = Field(None, description="Log entry ID")
    agent_id: str = Field(..., description="Agent ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    action: str = Field(..., description="Action performed")
    input_data: Dict[str, Any] = Field(..., description="Input data for the action")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from the action")
    timestamp: Optional[datetime] = Field(None, description="Action timestamp")
    success: bool = Field(..., description="Action success status")
    error_message: Optional[str] = Field(None, description="Error message if action failed")


# In-memory storage for demo purposes (replace with actual database)
conversations_db: dict[str, Conversation] = {}
orchestrator_states_db: dict[str, OrchestratorState] = {}
action_logs_db: dict[str, ActionLog] = {}


@router.post("/conversations", response_model=ConversationResponse)
async def start_conversation(request: ConversationRequest, composio_client: ComposioClient):
    """
    Send a message to an agent and get a response.
    
    This is the main interaction endpoint that forwards prompts to agents
    and returns their responses. It handles conversation context and
    logs all interactions for future reference.
    """
    supabase_client = get_authenticated_client()
    
    try:
        conversation = Conversation(
            agent_set_id=request.agent_set_id,
            messages=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        conversations_db[conversation.id] = conversation
        
        # Add user message to conversation
        user_message = Message(
            role="user",
            content=request.message,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(user_message)
        
        # Log the interaction
        # action_log = ActionLog(
        #     id=str(uuid.uuid4()),
        #     agent_id=request.agent_id,
        #     conversation_id=conversation_id,
        #     action="user_message",
        #     input_data={
        #         "message": request.message,
        #         "context": request.context or {}
        #     },
        #     output_data={},
        #     error_message=None,
        #     timestamp=datetime.now(timezone.utc),
        #     success=True
        # )
        # action_logs_db[action_log.id] = action_log
        
        agents = [Agent(**agent) for agent in get_agents_in_set(request.agent_set_id, supabase_client)]
        orchestrator_state = orchestrator_create_tasks(request.message, agents)
        orchestrator_states_db[conversation.id] = orchestrator_state
        if orchestrator_state.is_completed:
            # Means orchestrator answered the question itself
            return ConversationResponse(
                success=True,
                message="Orchestrator answered the question itself",
                agent_response=orchestrator_state.orchestrator_messages[-1]["content"],
                conversation_id=conversation.id,
                usage={"tokens": None}
            )
        print(f"Orchestrator state: {orchestrator_state}")
        while not orchestrator_state.is_completed:
            orchestrator_state = orchestrator_execute_next_task(orchestrator_state, composio_client)
            print(f"Orchestrator state: {orchestrator_state}")
            
            if orchestrator_state.waiting_for_authentication:
                latest_agent_response = orchestrator_state.messages_by_agent[orchestrator_state.plan[orchestrator_state.next_agent_action_index].agent.uuid][-1]["content"]
                conversation.messages.append(Message(role="assistant", content=latest_agent_response, timestamp=datetime.now(timezone.utc)))
                conversation.updated_at = datetime.now(timezone.utc)
                return ConversationResponse(
                    success=True,
                    message="User needs to authenticate",
                    agent_response=latest_agent_response,
                    conversation_id=conversation.id,
                    usage={"tokens": None}
                )
            
        summary = orchestrator_summarize_execution(orchestrator_state)
            
        # Add agent response to conversation
        agent_message = Message(
            role="assistant",
            content=summary,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(agent_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        # Log the agent response
        # response_log = ActionLog(
        #     id=str(uuid.uuid4()),
        #     agent_id=request.agent_id,
        #     conversation_id=conversation_id,
        #     action="agent_response",
        #     input_data={
        #         "prompt": request.message,
        #         "system_prompt": agent.config.system_prompt
        #     },
        #     output_data={
        #         "response": agent_response_content,
        #         "usage": {"tokens": len(agent_response_content.split())}  # Simplified token count
        #     },
        #     timestamp=datetime.now(timezone.utc),
        #     success=True,
        #     error_message=None
        # )
        # action_logs_db[response_log.id] = response_log
        
        logger.info(f"Processed interaction in conversation {conversation.id}")
        
        return ConversationResponse(
            success=True,
            message="Conversation started successfully",
            agent_response=agent_message.content,
            conversation_id=conversation.id,
            # TODO: Add proper token usage
            usage={"tokens": None}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process interaction: {str(e)}")


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    agent_set_id: Optional[str] = Query(None, description="Filter by agent set ID"),
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of conversations to return")
):
    """
    Retrieve a list of conversations with optional filtering and pagination.
    
    You can filter conversations by agent ID and use pagination parameters
    to control the number of results returned.
    """
    try:
        # Filter conversations by agent_id if provided
        filtered_conversations = list(conversations_db.values())
        if agent_set_id:
            filtered_conversations = [conv for conv in filtered_conversations if conv.agent_set_id == agent_set_id]
        
        # Sort by updated_at descending (most recent first)
        filtered_conversations.sort(key=lambda x: x.updated_at or datetime.min, reverse=True)
        
        # Apply pagination
        total = len(filtered_conversations)
        conversations_page = filtered_conversations[skip:skip + limit]
        
        return ConversationListResponse(
            success=True,
            message=f"Retrieved {len(conversations_page)} conversations",
            conversations=conversations_page,
            total=total
        )
    
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Retrieve a specific conversation by its ID.
    
    Returns the complete conversation including all messages
    and metadata.
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        conversation = conversations_db[conversation_id]
        
        return conversation
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")
        

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation by its ID.
    
    This will permanently remove the conversation and all its messages.
    Associated action logs will be preserved for audit purposes.
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        # Remove conversation
        del conversations_db[conversation_id]
        
        logger.info(f"Deleted conversation {conversation_id}")
        
        return {"success": True, "message": f"Conversation {conversation_id} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
async def send_message(conversation_id: str, request: MessageRequest, composio_client: ComposioClient):
    """
    Send a message to an existing conversation.
    
    This endpoint allows you to continue an existing conversation by sending
    a new message. The agent will process the message in the context of the
    conversation history and return a response.
    """
    supabase_client = get_authenticated_client()
    
    try:
        # Validate conversation exists
        print(conversations_db)
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        conversation = conversations_db[conversation_id]
        orchestrator_state = orchestrator_states_db[conversation_id]
        
        # Clean the user agent messages because they are not needed anymore
        agents = [Agent(**agent) for agent in get_agents_in_set(conversation.agent_set_id, supabase_client)]
        if orchestrator_state.is_completed:
            orchestrator_state = orchestrator_create_tasks(request.message, agents, orchestrator_state.orchestrator_messages)
        else:
            orchestrator_state.orchestrator_messages.append({"role": "user", "content": request.message})
            orchestrator_state = orchestrator_create_tasks(request.message, agents, orchestrator_state.orchestrator_messages)
        # Add user message to conversation
        user_message = Message(
            role="user",
            content=request.message,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(user_message)
        
        print(f"Orchestrator state: {orchestrator_state}")
        while not orchestrator_state.is_completed:
            orchestrator_state = orchestrator_execute_next_task(orchestrator_state, composio_client)
            print(f"Orchestrator state: {orchestrator_state}")
            
            if orchestrator_state.waiting_for_authentication:
                latest_agent_response = orchestrator_state.messages_by_agent[orchestrator_state.plan[orchestrator_state.next_agent_action_index].agent.uuid][-1]["content"]
                conversation.messages.append(Message(role="assistant", content=latest_agent_response, timestamp=datetime.now(timezone.utc)))
                conversation.updated_at = datetime.now(timezone.utc)
                return ConversationResponse(
                    success=True,
                    message="User needs to authenticate",
                    agent_response=latest_agent_response,
                    conversation_id=conversation_id,
                    usage={"tokens": None}
                )
            
        summary = orchestrator_summarize_execution(orchestrator_state)
        
        # Add agent response to conversation
        agent_message = Message(
            role="assistant",
            content=summary,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(agent_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Processed message in conversation {conversation_id}")
        
        return ConversationResponse(
            success=True,
            message="Message sent successfully",
            agent_response=agent_message.content,
            conversation_id=conversation_id,
            # TODO: Add proper token usage
            usage={"tokens": None}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


# @router.get("/agents/{agent_id}/logs")
# async def get_agent_action_logs(
#     agent_id: str,
#     skip: int = Query(0, ge=0, description="Number of logs to skip"),
#     limit: int = Query(50, ge=1, le=1000, description="Number of logs to return"),
#     action: Optional[str] = Query(None, description="Filter by action type")
# ):
#     """
#     Retrieve action logs for a specific agent.
    
#     This endpoint provides access to the agent's action history
#     for context management and debugging purposes.
#     """
#     try:
#         # Validate agent exists
#         if agent_id not in agents_db:
#             raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
#         # Filter logs by agent_id
#         agent_logs = [log for log in action_logs_db.values() if log.agent_id == agent_id]
        
#         # Filter by action if provided
#         if action:
#             agent_logs = [log for log in agent_logs if log.action == action]
        
#         # Sort by timestamp descending (most recent first)
#         agent_logs.sort(key=lambda x: x.timestamp or datetime.min, reverse=True)
        
#         # Apply pagination
#         total = len(agent_logs)
#         logs_page = agent_logs[skip:skip + limit]
        
#         return {
#             "success": True,
#             "message": f"Retrieved {len(logs_page)} action logs",
#             "logs": logs_page,
#             "total": total
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error retrieving logs for agent {agent_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to retrieve agent logs: {str(e)}")


# @router.get("/conversations/{conversation_id}/context")
# async def get_conversation_context(conversation_id: str):
#     """
#     Get conversation context for an agent.
    
#     This endpoint provides the conversation history and context
#     that can be used by the orchestrator to manage agent interactions.
#     """
#     try:
#         if conversation_id not in conversations_db:
#             raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
#         conversation = conversations_db[conversation_id]
        
#         # Get related action logs
#         conversation_logs = [
#             log for log in action_logs_db.values() 
#             if log.conversation_id == conversation_id
#         ]
#         conversation_logs.sort(key=lambda x: x.timestamp or datetime.min)
        
#         # Build context
#         context = {
#             "conversation_id": conversation_id,
#             "agent_id": conversation.agent_id,
#             "message_count": len(conversation.messages),
#             "last_activity": conversation.updated_at,
#             "messages": conversation.messages,
#             "action_logs": conversation_logs,
#             "metadata": conversation.metadata
#         }
        
#         return {
#             "success": True,
#             "message": "Context retrieved successfully",
#             "context": context
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error retrieving context for conversation {conversation_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation context: {str(e)}")
