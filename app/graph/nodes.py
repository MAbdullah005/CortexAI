from app.tools.python_executor import python_executor
from __future__ import annotations


from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.graph.state import ChatState
from langchain_ollama import ChatOllama,OllamaEmbeddings
from app.tools import search_tool,rag_tool,stock_tool,calculator_tool
from langchain_core.messages import BaseMessage, SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition
import requests



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

tools = [search_tool, stock_tool, calculator_tool, rag_tool,python_executor]
llm=ChatOllama(model='qwen2.5:7b',temperature=0.2)

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)
