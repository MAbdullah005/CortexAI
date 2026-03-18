"""
Tool Registry

Central place to register and manage all tools used by the agent.
Keeps agent clean and allows easy scaling of tools.
"""

from langchain.tools import BaseTool

# Import all tools here
from app.tools.calculator_tool import calculator
from app.tools.rag_tool import rag_tool
from app.tools.search_tool import search_tool
from app.tools.stock_tool import get_stock_price
from app.tools.python_executor import python_executor

from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================
# Tool List
# =========================================

def get_all_tools() -> list[BaseTool]:
    """
    Return all tools available to the agent.
    """

    tools = [
        calculator,
        rag_tool,
        search_tool,
        get_stock_price,
        python_executor
    ]

    logger.info(f"{len(tools)} tools loaded")

    return tools


# =========================================
# Tool Map (Optional Advanced Use)
# =========================================

def get_tool_map():
    """
    Returns tool dictionary for quick lookup.
    Useful for advanced agent control.
    """

    tools = get_all_tools()

    return {tool.name: tool for tool in tools}


# =========================================
# Future Extensions (VERY IMPORTANT)
# =========================================

"""
Later you can extend this file to support:

- Tool permissions (per user / per thread)
- Tool filtering (enable/disable tools dynamically)
- Logging tool usage
- Tool categories (finance, rag, utility, etc.)
"""