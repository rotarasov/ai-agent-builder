import openai

from src.config import config

class Apertus:
    def __init__(self):
        # Apertus API is the same as OpenAI API
        self.client = openai.OpenAI(api_key=config.swiss_ai_platform_api_key, 
                                    base_url=config.swiss_ai_platform_base_url)
        

    def completion(self, messages: list[dict], model: str = "swiss-ai/Apertus-70B") -> str:
        """
        Generate a completion for the given messages.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
    
apertus = Apertus()