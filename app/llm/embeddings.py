from langchain_ollama import  OllamaEmbeddings
from langchain_openai import  OpenAIEmbeddings

from dotenv import load_dotenv



from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


USE_OPENAI = False   # Change to True if you want OpenAI

def load_embeddings():
    """
    Load embedding model.
    """

    if USE_OPENAI:

        logger.info("Loading OpenAI embeddings")

        return OpenAIEmbeddings()

    else:

        logger.info("Loading Ollama embeddings")

        return OllamaEmbeddings(
            model="nomic-embed-text",
            temperature=0.2,
            keep_alive=-1
        )


get_embeddings=load_embeddings()