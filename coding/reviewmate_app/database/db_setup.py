
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "reviewmate.db")


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            choice_a TEXT NOT NULL,
            choice_b TEXT NOT NULL,
            choice_c TEXT NOT NULL,
            choice_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            date_taken TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")


if __name__ == "__main__":
    create_tables()