import asyncio
import logging
import os
import importlib
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from contextvars import ContextVar
import telegramify_markdown

import config
from core.agent import Agent
from core.scheduler import scheduler, set_bot
from core.context import current_user_id, current_chat_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Agent storage
agents = {}

def get_agent(user_id):
    if user_id not in agents:
        agents[user_id] = Agent()
    return agents[user_id]

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello! I am Garvis, your advanced AI assistant. How can I help you today?")

@dp.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Set context variables
    token_user = current_user_id.set(user_id)
    token_chat = current_chat_id.set(chat_id)

    try:
        agent = get_agent(user_id)

        # Notify user that processing is happening
        await bot.send_chat_action(chat_id=chat_id, action="typing")

        response = await agent.process_message(message.text, user_id=user_id)

        # Format and send response
        if response:
            try:
                # telegramify is async in newer versions but might be sync in some.
                # In 0.5.4, telegramify is async.
                # However, let's verify if we need to await it.
                # My previous test showed it is a coroutine.
                # But to be safe, we check if it is awaitable.

                result = telegramify_markdown.telegramify(response)
                if asyncio.iscoroutine(result):
                    formatted_chunks = await result
                else:
                    formatted_chunks = result

                for chunk in formatted_chunks:
                    await message.answer(chunk.content, parse_mode="MarkdownV2")
            except Exception as e:
                logger.error(f"Failed to send formatted message: {e}")
                # Fallback to plain text splitting
                if len(response) > 4000:
                    for x in range(0, len(response), 4000):
                        await message.answer(response[x:x+4000])
                else:
                    await message.answer(response)
        else:
            await message.answer("I processed your request but have no response.")

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.answer(f"An error occurred: {str(e)}")
    finally:
        current_user_id.reset(token_user)
        current_chat_id.reset(token_chat)

async def on_startup():
    logger.info("Starting bot...")

    if config.ADMIN_ID == 0:
        logger.warning("ADMIN_ID is not set in .env. Admin tools (shell, module generator) will be disabled.")

    # Set bot instance for scheduler
    set_bot(bot)
    scheduler.start()

    # Load modules
    modules_path = os.path.join(os.path.dirname(__file__), "modules")
    for filename in os.listdir(modules_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                importlib.import_module(f"modules.{module_name}")
                logger.info(f"Loaded module: {module_name}")

                # Check for init function
                module = sys.modules.get(f"modules.{module_name}")
                if module and hasattr(module, "init"):
                    if asyncio.iscoroutinefunction(module.init):
                        await module.init()
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {e}")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Add project root to path if needed
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
