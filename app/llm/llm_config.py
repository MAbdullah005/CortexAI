
"""
LLM Configuration

Central place for initializing LLMs and embeddings used in the project.
Supports easy switching between local (Ollama) and cloud models.
"""

from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

# ================================
# Model Settingas
# ================================

DEFAULT_LOCAL_MODEL = "qwen2.5:3b"
DEFAULT_LOCAL_MODEL_title="qwen2.5:0.5b"

DEFAULT_TEMPERATURE = 0.2

USE_OPENAI = False   # Change to True if you want OpenAI


# ================================
# LLM Loader
# ================================

def load_llm():
    """
    Load the main language model.
    """

    if USE_OPENAI:

        logger.info("Loading OpenAI LLM")

        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=DEFAULT_TEMPERATURE
        )

    else:

        logger.info(f"Loading Ollama model: {DEFAULT_LOCAL_MODEL}")

        return ChatOllama(
            model=DEFAULT_LOCAL_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            keep_alive=-1
        )
    

def generate_title_llm():

    if USE_OPENAI:

        logger.info("Loading OpenAI LLM")

        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=DEFAULT_TEMPERATURE
        )

    else:

        logger.info(f"Loading Ollama model: {DEFAULT_LOCAL_MODEL_title}")

        return ChatOllama(
            model=DEFAULT_LOCAL_MODEL_title,
            temperature=DEFAULT_TEMPERATURE,
            keep_alive=-1
        )



llm = load_llm()

