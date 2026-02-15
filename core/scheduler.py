from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import config
import logging

logger = logging.getLogger(__name__)

jobstores = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///{config.DB_FILE}')
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

_bot_instance = None

def set_bot(bot):
    global _bot_instance
    _bot_instance = bot
    logger.info("Bot instance set in scheduler.")

def get_bot():
    return _bot_instance
