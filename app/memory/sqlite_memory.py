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


def init_db():
    cursor = conn.cursor()

    # THREADS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        thread_id TEXT PRIMARY KEY,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 🔥 DOCUMENTS TABLE (MISSING)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        type TEXT,
        content_hash TEXT UNIQUE,
        source TEXT,
        vectorstore_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 🔥 RELATION TABLE (MISSING)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_documents (
        thread_id TEXT,
        doc_id TEXT,
        PRIMARY KEY (thread_id, doc_id)
    )
    """)

    conn.commit()


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


def init_thread_context_table():
    cursor=conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_context (
        thread_id TEXT PRIMARY KEY,
        youtube_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(thread_id) REFERENCES threads(thread_id)
    )
    """)

    conn.commit()

init_thread_context_table()


def save_youtube_url(thread_id: str, youtube_url: str):
    try:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO thread_context (thread_id, youtube_url)
        VALUES (?, ?)
        ON CONFLICT(thread_id)
        DO UPDATE SET youtube_url=excluded.youtube_url
        """, (thread_id, youtube_url))

        conn.commit()

        logger.info(f"YouTube URL saved | thread={thread_id}")

    except Exception as e:
        logger.error(f"Failed to save YouTube URL: {str(e)}")

    
def get_youtube_url(thread_id: str) -> str:
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT youtube_url FROM thread_context WHERE thread_id=?
        """, (thread_id,))

        row = cursor.fetchone()

        if row:
            return row[0]

        return None

    except Exception as e:
        logger.error(f"Failed to fetch YouTube URL: {str(e)}")
        return None
    

init_db()