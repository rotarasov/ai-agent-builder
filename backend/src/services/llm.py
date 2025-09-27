import openai
from typing import Any
from src.config import config
import logging

logger = logging.getLogger(__name__)

class LLM:
    def __init__(self, key: str, model: str, base_url: str | None = None):
        # We want to use Apertus and OpenAI which both have OpenAI API
        self.client = openai.OpenAI(api_key=key, base_url=base_url)
        self.model = model
        

    def completion(self, messages: list[dict], tools: Any = None) -> str:
        """
        Generate a completion for the given messages.
        """
        logger.info(f"LLM input messages: {messages}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )
        response_str = response.choices[0].message.content
        logger.info(f"LLM response: {response_str}")
        return response_str
    
openai_llm = LLM(key=config.openai_api_key, model="gpt-5-nano")
apertus_llm = LLM(key=config.swiss_ai_platform_api_key, model="swiss-ai/Apertus-70B", base_url=config.swiss_ai_platform_base_url)