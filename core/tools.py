import inspect
from functools import wraps
import logging

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name, description):
        def decorator(func):
            sig = inspect.signature(func)
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }

            for param_name, param in sig.parameters.items():
                if param_name == 'self': continue

                # Infer type
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"

                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }

                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

            tool_def = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            }

            self.tools[name] = {
                "func": func,
                "schema": tool_def
            }

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def get_tools_schema(self):
        schemas = [t["schema"] for t in self.tools.values()]
        return schemas if schemas else None

    async def execute(self, tool_name, tool_args):
        if tool_name in self.tools:
            func = self.tools[tool_name]["func"]
            try:
                self.logger.info(f"Executing tool {tool_name} with args {tool_args}")
                if inspect.iscoroutinefunction(func):
                    return await func(**tool_args)
                else:
                    return func(**tool_args)
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_name}: {e}")
                return f"Error executing tool: {e}"
        return f"Tool {tool_name} not found."

registry = ToolRegistry()
