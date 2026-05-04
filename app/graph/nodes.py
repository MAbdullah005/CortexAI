from __future__ import annotations


from app.graph.state import ChatState
from app.llm.llm_config import llm
from app.tools.python_executor import python_executor
from app.tools.calculator_tool import calculator
from app.tools.unified_rag_tool import unified_rag_tool
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
        "You are an AI assistant with tool access.\n\n"

        "STRICT RULES:\n"
        "1. If ANY document (PDF or YouTube) exists → ALWAYS use `unified_rag_tool`\n"
        "2. NEVER answer from your own knowledge if documents exist\n"
        "3. Do NOT say 'I cannot access the document'\n"
        "4. Use search_tool ONLY for external info\n"
        "5. Use calculator for math\n\n"
        "6. Prefer `unified_rag_tool` whenever possible\n"

        f"Thread ID: {thread_id}\n"
    )
)

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    print("this is message by llm ",{"messages": [response]})
    return {"messages": [response]}

tools = [search_tool, get_stock_price, calculator,unified_rag_tool,python_executor]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)
