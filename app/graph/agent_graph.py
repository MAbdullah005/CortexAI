from __future__ import annotations

from typing import Annotated, Any, Dict, Optional, TypedDict
from app.graph.state import ChatState
from app.graph.nodes import chat_node,tool_node
from app.memory.sqlite_memory import checkpointer
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import requests

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)
