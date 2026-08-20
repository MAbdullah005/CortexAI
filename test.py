import sqlite3
import os
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")

os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor=conn.cursor()
cursor.execute("""
ALTER TABLE documents
ADD COLUMN user_id INTEGER
""")