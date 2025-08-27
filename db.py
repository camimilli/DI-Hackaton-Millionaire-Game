import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection  = psycopg2.connect(os.getenv("DATABASE_URL"))
    return connection

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    query = """CREATE TABLE game_progress(
    question_num SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    answered_at TIMESTAMP DEFAULT NOW()
    )"""

    cursor.execute('DROP TABLE IF EXISTS game_progress')
    cursor.execute(query)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Table Initialized.")

init_db()