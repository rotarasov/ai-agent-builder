import supabase

from src.models.agents import Agent, AgentSetSupabase
from src.config import config


def get_authenticated_client() -> supabase.Client:
    client = supabase.create_client(config.supabase_url, config.supabase_key)
    client.auth.sign_in_with_password(
        {
            "email": config.supabase_user,
            "password": config.supabase_password,
        }
    )

    return client


def create_agent_set(
    agent_set: AgentSetSupabase, supabase_client: supabase.Client
) -> tuple[bool, str]:
    agent_set_dump = agent_set.model_dump()

    response = (
        supabase_client.table(config.agents_set_table_name).insert(agent_set_dump).execute()
    )

    if response.data is not None:
        return (True, response.data[0]["uuid"])

    return (False, "")


def create_agent(agent: Agent, supabase_client: supabase.Client) -> tuple[bool, str]:
    """Save agent to supabase. Return True on success, False otherwise."""

    agent_dump = agent.model_dump()

    response = (
        supabase_client.table(config.agents_table_name).insert(agent_dump).execute()
    )

    if response.data is not None:
        return (True, response.data[0]["uuid"])

    return (False, "")


def get_agents_in_set(agent_set_id: str, supabase_client: supabase.Client):

    response = (
        supabase_client.table(config.agents_table_name)
        .select("*")
        .eq("agent_set", agent_set_id)
        .execute()
    )

    return response.data


def get_agent_set(supabase_client: supabase.Client):

    response = supabase_client.table(config.agents_set_table_name).select("*").execute()

    return response.data


def get_agent_set_by_id(agent_set_id: str, supabase_client: supabase.Client):

    response = (
        supabase_client.table(config.agents_set_table_name)
        .select("*")
        .eq("uuid", agent_set_id)
        .execute()
    )

    return response.data
