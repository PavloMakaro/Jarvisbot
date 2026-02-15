from core.tools import registry
from core.context import current_user_id
import aiosqlite
import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def init():
    """Initialize database table."""
    try:
        async with aiosqlite.connect(config.DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to init diary db: {e}")

@registry.register(name="add_diary_entry", description="Add a new entry to the user's diary.")
async def add_diary_entry(content: str):
    """
    Add a diary entry.

    Args:
        content: The text content of the entry.
    """
    user_id = current_user_id.get()
    if not user_id:
        return "Error: User context missing."

    try:
        # Ensure table exists (lazy init fallback)
        await init()

        async with aiosqlite.connect(config.DB_FILE) as db:
            await db.execute("INSERT INTO diary_entries (user_id, content) VALUES (?, ?)", (user_id, content))
            await db.commit()
        return "Diary entry added."
    except Exception as e:
        logger.error(f"Failed to add diary entry: {e}")
        return f"Failed to add entry: {e}"

@registry.register(name="read_diary", description="Read diary entries.")
async def read_diary(date: str = None, limit: int = 5):
    """
    Read diary entries.

    Args:
        date: Optional date filter (YYYY-MM-DD).
        limit: Max number of entries to return (default 5).
    """
    user_id = current_user_id.get()
    if not user_id:
        return "Error: User context missing."

    try:
        # Ensure table exists
        await init()

        async with aiosqlite.connect(config.DB_FILE) as db:
            if date:
                # Filter by date
                query = "SELECT created_at, content FROM diary_entries WHERE user_id = ? AND date(created_at) = ? ORDER BY created_at DESC LIMIT ?"
                cursor = await db.execute(query, (user_id, date, limit))
            else:
                query = "SELECT created_at, content FROM diary_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
                cursor = await db.execute(query, (user_id, limit))

            rows = await cursor.fetchall()
            if not rows:
                return "No entries found."

            entries = []
            for row in rows:
                entries.append(f"[{row[0]}] {row[1]}")

            return "\n\n".join(entries)
    except Exception as e:
        logger.error(f"Failed to read diary: {e}")
        return f"Failed to read diary: {e}"
