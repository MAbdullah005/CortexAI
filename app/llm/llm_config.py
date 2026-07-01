
import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


DEFAULT_LOCAL_MODEL = "qwen2.5:3b"
DEFAULT_LOCAL_MODEL_title = "qwen2.5:0.5b"

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

DEFAULT_TEMPERATURE = 0.2

USE_OPENAI = False   # optional manual override



def gemini_available():
    return os.getenv("Gemini_API_Key") is not None


def openai_available():
    return os.getenv("OPENAI_API_KEY") is not None



def load_llm():


    if gemini_available():
        try:
            logger.info("Loading Gemini LLM")

            return ChatGoogleGenerativeAI(
                model=DEFAULT_GEMINI_MODEL,
                temperature=DEFAULT_TEMPERATURE
            )

        except Exception as e:
            logger.warning(f"Gemini failed, falling back... {e}")

    if USE_OPENAI and openai_available():
        try:
            logger.info("Loading OpenAI LLM")

            return ChatOpenAI(
                model=DEFAULT_OPENAI_MODEL,
                temperature=DEFAULT_TEMPERATURE
            )

        except Exception as e:
            logger.warning(f"OpenAI failed, falling back... {e}")

    logger.info(f"Loading Ollama model: {DEFAULT_LOCAL_MODEL}")

    return ChatOllama(
        model=DEFAULT_LOCAL_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        keep_alive=-1
    )


def generate_title_llm():

    # Gemini for title generation
    if gemini_available():
        try:
            logger.info("Loading Gemini Title LLM")

            return ChatGoogleGenerativeAI(
                model=DEFAULT_GEMINI_MODEL,
                temperature=0.3
            )

        except Exception as e:
            logger.warning(f"Gemini title failed: {e}")

    # OpenAI fallback
    if USE_OPENAI and openai_available():
        logger.info("Loading OpenAI Title LLM")

        return ChatOpenAI(
            model=DEFAULT_OPENAI_MODEL,
            temperature=0.3
        )

    # Ollama fallback
    logger.info(f"Loading Ollama title model: {DEFAULT_LOCAL_MODEL_title}")

    return ChatOllama(
        model=DEFAULT_LOCAL_MODEL_title,
        temperature=0.3,
        keep_alive=-1
    )



llm = load_llm()
gen_title = generate_title_llm()