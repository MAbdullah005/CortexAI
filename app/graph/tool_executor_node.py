"""
Tool Executor Node

Responsible for:
- Executing tools selected by planner
- Handling errors safely
- Returning results back to the agent

This is the "hands" of your agent.
"""

from typing import Dict, Any

from langchain_core.messages import ToolMessage

from app.tools.tools_registry import get_tool_map
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Load tools once
TOOL_MAP = get_tool_map()


# =========================================
# Tool Executor Logic
# =========================================

def tool_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the tool selected by planner.
    """

    try:
        tool_call = state.get("tool_call")

        if not tool_call:
            logger.warning("No tool_call found in state")

            return {
                "messages": [
                    ToolMessage(
                        content="No tool was selected.",
                        name="tool_executor"
                    )
                ]
            }

        tool_name = tool_call.get("name")
        tool_input = tool_call.get("input")

        logger.info(f"Executing tool: {tool_name} | input={tool_input}")

        # Get tool
        tool = TOOL_MAP.get(tool_name)

        if not tool:
            logger.error(f"Tool not found: {tool_name}")

            return {
                "messages": [
                    ToolMessage(
                        content=f"Tool '{tool_name}' not found.",
                        name=tool_name
                    )
                ]
            }

        # Execute tool
        try:
            result = tool.invoke(tool_input)
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")

            return {
                "messages": [
                    ToolMessage(
                        content=f"Error executing tool: {str(e)}",
                        name=tool_name
                    )
                ]
            }

        logger.info(f"Tool executed successfully: {tool_name}")

        return {
            "messages": [
                ToolMessage(
                    content=str(result),
                    name=tool_name
                )
            ]
        }

    except Exception as e:

        logger.error(f"Tool executor failed: {str(e)}")

        return {
            "messages": [
                ToolMessage(
                    content="❌ Tool execution failed.",
                    name="tool_executor"
                )
            ]
        }