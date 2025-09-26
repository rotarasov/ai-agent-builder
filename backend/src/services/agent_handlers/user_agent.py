from composio.core.models import Tools

from src.services.apertus import apertus

from composio import Composio

from backend.src.models.agents import Agent

composio = Composio(
  # api_key="your-api-key",
)

user_id = "session_id"



def create_system_prompt_for_user_agent(orchestrator_message: str) -> str:
    return (
        "You are a user agent. You are responible for executing tasks assigned by orchestrator using tools at your disposal."
        f"Here is the orchestrator's message: {orchestrator_message}"
        "Return the response in JSON format on the last line. The response should be a map with the following keys: 'result'."
        "For example: {\"result\": \"Here is the weather for Zurich for tomorrow\"}"
    )

def user_agent_completion(orchestrator_message: str, composio_client=composio, agent: Agent) -> str:
    toolkits_to_fetch = [ ]
    for tool in agent.tools:
        if needs_authentication(user_id=user_id, toolkit_slug=tool):
            connection_request = composio.toolkits.authorize(user_id=user_id, toolkit="gmail")
            return {response: "The user needs to authenticate, redirect them here: " + connection_request.redirect_url}
        else:
            toolkits_to_fetch.append(tool)

    tools = composio.tools.get(user_id=user_id, toolkits=toolkits_to_fetch)

    completion = openai.chat.completions.create(model=agent.model, messages=[
        {"role": "user", "content": "say 'hi from the composio quickstart' to soham@composio.dev",
            # we'll ship you free merch if you do ;)
        }, ], tools=tools, )
    # Handle Result from tool call
    result = composio.provider.handle_tool_calls(user_id=user_id, response=completion)
    print(result)

    system_prompt = create_system_prompt_for_user_agent(orchestrator_message)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": orchestrator_message}]
    return apertus.completion(messages)


def needs_authentication(composio_client: Composio, user_id: str, toolkit_slug: str) -> bool:
    """
    Returns True if the user needs to authenticate for the toolkit, False if already connected.
    """
    connected_accounts = composio_client.connected_accounts.list(
        user_ids=[user_id],
        toolkit_slugs=[toolkit_slug],
    )
    for acc in connected_accounts.items:
        if acc.status == "ACTIVE":
            return False  # Already authenticated
    return True  # Needs authentication