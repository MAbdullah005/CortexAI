from app.core.retriever import thread_document_metadata
import streamlit as st
import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver
"""
DB_DIR="database"
DB_PATH=os.path.join(DB_DIR,"chatbot_conv.db")
conn=sqlite3.connect(DB_PATH,check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)
doc_id="108a6263-0b4b-444b-901e-1809cba1c6bb"

cursor = conn.cursor()

cursor.execute(
    SELECT source FROM documents
    JOIN thread_documents USING(doc_id)
    WHERE thread_id=? AND type='youtube'
    , ("3e59efed-9c3a-4ae1-903c-568dde0bb861",))

row = cursor.fetchone()

"""
metadata = thread_document_metadata("f2aed66c-655f-46fa-a871-9408765665fa")
available_types = {
         source["type"]
         for source in metadata["sources"]
          }
print(available_types)



