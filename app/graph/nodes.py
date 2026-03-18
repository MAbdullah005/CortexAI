from app.tools.python_executor import python_executor
from __future__ import annotations


from app.graph.state import ChatState
from app.llm.llm_config import llm
from app.tools.python_executor import python_executor
from app.tools.calculator_tool import calculator
from app.tools.rag_tool import rag_tool
from app.tools.search_tool import search_tool
from app.tools.stock_tool import get_stock_price
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode


def chat_node(state: ChatState, config=None):
    """LLM node that may answer or request a tool call."""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
            "You are a helpful assistant. For questions about the uploaded PDF, call "
            "the `rag_tool` and include the thread_id "
            f"`{thread_id}`. You can also use the web search, stock price, and "
            "calculator tools when helpful. If no document is available, ask the user "
            "to upload a PDF."
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}

tools = [search_tool, get_stock_price, calculator, rag_tool,python_executor]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)
