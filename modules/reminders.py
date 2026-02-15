from core.tools import registry
from core.scheduler import scheduler, get_bot
from core.context import current_chat_id
import logging
from datetime import datetime, timedelta
import dateutil.parser

logger = logging.getLogger(__name__)

async def send_reminder(chat_id, message):
    bot = get_bot()
    if bot:
        try:
            await bot.send_message(chat_id=chat_id, text=f"🔔 Reminder: {message}")
        except Exception as e:
            logger.error(f"Failed to send reminder to {chat_id}: {e}")
    else:
        logger.error("Bot instance not found for reminder.")

@registry.register(name="set_reminder", description="Set a reminder for a specific time.")
async def set_reminder(message: str, time_str: str):
    """
    Set a reminder.

    Args:
        message: The reminder message.
        time_str: The time for the reminder (ISO format "YYYY-MM-DD HH:MM:SS" or "in X minutes/hours").
    """
    chat_id = current_chat_id.get()
    if not chat_id:
        return "Error: Chat context missing."

    run_date = None
    now = datetime.now()
    try:
        if time_str.lower().startswith("in "):
            # Relative time
            parts = time_str[3:].split()
            amount = float(parts[0])
            unit = parts[1].lower()
            if "minute" in unit:
                run_date = now + timedelta(minutes=amount)
            elif "hour" in unit:
                run_date = now + timedelta(hours=amount)
            elif "second" in unit:
                run_date = now + timedelta(seconds=amount)
            elif "day" in unit:
                run_date = now + timedelta(days=amount)
        else:
            # Absolute time
            run_date = dateutil.parser.parse(time_str)
            if run_date.tzinfo is not None:
                # Convert to naive local
                run_date = run_date.replace(tzinfo=None)
    except Exception as e:
        return f"Invalid time format: {e}. Use ISO format or 'in X minutes'."

    if not run_date:
        return "Could not parse time."

    if run_date < now:
        return "Time is in the past."

    scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[chat_id, message])
    return f"Reminder set for {run_date.strftime('%Y-%m-%d %H:%M:%S')}."
