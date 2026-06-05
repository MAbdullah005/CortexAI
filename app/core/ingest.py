from __future__ import annotations

import os
import tempfile
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from app.core.embeddings import get_embeddings


def ingest_pdf(file_bytes: bytes, filename: Optional[str], doc_id: str) -> str:
    """
    Build and SAVE vectorstore for PDF (ONLY ONCE)

    Returns:
        vectorstore_path
    """

    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    # 🔥 Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        # Load PDF
        print("here is temp path ",temp_path)
        print("here is temp file  name ",temp_file)

        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        # Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)
        for chunk in chunks:
          chunk.metadata["source"] = filename or "pdf"
          chunk.metadata["doc_id"] = doc_id

        if not chunks:
            raise ValueError("No text extracted from PDF")

        # Embeddings
        embeddings = get_embeddings()

        # Vectorstore
        vector_store = FAISS.from_documents(chunks, embeddings)

        # 🔥 SAVE VECTORSTORE
        save_path = os.path.join(f"data/pdf/vectorstores", doc_id)
        os.makedirs(save_path, exist_ok=True)

        vector_store.save_local(save_path)

        return save_path

    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass