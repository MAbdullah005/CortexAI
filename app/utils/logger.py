import logging
import os
import time
import uuid
from contextvars import ContextVar

# ================================
# Request Context (for request id)
# ================================
request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")


def set_request_id():
    """Generate and store request id for the current request"""
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    return request_id


def get_request_id():
    return request_id_var.get()


# ================================
# Logging Setup
# ================================
LOG_DIR = "logs"
LOG_FILE = "logs/app.log"

os.makedirs(LOG_DIR, exist_ok=True)


class RequestFormatter(logging.Formatter):
    """Add request id to every log automatically"""

    def format(self, record):
        record.request_id = get_request_id()
        return super().format(record)


def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = RequestFormatter(
        "%(asctime)s | %(levelname)s | req:%(request_id)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = get_logger("AI-Agent")


# ================================
# Tool Logging
# ================================
def log_tool_usage(tool_name: str, input_data=None, output_data=None):

    logger.info(f"TOOL START → {tool_name}")
    if input_data:
        logger.debug(f"TOOL INPUT → {input_data}")

    if output_data:
        logger.debug(f"TOOL OUTPUT → {output_data}")

    logger.info(f"TOOL END → {tool_name}")


# ================================
# Latency Logger
# ================================
class log_latency:

    def __init__(self, step_name: str):
        self.step_name = step_name

    def __enter__(self):
        self.start = time.time()
        logger.info(f"STEP START → {self.step_name}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = round(time.time() - self.start, 3)
        logger.info(f"STEP END → {self.step_name} | latency={duration}s")


# ================================
# Agent Step Logger
# ================================
def log_agent_step(step: str, message=None):
    logger.info(f"AGENT STEP → {step}")
    if message:
        logger.debug(f"STEP DATA → {message}")