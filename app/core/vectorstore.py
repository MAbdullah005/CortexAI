from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import time

BATCH_SIZE = 50


def create_vector_db(chunks, embeddings):
    db = None

    try:
        for i in range(0, len(chunks), BATCH_SIZE):

            batch = chunks[i:i+BATCH_SIZE]

            if db is None:
                db = FAISS.from_documents(
                    batch,
                    embedding=embeddings
                )
            else:
                db.add_documents(batch)

            time.sleep(2)

        return db

    except Exception as e:

        print(f"Google embedding failed: {e}")

        fallback = OllamaEmbeddings(
            model="nomic-embed-text",
            keep_alive=-1
        )

        db = None

        for i in range(0, len(chunks), BATCH_SIZE):

            batch = chunks[i:i+BATCH_SIZE]

            if db is None:
                db = FAISS.from_documents(
                    batch,
                    embedding=fallback
                )
            else:
                db.add_documents(batch)

            time.sleep(2)

        return db