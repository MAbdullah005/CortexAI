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


from langgraph.graph import StateGraph, START, END
from app.graph.state import ChatState
from langgraph.prebuilt import tools_condition

from app.graph.nodes import chat_node,tool_node
from app.memory.sqlite_memory import checkpointer

from app.utils.logger import get_logger

logger = get_logger(__name__)


graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools",tool_node)

# Start
graph.add_edge(START, "chat_node")

# Conditional routing
graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {
        "tools":"tools",
        "__end__":END
    }
)

# Loop
graph.add_edge("tools", "chat_node")

# Compile
chatbot = graph.compile(checkpointer=checkpointer)