from langchain.tools import tool
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain_core.runnables import RunnableConfig
from app.core.retriever import get_thread_retriever
from app.llm.llm_config import llm
from langchain_core.tools import InjectedToolArg
from typing import Annotated
from app.core.retriever import thread_document_metadata
from app.core.source_router import detect_source

@tool
def unified_rag_tool(query: str, config:Annotated[RunnableConfig,InjectedToolArg]) -> str:
    """
    Search and answer questions from. ALL uploaded PDFs,
    resumes, documents, files, and YouTube videos
    attached to the current thread.

    Use this tool whenever the user asks about
    uploaded content, summaries or summarys, information contained
    in documents, resumes, reports, or videos.

    Do NOT use for internet searches or current events.
    """

    try:
        thread_id = config.get("configurable", {}).get("thread_id")

        if not thread_id:
            return "⚠️ Missing thread_id"
        
        metadata = thread_document_metadata(thread_id)

        if not metadata:
           return "⚠️ No documents attached to this thread."

        available_types = {
         source["type"]
         for source in metadata["sources"]
          }
        
        print(
    f"[ROUTER] Available Sources: {available_types}"
      )

        if len(available_types)==1:
            source_type=list(available_types)[0]

        else:
            source_type=detect_source(query=query)

            print(
              f"[ROUTER] source_type={source_type}"
)

        retriever = get_thread_retriever(thread_id,source_type=source_type)

        if not retriever:
            return "⚠️ No documents loaded for this thread."

        docs = retriever.invoke(query)

        print(f"[RAG] Thread: {thread_id}")
        print(f"[RAG] Docs retrieved: {len(docs) if docs else 0}")

        if not docs:
            return "❌ No relevant information found."

        context = "\n\n".join(d.page_content for d in docs[:4])

        print("/n \n here is docs context which get from retriver /n",context)

        return f"""
             You are answering ONLY from retrieved context.
 
             Rules:

             - Never use outside knowledge.
             - If information is missing, say so.
             - Do not invent facts.
             - Do not merge unrelated chunks.
              - If summarizing a document or video,
             summarize the retrieved content only.
 
            Context: {context}
            sources: {source_type}

            Question: {query}
    """

    except Exception as e:
        return f"❌ RAG tool error: {str(e)}"
    

