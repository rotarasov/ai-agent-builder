from composio import Composio
from composio_openai import OpenAIProvider
from fastapi import Depends
import typing_extensions as te

from src.config import config

_composio_client: Composio[OpenAIProvider] | None = None

def provide_composio_client():
    """
    Provide a Composio client.
    """
    global _composio_client
    if _composio_client is None:
        _composio_client = Composio(provider=OpenAIProvider(), api_key=config.composio_api_key)
    return _composio_client

ComposioClient = te.Annotated[Composio, Depends(provide_composio_client)]