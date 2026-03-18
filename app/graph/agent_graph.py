from __future__ import annotations

"""
Agent Graph (Final Clean Version)

Flow:
START → planner → (tool_executor OR END)
tool_executor → planner (loop)

Uses:
- Planner-based reasoning
- Custom tool execution
- SQLite memory
"""

from typing import TypedDict, Annotated, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from app.graph.state import ChatState
from langchain_core.messages import BaseMessage

from app.graph.planner_node import planner_node
from app.graph.tool_executor_node import tool_executor_node
from app.memory.sqlite_memory import checkpointer

from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================
# State
# =========================================




# =========================================
# Router
# =========================================

def route_after_planner(state: ChatState):
    """
    Decide next step after planner
    """

    if state.get("tool_call"):
        return "tool_executor"

    return END


# =========================================
# Graph
# =========================================

graph = StateGraph(ChatState)

# Nodes
graph.add_node("planner", planner_node)
graph.add_node("tool_executor", tool_executor_node)

# Entry
graph.add_edge(START, "planner")

# Conditional routing
graph.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "tool_executor": "tool_executor",
        END: END,
    },
)

# Loop back
graph.add_edge("tool_executor", "planner")

# Compile
chatbot = graph.compile(checkpointer=checkpointer)