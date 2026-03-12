
"""
Python Execution Tool

Allows the AI agent to execute small Python code snippets and return
the output. Useful for calculations, data analysis, quick scripting,
and reasoning tasks.

⚠️ WARNING:
This should only run in a controlled environment. Do NOT expose this
directly in public production without sandboxing (Docker / restricted env).
"""

import io
import contextlib
from langchain_core.tools import tool


@tool
def python_executor(code: str) -> str:
    """
    Execute a Python code snippet and return its output.

    Input:
        code (str): Python code to execute

    Returns:
        str: Printed output or error message
    """

    output_buffer = io.StringIO()

    try:
        # Capture print output
        with contextlib.redirect_stdout(output_buffer):
            exec(code, {})

        output = output_buffer.getvalue()

        if output.strip() == "":
            return "✅ Code executed successfully (no output)."

        return f"✅ Output:\n{output}"

    except Exception as e:
        return f"❌ Execution Error:\n{str(e)}"