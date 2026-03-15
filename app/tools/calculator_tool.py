
"""
Calculator Tool

Provides basic arithmetic operations for the AI agent.
Supports: addition, subtraction, multiplication, division
"""

from langchain_core.tools import tool
from app.utils.logger import get_logger

logger = get_logger(__name__)


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.

    Parameters
    ----------
    first_num : float
        First number in the calculation

    second_num : float
        Second number in the calculation

    operation : str
        Operation to perform.
        Supported operations:
        - add
        - sub
        - mul
        - div

    Returns
    -------
    dict
        Contains calculation result or error message.
    """

    logger.info(f"Calculator tool called | operation={operation} | {first_num}, {second_num}")

    try:

        if operation == "add":
            result = first_num + second_num

        elif operation == "sub":
            result = first_num - second_num

        elif operation == "mul":
            result = first_num * second_num

        elif operation == "div":
            if second_num == 0:
                logger.warning("Division by zero attempted")
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num

        else:
            logger.error(f"Unsupported operation: {operation}")
            return {"error": f"Unsupported operation '{operation}'"}

        response = {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }

        logger.info(f"Calculator result: {result}")

        return response

    except Exception as e:

        logger.error(f"Calculator error: {str(e)}")

        return {
            "error": str(e)
        }