import config
from openai import AsyncOpenAI
import logging

class LLMClient:
    def __init__(self, provider=config.DEFAULT_MODEL_PROVIDER):
        self.provider = provider
        self.client = self._get_client()
        self.model = self._get_model_name()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _get_client(self):
        if self.provider == "deepseek":
            return AsyncOpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
        elif self.provider == "groq":
            return AsyncOpenAI(
                api_key=config.GROQ_API_KEY,
                base_url=config.GROQ_BASE_URL
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _get_model_name(self):
        if self.provider == "deepseek":
            return "deepseek-chat"
        elif self.provider == "groq":
            return "llama3-70b-8192"
        return "deepseek-chat"

    async def chat_completion(self, messages, tools=None):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            raise e
