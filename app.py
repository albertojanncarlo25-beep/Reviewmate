"""
ReviewMate - Streamlit version (reference only).
Run with: streamlit run app.py

NOTE: This runs in a web browser, not as a desktop window.
If your professor requires a desktop app, use the Tkinter version instead.
"""
import sqlite3
import os
import streamlit as st
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviewmate.db")


# ----------------------- DATABASE -----------------------

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_tables():
    conn = get_connection()
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


def add_subject(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def get_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE subject_id = ?", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_question(question_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


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


# ----------------------- APP -----------------------

st.set_page_config(page_title="ReviewMate", page_icon="📚")
create_tables()

st.title("📚 ReviewMate")
st.caption("Student Reviewer & Quiz Management System")

page = st.sidebar.radio(
    "Menu",
    ["Add Subject", "Add Question", "View Questions", "Take Quiz", "Review History"]
)

# ---------- Add Subject ----------
if page == "Add Subject":
    st.header("Add Subject")
    name = st.text_input("Subject Name")
    if st.button("Save Subject"):
        if name.strip():
            add_subject(name.strip())
            st.success(f"Subject '{name}' added.")
        else:
            st.warning("Please enter a subject name.")

# ---------- Add Question ----------
elif page == "Add Question":
    st.header("Add Question")
    subjects = get_subjects()
    subject_map = {sname: sid for sid, sname in subjects}

    if not subject_map:
        st.warning("Please add a subject first.")
    else:
        subject_name = st.selectbox("Subject", list(subject_map.keys()))
        question_text = st.text_input("Question")
        choice_a = st.text_input("Choice A")
        choice_b = st.text_input("Choice B")
        choice_c = st.text_input("Choice C")
        choice_d = st.text_input("Choice D")
        correct = st.selectbox("Correct Answer", ["A", "B", "C", "D"])

        if st.button("Save Question"):
            if question_text and choice_a and choice_b and choice_c and choice_d:
                add_question(subject_map[subject_name], question_text,
                             choice_a, choice_b, choice_c, choice_d, correct)
                st.success("Question added successfully.")
            else:
                st.warning("Please fill in all fields.")

# ---------- View Questions ----------
elif page == "View Questions":
    st.header("View Questions")
    subjects = get_subjects()
    subject_map = {sname: sid for sid, sname in subjects}

    if not subject_map:
        st.info("No subjects yet.")
    else:
        subject_name = st.selectbox("Select Subject", list(subject_map.keys()))
        questions = get_questions_by_subject(subject_map[subject_name])

        if not questions:
            st.info("No questions yet for this subject.")
        else:
            for q in questions:
                with st.container(border=True):
                    st.markdown(f"**Q: {q[2]}**")
                    st.write(f"A) {q[3]}  B) {q[4]}  C) {q[5]}  D) {q[6]}")
                    st.write(f"Correct: {q[7]}")
                    if st.button("Delete", key=f"del_{q[0]}"):
                        delete_question(q[0])
                        st.rerun()

# ---------- Take Quiz ----------
elif page == "Take Quiz":
    st.header("Take Quiz")
    subjects = get_subjects()
    subject_map = {sname: sid for sid, sname in subjects}

    if not subject_map:
        st.warning("Please add a subject first.")
    else:
        subject_name = st.selectbox("Choose a subject", list(subject_map.keys()))
        subject_id = subject_map[subject_name]

        # Start a new quiz when the button is clicked
        if st.button("Start Quiz"):
            questions = get_questions_by_subject(subject_id)
            if not questions:
                st.warning("This subject has no questions yet.")
            else:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_subject_id = subject_id
                st.session_state.quiz_submitted = False

        if "quiz_questions" in st.session_state and not st.session_state.get("quiz_submitted", False) \
                and st.session_state.get("quiz_subject_id") == subject_id:

            questions = st.session_state.quiz_questions
            st.write(f"**{len(questions)} question(s)** — answer all, then submit.")

            answers = {}
            with st.form("quiz_form"):
                for i, q in enumerate(questions):
                    # q = (id, subject_id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer)
                    st.markdown(f"**{i + 1}. {q[2]}**")
                    choice_labels = {"A": q[3], "B": q[4], "C": q[5], "D": q[6]}
                    choice = st.radio(
                        "Select an answer",
                        options=["A", "B", "C", "D"],
                        format_func=lambda letter, labels=choice_labels: f"{letter}) {labels[letter]}",
                        key=f"q_{q[0]}",
                        label_visibility="collapsed",
                    )
                    answers[q[0]] = choice
                submitted = st.form_submit_button("Submit Quiz")

            if submitted:
                score = 0
                results = []
                for q in questions:
                    chosen = answers[q[0]]
                    correct = q[7]
                    is_correct = (chosen == correct)
                    if is_correct:
                        score += 1
                    results.append((q[2], chosen, correct, is_correct))

                save_attempt(subject_id, score, len(questions),
                             datetime.now().strftime("%Y-%m-%d %H:%M"))

                st.session_state.quiz_submitted = True
                st.success(f"Score: {score} / {len(questions)}")

                for text, chosen, correct, is_correct in results:
                    with st.container(border=True):
                        st.markdown(f"**Q: {text}**")
                        if is_correct:
                            st.markdown(f"✅ Your answer: {chosen} (Correct)")
                        else:
                            st.markdown(f"❌ Your answer: {chosen} — Correct answer: {correct}")

# ---------- Review History ----------
elif page == "Review History":
    st.header("Review Previous Attempts")
    subjects = get_subjects()
    subject_map = {sname: sid for sid, sname in subjects}

    if not subject_map:
        st.info("No subjects yet.")
    else:
        subject_name = st.selectbox("Select Subject", list(subject_map.keys()), key="history_subject")
        attempts = get_attempts_by_subject(subject_map[subject_name])

        if not attempts:
            st.info("No quiz attempts yet for this subject.")
        else:
            for a in attempts:
                # a = (id, subject_id, score, total_questions, date_taken)
                with st.container(border=True):
                    st.write(f"**Score:** {a[2]} / {a[3]}")
                    st.caption(f"Taken on {a[4]}")