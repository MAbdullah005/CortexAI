"""
Search Tool

Provides web search capability to the AI agent using DuckDuckGo.
Used for retrieving real-time information from the internet.
"""

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from app.utils.logger import get_logger, log_latency

logger = get_logger(__name__)

# Initialize search engine
search_engine = DuckDuckGoSearchRun(region="us-en")


@tool
def search_tool(query: str) -> str:
    """
    Perform a web search using DuckDuckGo.

    Parameters
    ----------
    query : str
        Search query from the user.

    Returns
    -------
    str
        Search results summary.
    """

    logger.info(f"Search tool called | query='{query}'")

    try:

        with log_latency("Web Search"):

            results = search_engine.run(query)

        logger.info("Search completed successfully")

        return results

    except Exception as e:

        logger.error(f"Search tool error: {str(e)}")

        return f"Search failed: {str(e)}"