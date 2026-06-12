import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'prompts.db')

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   member_name TEXT,
                   department TEXT,
                   original_prompt TEXT,
                   score INTEGER,
                   improved_prompt TEXT,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
