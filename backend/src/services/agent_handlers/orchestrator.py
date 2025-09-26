import json
from pydantic import BaseModel

from src.services.apertus import apertus


class AgentDescriptionForOrchestrator(BaseModel):
    name: str
    description: str
    system_prompt: str


class AgentAction(BaseModel):
    agent_name: str
    message: str

def create_orchestrator_system_prompt(available_agents: list[AgentDescriptionForOrchestrator]) -> str:
    return (
        "You are an orchestrator for AI agents.\n"
        "You are responsible for planning the flow of the conversation and the tasks to be performed by the agents.\n"
        f"Here are the list of agents available to you: {[agent.model_dump_json() for agent in available_agents]}\n"
        "Return the response in JSON format on the last line. The response should be a list of maps with the following keys: 'agent_name', 'message'."
        "For example: [{\"agent_name\": \"notion\", \"message\": \"Create a page with the title: 'My page'\"}, {\"agent_name\": \"gmail\", \"message\": \"Send an email to john.doe@example.com and remind about the meeting tomorrow \"}]"
    )

def orchestrator_completion(message: str, available_agents: list[AgentDescriptionForOrchestrator]) -> str:
    system_prompt = create_orchestrator_system_prompt(available_agents)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
    return apertus.completion(messages)

def parse_orchestrator_response(response: str) -> list[AgentAction]:
    agent_actions = json.loads(response.split("\n")[-1])
    return [AgentAction(**action_dict) for action_dict in agent_actions]
    