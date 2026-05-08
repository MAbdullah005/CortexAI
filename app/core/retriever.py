from __future__ import annotations

import os
import sqlite3
from typing import Dict, Any, Optional

from langchain_community.vectorstores import FAISS
from app.core.embeddings import get_embeddings
from app.memory.sqlite_memory import checkpointer
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
DB_PATH = "database/chatbot_conv.db"

# 🔥 CACHE (VERY IMPORTANT)
_THREAD_CACHE: Dict[str, Any] = {}


# ==============================
# MAIN RETRIEVER (FINAL VERSION)a
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

        # 🔥 ALL DOCS FOR BM25
        self.all_documents = []

        for vs in stores:
            try:
                docs = vs.similarity_search("", k=1000)

                self.all_documents.extend(docs)

            except Exception as e:
                print("BM25 load error:", e)

        # 🔥 TOKENIZE FOR BM25
        self.bm25_docs = [
            doc.page_content.split()
            for doc in self.all_documents
        ]

        # 🔥 BM25 INDEX
        self.bm25 = BM25Okapi(self.bm25_docs)

    def invoke(self, query):

        dense_results = []
        sparse_results = []

        # =========================================
        # 1. DENSE SEARCH (FAISS)
        # =========================================
        for vs in self.stores:

            try:
                docs = vs.similarity_search_with_score(query, k=4)

                for doc, score in docs:

                    doc.metadata["dense_score"] = float(score)

                    dense_results.append(doc)

            except Exception as e:
                print("Dense retrieval error:", e)

        # =========================================
        # 2. BM25 SEARCH
        # =========================================

        tokenized_query = query.split()

        bm25_scores = self.bm25.get_scores(tokenized_query)

        scored_docs = list(zip(self.all_documents, bm25_scores))

        scored_docs.sort(key=lambda x: x[1], reverse=True)

        top_sparse = scored_docs[:4]

        for doc, score in top_sparse:

            doc.metadata["bm25_score"] = float(score)

            sparse_results.append(doc)

        # =========================================
        # 3. MERGE RESULTS
        # =========================================

        combined = dense_results + sparse_results

        # =========================================
        # 4. REMOVE DUPLICATES
        # =========================================

        unique_docs = []
        seen = set()

        for doc in combined:

            content = doc.page_content.strip()

            if content not in seen:

                seen.add(content)

                unique_docs.append(doc)

        # =========================================
        # 5. OPTIONAL RERANK
        # =========================================

        def final_score(doc):

            dense = doc.metadata.get("dense_score", 1000)

            bm25 = doc.metadata.get("bm25_score", 0)

            # LOWER dense is better
            dense_part = 1 / (1 + dense)

            return dense_part + (0.3 * bm25)

        unique_docs.sort(
            key=final_score,
            reverse=True
        )

        return unique_docs[:5]