from __future__ import annotations
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))



from app.graph.state import ChatState
from app.llm.llm_config import llm
from app.tools.python_executor import python_executor
from app.tools.calculator_tool import calculator
from app.tools.unified_rag_tool import unified_rag_tool
from langchain_core.messages import ToolMessage
from app.tools.search_tool import search_tool
from app.tools.stock_tool import get_stock_price
from app.utils.logger import logger
from langchain_core.messages import SystemMessage
from typing import Annotated
from app.core.retriever import thread_document_metadata

from langgraph.prebuilt import ToolNode


def chat_node(state: ChatState, config=None):
    """LLM node that may answer or request a tool call."""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    last_message=state["messages"][-1] if state["messages"] else None
    print("last message ",last_message)

    if isinstance(last_message, ToolMessage):

       if last_message.name == "unified_rag_tool":
           logger.info("Generate final answer from RAG context.")
           logger.info("RAG Tool already executed -> Final answer generation")


           response = llm.invoke(state["messages"], config=config)

           return {"messages": [response]}


    metadata=thread_document_metadata(thread_id=thread_id)

    system_message = SystemMessage(
    content=f"""
You are a helpful AI assistant with access to tools.

CURRENT THREAD DOCUMENTS:
{metadata}

AVAILABLE TOOLS:

1. unified_rag_tool
   - Use this tool when the user's question can be answered from uploaded PDFs,
     uploaded documents, resumes, reports, files, or uploaded YouTube videos.
   - If the question refers to content that may exist inside the uploaded sources,
     ALWAYS use unified_rag_tool first.
   - Examples:
       • Summarize the uploaded PDF
       • summarize this uploaded video
       • What skills are listed in the resume?
       • What did the YouTube video say about CNNs?
2. search_tool
   - Use for information NOT contained in uploaded documents.
   - Use for current events, news, web search, external knowledge,
   - Examples:
       • Latest AI news
       • Who is the CEO of OpenAI?
       • Current weather

3. get_stock_price
   - Use when user asks about stock prices, stock symbols,
     market prices, or company stock performance.

4. calculator
   - Use for arithmetic, formulas, percentages,
     mathematical calculations.

5. python_executor
   - Use when code execution, data analysis,
     dataframe manipulation, scripting,
     or computation is required.

IMPORTANT RULES:

- First determine whether the question can be answered from uploaded documents.
- If the answer requires internet knowledge instead, use search_tool.
- If the answer is obvious and no tool is needed, answer directly.

Thread ID: {thread_id}
"""
)
    messages = [system_message, *state["messages"]]
    print("here is system mesage to llm_tool ....",messages)
    response = llm_with_tools.invoke(messages, config=config)
    print("this is message by llm_tool ",{"messages": [response]})


    return {"messages": [response]}

tools = [search_tool, get_stock_price, calculator,unified_rag_tool,python_executor]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

"""msg = llm_with_tools.invoke(
    "Summarize the uploaded resume document using unified_rag_tool"
)

print(msg)s
print(msg.tool_calls)

print("tool args ",unified_rag_tool.args)
print("tool call schema ",unified_rag_tool.tool_call_schema)
"""