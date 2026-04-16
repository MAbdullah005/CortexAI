from __future__ import annotations
from app.tools.python_executor import python_executor


from app.graph.state import ChatState
from app.llm.llm_config import llm
from app.tools.python_executor import python_executor
from app.tools.youtube_tool import youtube_rag_tool
from app.tools.calculator_tool import calculator
from langchain_core.tools import Tool
from app.memory.sqlite_memory import get_youtube_url
from app.tools.rag_tool import rag_tool
from app.tools.search_tool import search_tool
from app.tools.stock_tool import get_stock_price
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode

"""def youtube_tool_wrapper(query: str, config: dict = None):
    thread_id = None
    if config:
        thread_id = config.get("configurable", {}).get("thread_id")

    return youtube_rag_tool.invoke({
        "query": query,
        "thread_id": thread_id
    })
"""
"""youtube_tool = Tool(
    name="youtube_rag_tool",
    func=youtube_tool_wrapper,
    description="Answer questions from a YouTube video transcript."
)"""


def chat_node(state: ChatState, config=None):
    """LLM node that may answer or request a tool call."""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
    content=(
        "You are an intelligent AI assistant with access to multiple tools.\n\n"

        "STRICT RULES:\n"
        "1. If a YouTube video is loaded, ALWAYS use `youtube_rag_tool` for ANY question about the video.\n"
        "2. NEVER ask for the YouTube URL if it already exists.\n"
        "3. DO NOT answer from your own knowledge if a tool is available.\n"

        "TOOLS:\n"
        "- youtube_rag_tool → for video questions\n"
        "- rag_tool → for PDFs\n"
        "- search_tool → for web\n"
        "- calculator → math\n"
        "- get_stock_price → stocks\n\n"

        f"Current thread_id: {thread_id}\n"
    )
)

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    print("this is message by llm ",{"messages": [response]})
    return {"messages": [response]}

tools = [search_tool, get_stock_price, calculator, rag_tool,python_executor,youtube_rag_tool]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)
