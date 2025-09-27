from composio.core.models import Tools

from src.services.llm import LLM, openai_llm

from composio import Composio


# def create_system_prompt_for_user_agent(orchestrator_message: str) -> str:
def create_system_prompt_for_user_agent() -> str:
    return (
        "You are a user agent. You are responible for executing tasks assigned by orchestrator using tools at your disposal."
        # f"Here is the orchestrator's message: {orchestrator_message}"
        "Return the response in JSONL format wrapped in ```json ... ``` on the last line. The response should be a map with the following keys: 'result'."
        "For example: {\"result\": \"Here is the weather for Zurich for tomorrow\"}"
    )

def user_agent_completion(user_id: str, orchestrator_message: str, composio_client: Composio, tools: list[str], llm: LLM = openai_llm, transcript: list[dict[str, str]] | None = None) -> tuple[list[dict[str, str]], bool]:
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

    system_prompt = create_system_prompt_for_user_agent()
    agent_messages = (transcript or [{"role": "system", "content": system_prompt}])

    if len(authentication_urls) > 0:
        agent_messages.append({"role": "assistant", "content": "The user needs to authenticate, redirect them here:\n- " + "\n- ".join(authentication_urls)})
        return agent_messages, True

    tools = composio_client.tools.get(user_id=user_id, toolkits=toolkits_to_fetch)

    print(tools)

    agent_messages = agent_messages + [{"role": "user", "content": orchestrator_message}]
    response = llm.completion_raw(messages=agent_messages, tools=tools)
    print("Agent response in useragent.py: ", response)
    result = composio_client.provider.handle_tool_calls(user_id=user_id, response=response)
    print("tool call result:", result)

    agent_messages.append({"role": "assistant", "content": result})
    return agent_messages, False


def needs_authentication(composio_client: Composio, user_id: str, toolkit_slug: str) -> bool:
    """
    Returns True if the user needs to authenticate for the toolkit, False if already connected.
    """
    existing_configs = composio_client.auth_configs.list(toolkit_slug=toolkit_slug)
    print("Existing configs searched: ", existing_configs)

    if len(existing_configs.items) < 1:
        print("trying to create new config")
        composio_client.auth_configs.create(toolkit=toolkit_slug, options={"type": "use_composio_managed_auth"})
        print("new config created")



    connected_accounts = composio_client.connected_accounts.list(
        user_ids=[user_id],
        toolkit_slugs=[toolkit_slug],
    )
    for acc in connected_accounts.items:
        if acc.status == "ACTIVE":
            return False  # Already authenticated
    return True  # Needs authentication
