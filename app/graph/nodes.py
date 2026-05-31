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
    content=f"""
You are a helpful AI assistant with tool access.

Tool Selection:
- Questions about uploaded PDFs, documents, or YouTube content → use `unified_rag_tool`.
- External or real-time information → use `search_tool`.
- Mathematical calculations → use `calculator`.
- Code execution, analysis, or computation → use `python_executor`.
- If no tool is required, answer directly.

When answering document-related questions, rely on `unified_rag_tool` and do not make up information.

Thread ID: {thread_id}
"""
)
    
    print("this is message and user final input which we give to chatbot ",*state["messages"])

    messages = [system_message, *state["messages"]]
    print("here is system mesage ....",messages)
    response = llm_with_tools.invoke(messages, config=config)
    print("this is message by llm ",{"messages": [response]})
    return {"messages": [response]}

tools = [search_tool, get_stock_price, calculator,unified_rag_tool,python_executor]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)
