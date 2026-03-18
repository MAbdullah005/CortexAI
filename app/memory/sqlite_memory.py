"""
SQLite Memory Store

Handles persistent conversation memory for the LangGraph agent
using SqliteSaver.
"""

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
    List[str]
        List of thread IDs.
    """

    logger.info("Retrieving all conversation threads")

    try:

        all_threads = set()

        for checkpoint in checkpointer.list(None):

            thread_id = checkpoint.config.get("configurable", {}).get("thread_id")

            if thread_id:
                all_threads.add(thread_id)

        threads = list(all_threads)

        logger.info(f"Found {len(threads)} threads")

        return threads

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