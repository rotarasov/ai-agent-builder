from composio.core.models import Tools

from src.services.apertus import apertus


def create_system_prompt_for_user_agent(orchestrator_message: str, tools: list[str]) -> str:
    # TODO: Need to add tools to 
    return (
        "You are a user agent. You are responible for executing tasks assigned by orchestrator using tools at your disposal."
        f"Here is the orchestrator's message: {orchestrator_message}"
        "Return the response in JSON format on the last line. The response should be a map with the following keys: 'result'."
        "For example: {\"result\": \"Here is the weather for Zurich for tomorrow\"}"
    )

def user_agent_completion(orchestrator_message: str) -> str:
    system_prompt = create_system_prompt_for_user_agent(orchestrator_message)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": orchestrator_message}]
    return apertus.completion(messages)