
"""
Stock Price Tool

Fetches the latest stock price using Alpha Vantage API.
"""

import os
import requests
from langchain_core.tools import tool
from app.utils.logger import get_logger, log_latency
from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest stock price for a given stock symbol.

    Parameters
    ----------
    symbol : str
        Stock ticker symbol (e.g., AAPL, TSLA, MSFT)

    Returns
    -------
    dict
        Stock price data or error message.
    """

    logger.info(f"Stock tool called | symbol={symbol}")

    if not ALPHA_VANTAGE_API_KEY:
        logger.error("Alpha Vantage API key missing")
        return {"error": "Alpha Vantage API key not configured"}

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:

        with log_latency("Stock API Request"):

            response = requests.get(url, params=params, timeout=10)

        data = response.json()

        quote = data.get("Global Quote", {})

        if not quote:
            logger.warning(f"No data returned for symbol {symbol}")
            return {"error": f"No stock data found for symbol '{symbol}'"}

        result = {
            "symbol": quote.get("01. symbol"),
            "price": quote.get("05. price"),
            "change": quote.get("09. change"),
            "change_percent": quote.get("10. change percent"),
            "latest_trading_day": quote.get("07. latest trading day")
        }

        logger.info(f"Stock data retrieved | {symbol} price={result['price']}")

        return result

    except Exception as e:

        logger.error(f"Stock API error: {str(e)}")

        return {"error": str(e)}

