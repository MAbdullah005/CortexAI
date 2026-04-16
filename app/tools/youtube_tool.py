from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from app.memory.sqlite_memory import get_youtube_url
from app.services.youtube_loader import build_youtube_retriever

_YT_CACHE = {}

@tool
def youtube_rag_tool(query: str, config: RunnableConfig) -> str:
    """
    YouTube RAG Tool (FINAL FIXED VERSION)
    """

    try:
        thread_id = config.get("configurable", {}).get("thread_id")

        if not thread_id:
            return "⚠️ Missing thread_id"

        youtube_url = get_youtube_url(thread_id)

        if not youtube_url:
            return "⚠️ No YouTube video found. Please load a video first."

        # Cache retriever
        if thread_id not in _YT_CACHE:
            retriever = build_youtube_retriever(youtube_url)
            _YT_CACHE[thread_id] = retriever
        else:
            retriever = _YT_CACHE[thread_id]

       # docs = retriever.get_relevant_documents(query)
        retriever_1 = retriever.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
        retrieved_docs = retriever_1.invoke(query)

        if not docs:
            return "❌ No relevant content found in video."

        context = "\n\n".join(d.page_content for d in docs)

        return f"""
Answer based ONLY on this YouTube video:

{context}

Question: {query}
"""

    except Exception as e:
        return f"❌ YouTube tool error: {str(e)}"