from core.tools import registry
from core.llm import LLMClient
from core.context import current_user_id
import config
import logging
import os
import importlib

logger = logging.getLogger(__name__)

@registry.register(name="generate_module", description="Generate a new module/skill for the bot.")
async def generate_module(description: str, module_name: str):
    if current_user_id.get() != config.ADMIN_ID:
        return "Permission denied: This tool is restricted to admin only."
    """
    Generate a new module.

    Args:
        description: Description of what the module should do.
        module_name: The name of the file (without .py extension).
    """
    logger.info(f"Generating module {module_name}...")

    prompt = f"""
    You are an expert Python developer. Create a Python module file for a bot.
    The module must use the `core.tools` registry to register tools.

    Requirements:
    - Import `registry` from `core.tools`.
    - Use `@registry.register(name="tool_name", description="Tool description")` decorator.
    - The functions should be async.
    - Implement the logic described below.
    - Use `logging` if needed.
    - Do not include markdown formatting (like ```python ... ```), just raw code.

    Description:
    {description}
    """

    try:
        llm = LLMClient()
        messages = [{"role": "user", "content": prompt}]
        response = await llm.chat_completion(messages)
        code = response.content

        # Clean up code
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        filepath = os.path.join("modules", f"{module_name}.py")
        if os.path.exists(filepath):
            return f"Module {module_name} already exists."

        with open(filepath, "w") as f:
            f.write(code.strip())

        # Try to load it?
        try:
             importlib.import_module(f"modules.{module_name}")
             return f"Module {module_name} generated and loaded successfully."
        except Exception as e:
             return f"Module generated at {filepath}, but failed to load: {e}"

    except Exception as e:
        return f"Failed to generate module: {e}"
