import json
from collections import defaultdict
from pydantic import BaseModel

from src.services.llm import apertus_llm, openai_llm
from src.services.agent_handlers.user_agent import user_agent_completion
from src.models.agents import Agent
from composio import Composio

def create_orchestrator_system_prompt(available_agents: list[Agent]) -> str:
    return (
        "You are a first point of entry to a network of AI agents.\n"
        "You are responsible for answering the user's question if it's in your ability or planning the tasks to be performed by the agents at your disposal. Execution is not your responsibility, create a plan and output it if needed.\n"
        f"Here are the list of agents available to you: {[{'name': agent.name, 'description': agent.description, 'system_prompt': agent.system_prompt} for agent in available_agents]}\n"
        "Return the response in JSONL format wrapped in ```json ... ``` on the last line. If you are able to answer the query yourself, do not include the JSONL string but only the response. Otherwise, the JSONL string should be a LIST of JSON OBJECTS with the following keys: 'agent_name', 'message'. "
        "For example: [{\"agent_name\": \"notion\", \"message\": \"Create a page with the title: 'My page'\"}, {\"agent_name\": \"gmail\", \"message\": \"Send an email to john.doe@example.com and remind about the meeting tomorrow \"}]\n"
    )


class AgentAction(BaseModel):
    agent: Agent
    task: str

class OrchestratorState(BaseModel):
    orchestrator_messages: list[dict[str, str]]
    messages_by_agent: dict[str, list[dict[str, str]]]
    plan: list[AgentAction]
    next_agent_action_index: int
    waiting_for_authentication: bool
    is_completed: bool

def orchestrator_create_tasks(message: str, available_agents: list[Agent]) -> OrchestratorState:
    system_prompt = create_orchestrator_system_prompt(available_agents)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
    
    response = openai_llm.completion(messages)
    if "```json\n" not in response:
        # Orchestrator answered the question itself
        messages.append({"role": "assistant", "content": response})
        return OrchestratorState(orchestrator_messages=messages, 
                                 messages_by_agent={}, 
                                 plan=[], 
                                 next_agent_action_index=-1, 
                                 waiting_for_authentication=False, 
                                 is_completed=True)

    response_json = response.split("```json\n")[1].removesuffix("\n```")
    if not response_json.startswith("[") and not response_json.endswith("]"):
        # Agent response is not in the correct format, we need to wrap it in []
        response_json = "[" + response_json + "]"
    
    agent_action_dicts = json.loads(response_json)
    agents_by_name = {agent.name: agent for agent in available_agents}
    return OrchestratorState(orchestrator_messages=messages, 
                             messages_by_agent={agent.uuid: [] for agent in available_agents}, 
                             plan=[AgentAction(agent=agents_by_name[action_dict["agent_name"]], task=action_dict["message"]) for action_dict in agent_action_dicts], 
                             next_agent_action_index=0, 
                             waiting_for_authentication=False, 
                             is_completed=False)

def orchestrator_execute_next_task(state: OrchestratorState, composio_client: Composio) -> OrchestratorState:
    if state.is_completed:
        return state
    
    agent_action = state.plan[state.next_agent_action_index]
    if state.waiting_for_authentication:
        # If it was executed again, we assume that the authentication is completed
        state.waiting_for_authentication = False
        state.messages_by_agent[agent_action.agent.uuid].append({"role": "assistant", "content": "Authentication completed, please execute the task."})
    else:
        state.messages_by_agent[agent_action.agent.uuid].append({"role": "user", "content": agent_action.task})
        
    agent_response, needs_authentication = user_agent_completion(state.messages_by_agent[agent_action.agent.uuid], composio_client, agent_action.agent.tools)
    state.messages_by_agent[agent_action.agent.uuid].append({"role": "assistant", "content": agent_response})
    if needs_authentication:
        state.waiting_for_authentication = True
        # We need to wait for the authentication to complete before we can execute the next task
        return state

    # Task is completed, we need to move to the next task
    state.next_agent_action_index += 1
    
    # If we have executed all tasks, we mark the orchestrator as completed
    if state.next_agent_action_index == len(state.plan):
        state.is_completed = True

    return state

def create_summary_prompt() -> str:
    return (
        "You are an orchestrator for AI agents.\n"
        "You are responsible for analyzing and summarizing the execution of the network of agents according to the plan.\n"
        "You will be given the messages from the orchestrator, the messages from the agents, and the plan.\n"
        "Return the response in JSONL format wrapped in ```json ... ``` on the last line. The response should be a JSON OBJECT with the following keys: 'summary'."
        "For example: {\"summary\": \"The orchestrator executed the plan successfully.\"}"
    )

def orchestrator_summarize_execution(state: OrchestratorState) -> str:
    system_prompt = create_summary_prompt()
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here are the list of messages from the orchestrator: {state.orchestrator_messages}\n"
        f"Here are the list of messages from the agents: {state.messages_by_agent}\n"
        f"Here is the plan: {state.plan}\n"
        "Summarize the execution of the network of agents according to the plan."}]
    response = openai_llm.completion(messages)
    response_json = response.split("```json\n")[1].removesuffix("\n```")
    return json.loads(response_json)["summary"]
    