
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "reviewmate.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------- Subjects ----------

def add_subject(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # subject already exists
    conn.close()


def get_subjects():
    """Returns a list of (id, name) tuples."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------- Questions ----------

def add_question(subject_id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions
            (subject_id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (subject_id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer))
    conn.commit()
    conn.close()


def get_questions_by_subject(subject_id):
    """Returns full rows: (id, subject_id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE subject_id = ?", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------- Quiz attempts (for later: scoring + history features) ----------

def save_attempt(subject_id, score, total_questions, date_taken):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_attempts (subject_id, score, total_questions, date_taken)
        VALUES (?, ?, ?, ?)
    """, (subject_id, score, total_questions, date_taken))
    conn.commit()
    conn.close()


def get_attempts_by_subject(subject_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_attempts WHERE subject_id = ? ORDER BY date_taken DESC", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows