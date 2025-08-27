import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
cursor = connection.cursor()

def init_db():
    """Initializes the game_progress table if it doesn't exist."""
    cursor.execute("""
    DROP TABLE IF EXISTS game_progress;
    CREATE TABLE game_progress(
        question_num SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        user_answer TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        money INTEGER NOT NULL,
        answered_at TIMESTAMP DEFAULT NOW()
    );
    """)
    connection.commit()
    print("Table Initialized.")

def log_answer(question, user_answer, correct_answer, money):
    """Logs the question, user answer, correct answer, and money value."""
    query = """
    INSERT INTO game_progress(question, user_answer, correct_answer, money)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (question, user_answer, correct_answer, money))
    connection.commit()

# def fetch_progress(cursor):
#     pass
