"""
Search Tool

Primary:
    - Tavily Search

Fallback:
    - DuckDuckGo Search

This provides better search quality while sremaining resilient if
Tavily is unavailable.
"""

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from functools import lru_cache
import os
from dotenv import load_dotenv

from app.utils.logger import get_logger, log_latency
load_dotenv()


logger = get_logger(__name__)

# -------------------------
# Primary Search
# -------------------------
tavily_search = TavilySearchResults(max_results=5)

# -------------------------
# Fallback Search
# -------------------------
duckduckgo_search = DuckDuckGoSearchRun(
    region="us-en"
)

# use for catch if same question ask for in same session
@lru_cache(maxsize=200)
def cached_search(query: str):
    """
    Cache Tavily search results so repeated
    queries don't hit the API again.
    """
    return tavily_search.invoke(query)


@tool
def search_tool(query: str) -> str:
    """
    Perform an internet search.

    Search order:
        1. Tavily
        2. DuckDuckGo (fallback)

    Parameters
    ----------
    query : str
        User search query.

    Returns
    -------
    str
        Search results.
    """

    logger.info(f"Search tool called | query='{query}'")

    # ==========================
    # Try Tavily
    # ==========================
    try:
        logger.info("Using Tavily Search")

        with log_latency("Tavily Search"):

            result = cached_search(query)

        logger.info("Tavily search completed successfully")


        return result


    except Exception as e:

        logger.warning(
            f"Tavily failed. Switching to DuckDuckGo. Error: {e}"
        )

    # ==========================
    # Fallback DuckDuckGo
    # ==========================
    try:

        with log_latency("DuckDuckGo Search"):

            result = duckduckgo_search.run(query)

        logger.info("DuckDuckGo search completed successfully")

        return result

    except Exception as e:

        logger.error(f"Both search engines failed: {e}")

        return (
            "Unable to retrieve search results at the moment. "
            "Please try again later."
        )