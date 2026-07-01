

import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings

from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

USE_OPENAI = False

DEFAULT_GOOGLE_EMBEDDING = "gemini-embedding-001"
DEFAULT_OLLAMA_EMBEDDING = "nomic-embed-text"


def google_available():
    return os.getenv("Gemini_API_Key") is not None



def openai_available():
    return os.getenv("OPENAI_API_KEY") is not None


def load_embeddings():
  

    if google_available():
        try:
            logger.info("Loading Google Embeddings")

            return GoogleGenerativeAIEmbeddings(
                model=DEFAULT_GOOGLE_EMBEDDING
            )

        except Exception as e:
            logger.warning(f"Google embeddings failed. Falling back... {e}")

    # -------------------------
    # OpenAI (Optional)
    # -------------------------
    if USE_OPENAI and openai_available():
        try:
            logger.info("Loading OpenAI Embeddings")

            return OpenAIEmbeddings()

        except Exception as e:
            logger.warning(f"OpenAI embeddings failed. Falling back... {e}")

    logger.info("Loading Ollama Nomic Embeddings")

    return OllamaEmbeddings(
        model=DEFAULT_OLLAMA_EMBEDDING,
        keep_alive=-1
    )


def get_embeddings():
    return load_embeddings()


embeddings = get_embeddings()