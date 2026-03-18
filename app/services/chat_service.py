"""
Chat Service

Handles interaction between frontend (Streamlit) and LangGraph agent.
Keeps UI clean and manages chat execution, streaming, and formatting.
"""

from typing import Generator, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.graph.agent_graph import chatbot
from app.utils.logger import get_logger, set_request_id
from app.memory.sqlite_memory import retrieve_all_threads
from app.utils.thread_utils import format_messages_for_ui

logger = get_logger(__name__)


# =========================================
# Chat Execution (Streaming)
# =========================================

def stream_chat_response(user_input: str, thread_id: str) -> Generator[str, None, None]:
    """
    Stream AI response for a given user input and thread.

    Yields:
        str: chunks of AI response
    """

    set_request_id()

    logger.info(f"New chat request | thread_id={thread_id} | input={user_input}")

    CONFIG = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }

    try:

        for message_chunk, _ in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):

            # Log tool usage
            if isinstance(message_chunk, ToolMessage):
                tool_name = getattr(message_chunk, "name", "tool")
                logger.info(f"Tool used → {tool_name}")

            # Stream only AI messages
            if isinstance(message_chunk, AIMessage):
                yield message_chunk.content

    except Exception as e:

        logger.error(f"Chat streaming error: {str(e)}")

        yield "❌ Error generating response."


# =========================================
# Load Conversation
# =========================================

def load_conversation(thread_id: str):
    """
    Load past conversation from memory.
    """

    try:

        state = chatbot.get_state(
            config={"configurable": {"thread_id": thread_id}}
        )

        messages = state.values.get("messages", [])

        return format_messages_for_ui(messages)

    except Exception as e:

        logger.error(f"Failed to load conversation: {str(e)}")

        return []


# =========================================
# Thread Management
# =========================================

def get_all_threads():
    """
    Retrieve all thread IDs.
    """
    return retrieve_all_threads()


# =========================================
# Simple Chat (Non-Streaming - Optional)
# =========================================

def chat_once(user_input: str, thread_id: str) -> Dict[str, Any]:
    """
    Non-streaming version of chat (optional use).
    """

    set_request_id()

    logger.info(f"Chat once | thread_id={thread_id}")

    CONFIG = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }

    try:

        response = chatbot.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
        )

        ai_message = response["messages"][-1].content

        return {
            "response": ai_message
        }

    except Exception as e:

        logger.error(f"Chat error: {str(e)}")

        return {
            "error": str(e)
        }