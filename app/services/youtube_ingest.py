import os
from app.services.youtube_loader import load_youtube_transcript
from app.core.splitter import chunk_text
from app.llm.embeddings import get_embeddings
from app.core.vectorstore import create_vector_db

def ingest_youtube(video_id: str, doc_id: str):
    """
    Build and SAVE vectorstore for YouTube video (ONLY ONCE)
    """

    # 🔥 Convert video_id → full URL
    url = f"https://www.youtube.com/watch?v={video_id}"

    text = load_youtube_transcript(url)

    if not text or text.startswith("no") or text.startswith("done"):
        raise ValueError("No valid transcript found")

    docs = chunk_text(text=text)
    embeddings = get_embeddings()

    vectorstore = create_vector_db(docs, embeddings=embeddings)

    # 🔥 SAVE FAISS
    save_path = os.path.join("data/yt/vectorstores/", doc_id)
    os.makedirs(save_path, exist_ok=True)

    vectorstore.save_local(save_path)

    return save_path