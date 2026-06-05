from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from app.core.retriever import get_thread_retriever
from app.llm.llm_config import llm


@tool
def unified_rag_tool(query: str, config: RunnableConfig) -> str:
    """
    Answer questions using ALL documents (PDF + YouTube) in this thread
    """

    try:
        thread_id = config.get("configurable", {}).get("thread_id")

        if not thread_id:
            return "⚠️ Missing thread_id"

        retriever = get_thread_retriever(thread_id)

        if not retriever:
            return "⚠️ No documents loaded for this thread."

        docs = retriever.invoke(query)

        print(f"[RAG] Thread: {thread_id}")
        print(f"[RAG] Docs retrieved: {len(docs) if docs else 0}")

        if not docs:
            return "❌ No relevant information found."

        context = "\n\n".join(d.page_content for d in docs[:4])

        print("/n \n here is docs context which get from retriver /n",context)

        return llm.invoke(f"""
Answer ONLY from the context below.

Context:
{context}

Question:
{query}
""")


    except Exception as e:
        return f"❌ RAG tool error: {str(e)}"