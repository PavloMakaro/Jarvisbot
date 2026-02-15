from core.tools import registry
from core.context import current_user_id
import config
import asyncio
import sys
import io
import contextlib
import logging

logger = logging.getLogger(__name__)

@registry.register(name="execute_python", description="Execute Python code. Use with caution.")
async def execute_python(code: str):
    if current_user_id.get() != config.ADMIN_ID:
        return "Permission denied: This tool is restricted to admin only."

    """
    Execute Python code and return the output.

    Args:
        code: The Python code to execute.
    """
    logger.info("Executing Python code...")

    # Create a string buffer to capture output
    str_output = io.StringIO()

    try:
        # Redirect stdout and stderr
        with contextlib.redirect_stdout(str_output), contextlib.redirect_stderr(str_output):
            # execute in a limited scope?
            # We want it to be powerful as requested ("Open Code"), so we don't restrict much.
            # But we should run it in a way that async code might not work well with exec() unless we handle it.
            # exec() is synchronous. If the code has async/await, it won't work directly without an event loop.
            # For now, we assume synchronous code snippets.

            exec_globals = {"print": print, "__builtins__": __builtins__}
            exec(code, exec_globals)

        output = str_output.getvalue()
        if not output:
            output = "Code executed successfully (no output)."
        return output
    except Exception as e:
        return f"Error executing code: {e}"

@registry.register(name="execute_shell", description="Execute a shell command. Use with caution.")
async def execute_shell(command: str):
    """
    Execute a shell command.

    Args:
        command: The shell command to execute.
    """
    if current_user_id.get() != config.ADMIN_ID:
        return "Permission denied: This tool is restricted to admin only."

    logger.info(f"Executing shell command: {command}")
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Timeout safety?
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        except asyncio.TimeoutError:
            process.kill()
            return "Command timed out."

        output = ""
        if stdout:
            output += f"STDOUT:\n{stdout.decode().strip()}\n"
        if stderr:
            output += f"STDERR:\n{stderr.decode().strip()}\n"

        if not output:
            output = "Command executed successfully (no output)."

        return output
    except Exception as e:
        return f"Error executing command: {e}"
