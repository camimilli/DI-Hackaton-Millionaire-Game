import os
import psycopg2
from psycopg2.extras import RealDictCursor

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
        money INTEGER NOT NULL
    );
    """)
    connection.commit()
    print("Table Initialized.")

def log_answer(question, user_answer, correct_answer, money):
    """Logs the question, user answer, correct answer, and money value into the database """
    query = """
    INSERT INTO game_progress(question, user_answer, correct_answer, money)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (question, user_answer, correct_answer, money))
    connection.commit()

def fetch_progress():
    cursor.execute('SELECT * FROM game_progress')

    rows = cursor.fetchall()
    for row in rows:
        print(
            f"| Question Number: {row['question_num']} | "
            f"Question: {row['question']} | "
            f"User Answer: {row['user_answer']} | "
            f"Correct Answer: {row['correct_answer']} | "
            f"Money: {row['money']} | "
        )