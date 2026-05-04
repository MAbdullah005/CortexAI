from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from app.memory.sqlite_memory import get_youtube_url
from app.services.youtube_loader import build_youtube_retriever
from app.core.retriever import get_thread_retriever

_YT_CACHE = {}

@tool
def youtube_rag_tool(query: str, config: RunnableConfig) -> str:
    """
    Answer questions using retrieved content from thread documents.
    """
    try:
        thread_id = config.get("configurable", {}).get("thread_id")

        if not thread_id:
            return "⚠️ Missing thread_id"

        retriever = get_thread_retriever(thread_id)

        docs = retriever.invoke(query)

        if not docs:
            return "❌ No relevant content found."

        context = "\n\n".join(d.page_content for d in docs)

        return f"""
Answer based on retrieved documents:

{context}

Question: {query}
"""

    except Exception as e:
        return f"❌ YouTube tool error: {str(e)}"