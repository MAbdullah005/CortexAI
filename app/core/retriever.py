from __future__ import annotations

import os
import sqlite3
from typing import Dict, Any, Optional

from langchain_community.vectorstores import FAISS
from app.core.embeddings import get_embeddings
from app.memory.sqlite_memory import checkpointer

DB_PATH = "database/chatbot_conv.db"

# 🔥 CACHE (VERY IMPORTANT)
_THREAD_CACHE: Dict[str, Any] = {}


# ==============================
# MAIN RETRIEVER (FINAL VERSION)
# ==============================
def get_thread_retriever(thread_id: str):
    """
    Load and merge all vectorstores linked to a thread
    """

    # ✅ 1. Check cache
    if thread_id in _THREAD_CACHE:
        return _THREAD_CACHE[thread_id]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT vectorstore_path FROM documents
    JOIN thread_documents USING(doc_id)
    WHERE thread_id=?
    """, (thread_id,))

    rows = cursor.fetchall()
    print("THREAD ID:", thread_id)
    print("DB ROWS:", rows)
    conn.close()

    if not rows:
        return None

    embeddings = get_embeddings()

    vectorstores = []

    # ✅ 2. Load all vectorstores
    for (path,) in rows:
        try:
            if os.path.exists(path):
                vs = FAISS.load_local(
                    path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                vectorstores.append(vs)
        except Exception as e:
            print(f"⚠️ Failed loading vectorstore: {path} | {e}")

    if not vectorstores:
        return None
    

   

    retriever = SmartRetriever(vectorstores)

    # ✅ 4. Cache it
    _THREAD_CACHE[thread_id] = retriever


    return retriever


# ==============================
# OPTIONAL HELPERS (CLEAN)
# ==============================

def retrieve_all_threads():
    """
    Get all thread IDs from memory checkpoints
    """
    all_threads = set()

    for checkpoint in checkpointer.list(None):
        all_threads.add(
            checkpoint.config["configurable"]["thread_id"]
        )

    return list(all_threads)


def thread_has_document(thread_id: str) -> bool:
    """
    Check if thread has any documents in DB
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1 FROM thread_documents WHERE thread_id=? LIMIT 1
    """, (thread_id,))

    return cursor.fetchone() is not None


def clear_thread_cache(thread_id: str):
    """
    Clear cache when new document is added
    """
    if thread_id in _THREAD_CACHE:
        del _THREAD_CACHE[thread_id]


def thread_document_metadata(thread_id: str) -> dict:
    """
    Get metadata for all documents linked to a thread
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT type, source FROM documents
    JOIN thread_documents USING(doc_id)
    WHERE thread_id=?
    """, (thread_id,))

    rows = cursor.fetchall()

    if not rows:
        return {}

    sources = []

    for doc_type, source in rows:
        if doc_type == "pdf":
            name = source.split("/")[-1]  # filename
        elif doc_type == "youtube":
            name = f"https://www.youtube.com/watch?v={source}"
        else:
            name = source

        sources.append({
            "type": doc_type,
            "name": name
        })

    return {
        "total_docs": len(sources),
        "sources": sources
    }

class SmartRetriever:
    def __init__(self, stores):
        self.stores = stores

    def invoke(self, query):
        all_docs = []

        # 1. Get top results per store
        for vs in self.stores:
            try:
                docs = vs.similarity_search_with_score(query, k=3)

                for doc, score in docs:
                    doc.metadata["score"] = score
                    all_docs.append(doc)

            except Exception as e:
                print("Retriever error:", e)

        if not all_docs:
            return []

        # 2. Global ranking (LOWER score = better in FAISS)
        all_docs.sort(key=lambda x: x.metadata.get("score", 9999))

        # 3. Remove duplicates (optional but good)
        seen = set()
        unique_docs = []

        for doc in all_docs:
            content = doc.page_content.strip()

            if content not in seen:
                seen.add(content)
                unique_docs.append(doc)

        # 4. Return top N
        return unique_docs[:5]