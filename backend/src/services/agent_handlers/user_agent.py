from composio.core.models import Tools

from src.services.llm import apertus_llm, openai_llm

from composio import Composio

user_id = "session_id"



# def create_system_prompt_for_user_agent(orchestrator_message: str) -> str:
def create_system_prompt_for_user_agent() -> str:
    return (
        "You are a user agent. You are responible for executing tasks assigned by orchestrator using tools at your disposal."
        # f"Here is the orchestrator's message: {orchestrator_message}"
        "Return the response in JSONL format wrapped in ```json ... ``` on the last line. The response should be a map with the following keys: 'result'."
        "For example: {\"result\": \"Here is the weather for Zurich for tomorrow\"}"
    )

def user_agent_completion(orchestrator_message: str, composio_client: Composio, tools: list[str], transcript: list[dict[str, str]] | None = None) -> tuple[str, bool]:
    """
    Returns a tuple with the response and a boolean indicating if the user needs to authenticate.
    """
    toolkits_to_fetch = []
    authentication_urls = []
    for tool in tools:
        if needs_authentication(composio_client=composio_client, user_id=user_id, toolkit_slug=tool):
            connection_request = composio_client.toolkits.authorize(user_id=user_id, toolkit=tool)
            authentication_urls.append(connection_request.redirect_url)
        else:
            toolkits_to_fetch.append(tool)

    if len(authentication_urls) > 0:
        return "The user needs to authenticate, redirect them here:\n- " + "\n- ".join(authentication_urls), True

    tools = composio_client.tools.get(user_id=user_id, toolkits=toolkits_to_fetch)

    system_prompt = create_system_prompt_for_user_agent()
    response = apertus_llm.completion(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": orchestrator_message}], tools=tools)
    result = composio_client.provider.handle_tool_calls(user_id=user_id, response=response)
    return result, False


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
