"""
PDF Service

Handles:
- PDF upload
- Text extraction
- Chunking
- Vector store creation
- Thread metadata storage
"""

import os
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.llm.llm_config import embeddings
from app.config.settings import (
    UPLOAD_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_K,
)

from app.rag.retriever import _store_retriever, _THREAD_METADATA
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================
# Ensure directories exist
# =========================================

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================
# PDF Processing
# =========================================

def process_pdf(file_path: str, thread_id: str) -> dict:
    """
    Process PDF and create retriever for a thread.
    """

    try:
        logger.info(f"Processing PDF | thread_id={thread_id}")

        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        if not documents:
            return {"error": "No content found in PDF."}

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        docs = splitter.split_documents(documents)

        logger.info(f"PDF split into {len(docs)} chunks")

        # Create vectorstore (FAISS)
        from langchain_community.vectorstores import FAISS

        vectorstore = FAISS.from_documents(docs, embeddings)

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": RETRIEVAL_K}
        )

        # Store retriever for thread
        _store_retriever(thread_id, retriever)

        # Save metadata
        _THREAD_METADATA[thread_id] = {
            "filename": os.path.basename(file_path),
            "num_chunks": len(docs),
        }

        logger.info("PDF processed successfully")

        return {
            "status": "success",
            "chunks": len(docs),
            "file": os.path.basename(file_path),
        }

    except Exception as e:
        logger.error(f"PDF processing error: {str(e)}")

        return {"error": str(e)}


# =========================================
# Save Uploaded File
# =========================================

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """
    Save uploaded file to disk.
    """

    try:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        logger.info(f"File saved: {file_path}")

        return file_path

    except Exception as e:
        logger.error(f"File save error: {str(e)}")
        return None


# =========================================
# Full Pipeline (Upload + Process)
# =========================================

def handle_pdf_upload(uploaded_file, thread_id: str) -> dict:
    """
    Complete PDF upload pipeline.
    """

    file_path = save_uploaded_file(uploaded_file)

    if not file_path:
        return {"error": "Failed to save file."}

    return process_pdf(file_path, thread_id)