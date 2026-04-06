"""
SQLite Memory Store

Handles persistent conversation memory for the LangGraph agent
using SqliteSaver.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import os
import sqlite3
from typing import List
from langgraph.checkpoint.sqlite import SqliteSaver
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ================================
# Database Setup
# ================================

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")

os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

logger.info(f"SQLite memory initialized | db={DB_PATH}")


# ================================
# Thread Utilities
# ================================

def retrieve_all_threads() -> List[str]:
    """
    Retrieve all stored conversation thread IDs.

    Returns
    -------
    List[str]get_thread_title_db
        List of thread IDs.
    """

    logger.info("Retrieving all conversation threads")

    try:

      cursor = conn.cursor()
      cursor.execute("SELECT thread_id FROM threads ORDER BY created_at DESC")
      rows = cursor.fetchall()

      return [row[0] for row in rows]

    except Exception as e:

        logger.error(f"Failed to retrieve threads: {str(e)}")

        return []


def thread_exists(thread_id: str) -> bool:
    """
    Check if a thread exists in memory.
    """

    try:

        for checkpoint in checkpointer.list(None):

            if checkpoint.config.get("configurable", {}).get("thread_id") == thread_id:
                return True

        return False

    except Exception as e:

        logger.error(f"Thread existence check failed: {str(e)}")

        return False

def init_thread_table():
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        thread_id TEXT PRIMARY KEY,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()


init_thread_table()



def get_thread_title_db(thread_id: str) -> str:
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT title FROM threads WHERE thread_id=?
        """, (thread_id,))

        row = cursor.fetchone()

        if row and row[0]:
            return row[0]

        return f"Chat {thread_id[:6]}"

    except Exception as e:
        logger.error(f"Failed to get thread title: {str(e)}")
        return f"Chat {thread_id[:6]}"


def save_thread_title(thread_id: str, title: str):
    try:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO threads (thread_id, title)
        VALUES (?, ?)
        ON CONFLICT(thread_id)
        DO UPDATE SET title=excluded.title
        """, (thread_id, title))

        conn.commit()

    except Exception as e:
        logger.error(f"Failed to save thread title: {str(e)}")