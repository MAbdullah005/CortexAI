"""
RAG Tool

Retrieves relevant information from indexed PDFs for a given chat thread.
This tool queries the vector retriever associated with the thread and
returns relevant context for the LLM to generate grounded responses.
"""
"""

from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

#from app.core.retriever import _get_retriever, _THREAD_METADATA
from app.utils.logger import get_logger, log_latency

logger = get_logger(__name__)


@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
    
    Retrieve relevant document chunks from the indexed PDF for a specific chat thread.

    Parameters
    ----------
    query : str
        User question to search in the document.

    thread_id : Optional[str]
        Chat thread identifier used to locate the correct retriever.

    Returns
    -------
    Dict
        {
            "query": user query,
            "context": list of retrieved text chunks,
            "metadata": list of metadata for each chunk,
            "source_file": filename
        }
    

    logger.info(f"RAG tool called | query='{query}' | thread_id={thread_id}")

    if not thread_id:
        logger.warning("RAG tool called without thread_id")
        return {
            "error": "Thread ID is required to retrieve document context.",
            "query": query,
        }

    retriever = _get_retriever(thread_id)

    if retriever is None:
        logger.warning(f"No retriever found for thread {thread_id}")
        return {
            "error": "No document indexed for this chat. Please upload a PDF first.",
            "query": query,
        }

    try:

        with log_latency("RAG Retrieval"):

            results = retriever.invoke(query)

        context: List[str] = [doc.page_content for doc in results]
        metadata: List[Dict] = [doc.metadata for doc in results]

        source_file = _THREAD_METADATA.get(str(thread_id), {}).get("filename")

        logger.info(
            f"RAG retrieved {len(context)} chunks | source={source_file}"
        )

        return {
            "query": query,
            "context": context,
            "metadata": metadata,
            "source_file": source_file,
            "num_chunks": len(context),
        }

    except Exception as e:

        logger.error(f"RAG retrieval error: {str(e)}")

        return {
            "error": str(e),
            "query": query,
        }

        """