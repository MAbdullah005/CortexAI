

import uuid
from typing import List
from langchain_core.messages import HumanMessage, AIMessage


def generate_thread_id() -> str:
    """
    Generate a unique thread ID.
    """
    return str(uuid.uuid4())


def add_thread(thread_id: str, thread_list: List[str]) -> List[str]:
    """
    Add thread to thread list if not present.
    """
    if thread_id not in thread_list:
        thread_list.append(thread_id)
    return thread_list


def format_messages_for_ui(messages):
    """
    Convert LangChain messages to UI friendly format.
    """
    formatted = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue

        formatted.append(
            {
                "role": role,
                "content": msg.content
            }
        )

    return formatted


def reverse_threads(threads: List[str]) -> List[str]:
    """
    Show newest threads first.
    """
    return list(reversed(threads))


def thread_exists(thread_id: str, thread_list: List[str]) -> bool:
    """
    Check if thread exists.
    """
    return thread_id in thread_list
