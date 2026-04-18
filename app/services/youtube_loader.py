from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS 
from langchain_ollama import OllamaEmbeddings
from app.core.vectorstore import create_vector_db
from app.core.splitter import chunk_text
from app.core.embeddings import get_embeddings
from youtube_transcript_api._errors import NoTranscriptFound, RequestBlocked
import re

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)

def load_youtube_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    print(url)

    try:
        # Universal method (works in all versions)
        print("2")
        ytt_api = YouTubeTranscriptApi()
        transcript_list=ytt_api.list(video_id=video_id)
        transcript = ytt_api.fetch(video_id,languages=['en'])
        #transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("2.1")
        if transcript_list==[]:


            try:
              #print(transcript_list)
              print("3")
              transcript = transcript_list.find_transcript(["en", "hi", "ur"])
            except NoTranscriptFound:
              print("4")
              transcript = transcript_list.find_generated_transcript(
                  transcript_list._generated_transcripts.keys()
              )

              print("5")
       # transcript_data = transcript.fetch()

    except RequestBlocked:
        return "no  video script avaliable"

    except Exception as e:
        return "done no voideo"

    text = " ".join(chunk.text for chunk in transcript)
    #print(text)
    return text



def build_youtube_retriever(url: str):
    """
    Build FAISS retriever from YouTube transcript
    """

    text = load_youtube_transcript(url)

    if not text or text.startswith("no") or text.startswith("done"):
        raise ValueError("No valid transcript found")

    # Chunking
    docs =chunk_text(text=text)

    # Embeddings (same style as your project)
    embeddings = get_embeddings()

    vectorstore = create_vector_db(docs,embeddings=embeddings)

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

"""
if __name__=='__main__':
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    load_youtube_transcript(url=url)

    """