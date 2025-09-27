import json
from collections import defaultdict
from pydantic import BaseModel

from src.services.llm import apertus_llm, openai_llm
from src.services.agent_handlers.user_agent import user_agent_completion
from src.models.agents import Agent
from composio import Composio

def create_orchestrator_system_prompt(available_agents: list[Agent]) -> str:
    return (
        "You are a coordinator AI that serves as the first point of entry to a network of specialized AI agents. Your role is to either answer the user's question directly if it's within your general capabilities, or create a plan for other agents to execute.\n\n"
        "Here are the agents available to you:\n"
        "<available_agents>\n"
        f"{[{'name': agent.name, 'description': agent.description, 'system_prompt': agent.system_prompt} for agent in available_agents]}\n"
        "</available_agents>\n\n"
        "Your responsibilities:\n"
        "- If the user's question is a general knowledge question, simple conversation, or something you can answer without needing specialized tools or actions, answer it directly\n"
        "- If the user's question requires specific actions, tool usage, or specialized capabilities that the available agents can provide, create a plan by assigning tasks to the appropriate agents\n"
        "- Do NOT attempt to execute tasks yourself - only plan them\n\n"
        "Before responding, use the scratchpad below to think through your approach:\n\n"
        "<scratchpad>\n"
        "Consider:\n"
        "1. Can I answer this query directly with general knowledge/conversation?\n"
        "2. Does this require specific actions or specialized capabilities?\n"
        "3. If planning is needed, which agents are most suitable for each part of the task?\n"
        "4. What is the logical sequence of tasks?\n"
        "</scratchpad>\n\n"
        "Output format rules:\n"
        "- If you can answer the query yourself: Provide your response directly without any JSONL formatting\n"
        "- If you need to create a plan: End your response with a JSONL array wrapped in ```json ... ``` tags\n\n"
        "The JSONL format should be a list of JSON objects, each containing:\n"
        "- \"agent_name\": The exact name of the agent to use\n"
        "- \"message\": Clear instructions for what that agent should do\n\n"
        "Example of proper JSONL formatting:\n"
        "```json\n"
        "[{\"agent_name\": \"notion\", \"message\": \"Create a page with the title: 'My page'\"}, {\"agent_name\": \"gmail\", \"message\": \"Send an email to john.doe@example.com and remind about the meeting tomorrow\"}]\n"
        "```\n\n"
        "Make sure each JSON object is properly formatted with double quotes around keys and string values."
    )


class AgentAction(BaseModel):
    agent: Agent
    task: str

class OrchestratorState(BaseModel):
    conversation_id: str
    orchestrator_messages: list[dict[str, str]]
    messages_by_agent: dict[str, list[dict[str, str]]]
    plan: list[AgentAction]
    next_agent_action_index: int
    waiting_for_authentication: bool
    is_completed: bool

def orchestrator_create_tasks(message: str, available_agents: list[Agent], conversation_id: str, transcript: list[dict[str, str]] | None = None) -> OrchestratorState:
    system_prompt = create_orchestrator_system_prompt(available_agents)
    messages = (transcript or [{"role": "system", "content": system_prompt}]) + [{"role": "user", "content": message}]
    
    response = openai_llm.completion(messages)
    if "```json\n" not in response:
        # Orchestrator answered the question itself
        messages.append({"role": "assistant", "content": response})
        return OrchestratorState(conversation_id=conversation_id, orchestrator_messages=messages, 
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
    return OrchestratorState(conversation_id=conversation_id, orchestrator_messages=messages, 
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
        
    llm = apertus_llm if agent_action.agent.model_name == "swiss-ai/Apertus-70B" else openai_llm
    agent_messages, needs_authentication = user_agent_completion(state.conversation_id, agent_action.task, composio_client, agent_action.agent.tools, llm, state.messages_by_agent[agent_action.agent.uuid])
    agent_response = agent_messages[-1]["content"]
    state.messages_by_agent[agent_action.agent.uuid] = agent_messages
    state.orchestrator_messages.append({"role": "assistant", "content": agent_response})
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
        "You are an AI assistant that helps summarize the results of automated tasks and workflows. You will review the conversation history and task details to provide a clear, user-friendly response to the user query in which you summarize what was accomplished.\n\n"
        "Your task is to:\n"
        "1. Review what tasks were requested and how they were handled\n"
        "2. Summarize the key results and outcomes from the automated processes\n"
        "3. Highlight any important details about what was completed\n"
        "4. Note whether all requested tasks were completed successfully or if there were any issues\n\n"
        "Before providing your final response, use the scratchpad below to organize your thoughts:\n\n"
        "<scratchpad>\n"
        "Think through:\n"
        "- What was the user trying to accomplish?\n"
        "- How were the tasks coordinated and executed?\n"
        "- What were the key results from each step?\n"
        "- Were there any problems or incomplete tasks?\n"
        "- What was the overall outcome for the user?\n"
        "</scratchpad>\n\n"
        "Provide your response in JSONL format wrapped in json ... tags. The response must be a single JSON object with a 'summary' key that contains a comprehensive summary of the results.\n\n"
        "For example:\n"
        "```json\n"
        "{\"summary\": \"Your request was completed successfully. The system handled task A and produced result X, while also completing task B with outcome Y. All requested objectives were met.\"}\n"
        "```\n\n"
        "Your summary should be detailed and include specific results and outcomes from the automated processes."
    )

def orchestrator_summarize_execution(state: OrchestratorState) -> str:
    system_prompt = create_summary_prompt()
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here are the list of messages from the orchestrator\n<orchestrator_messages>\n{state.orchestrator_messages}\n</orchestrator_messages>\n"
        f"Here are the list of messages from the agents\n<agent_messages>\n{state.messages_by_agent}\n</agent_messages>\n"
        f"Here is the plan\n<plan>\n{state.plan}\n</plan>\n"
        "Summarize the execution of the network of agents according to the plan."}]
    response = openai_llm.completion(messages)
    response_json = response.split("```json\n")[1].removesuffix("\n```")
    return json.loads(response_json)["summary"]
    