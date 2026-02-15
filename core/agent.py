import json
import logging
from core.llm import LLMClient
from core.tools import registry

class Agent:
    def __init__(self, provider=None, system_prompt=None):
        self.llm = LLMClient(provider) if provider else LLMClient()
        self.system_prompt = system_prompt or "You are Garvis, a helpful and powerful AI assistant."
        self.history = [{"role": "system", "content": self.system_prompt}]
        self.logger = logging.getLogger(__name__)

    async def process_message(self, user_message, user_id=None):
        self.history.append({"role": "user", "content": user_message})

        # Limit history size to avoid context limit
        if len(self.history) > 20:
             # Keep system prompt and last 19 messages
             self.history = [self.history[0]] + self.history[-19:]

        tools_schema = registry.get_tools_schema()

        try:
            response_message = await self.llm.chat_completion(self.history, tools=tools_schema)

            # Convert to dict for history using model_dump() (Pydantic)
            response_dict = response_message.model_dump()

            # Ensure tool_calls are kept if present
            if not response_dict.get('content'):
                response_dict['content'] = "" # Ensure content is at least empty string if None

            self.history.append(response_dict)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                         func_args = {}

                    tool_result = await registry.execute(func_name, func_args)

                    self.history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": str(tool_result)
                    })

                # Get final response
                final_response = await self.llm.chat_completion(self.history)
                final_response_dict = final_response.model_dump()
                if not final_response_dict.get('content'):
                    final_response_dict['content'] = ""
                self.history.append(final_response_dict)
                return final_response.content

            return response_message.content

        except Exception as e:
            self.logger.error(f"Error in agent process: {e}")
            return f"An error occurred: {str(e)}"

    def clear_history(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
