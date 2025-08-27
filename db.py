import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection  = psycopg2.connect(os.getenv("DATABASE_URL"))
    return connection

def init_db():
    '''Initializes a new progress table for a game of "Who Wants to be a Millionare?!'''
    connection = get_connection()
    cursor = connection.cursor()

    query = """CREATE TABLE game_progress(
    question_num SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    money INTEGER NOT NULL,
    answered_at TIMESTAMP DEFAULT NOW()
    )"""

    cursor.execute('DROP TABLE IF EXISTS game_progress')
    cursor.execute(query)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Table Initialized.")

def log_answer(question, user_answer, correct_answer, money):
    """Logs the question, answer and user response to the progress table"""
    connection = get_connection()
    cursor = connection.cursor()

    query = f"""INSERT INTO game_progress(question, user_answer, correct_answer, money) VALUES
    ('{question}', '{user_answer}', '{correct_answer}', '{money}')"""

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


log_answer("What is your name?", "Niv", "Jesus", 100)