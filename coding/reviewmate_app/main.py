
import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviewmate.db")

# DATABASE SETUP  

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

# DATABASE FUNCTIONS  

def get_connection():
    return sqlite3.connect(DB_PATH)


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

# GUI  

class ReviewMateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ReviewMate")
        self.geometry("420x360")
        self.resizable(False, False)

        tk.Label(self, text="ReviewMate", font=("Arial", 22, "bold")).pack(pady=(30, 5))
        tk.Label(self, text="Student Reviewer & Quiz Management",
                 font=("Arial", 11), fg="gray").pack(pady=(0, 25))

        ttk.Button(self, text="Add Subject", command=self.open_add_subject).pack(pady=8, padx=60, fill="x")
        ttk.Button(self, text="Add Question", command=self.open_add_question).pack(pady=8, padx=60, fill="x")
        ttk.Button(self, text="View Questions", command=self.open_view_questions).pack(pady=8, padx=60, fill="x")

    def open_add_subject(self):
        AddSubjectWindow(self)

    def open_add_question(self):
        AddQuestionWindow(self)

    def open_view_questions(self):
        ViewQuestionsWindow(self)


class AddSubjectWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Subject")
        self.geometry("300x160")
        self.grab_set()

        tk.Label(self, text="Subject Name:").pack(pady=(20, 5))
        self.entry = ttk.Entry(self, width=25)
        self.entry.pack(pady=5)

        ttk.Button(self, text="Save", command=self.save).pack(pady=15)

    def save(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Missing info", "Please enter a subject name.")
            return
        add_subject(name)
        messagebox.showinfo("Saved", f"Subject '{name}' added.")
        self.destroy()


class AddQuestionWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Question")
        self.geometry("400x520")
        self.grab_set()

        subjects = get_subjects()
        self.subject_map = {name: sid for sid, name in subjects}
        subject_names = list(self.subject_map.keys())

        tk.Label(self, text="Subject:").pack(pady=(15, 5))
        self.subject_var = tk.StringVar(value=subject_names[0] if subject_names else "")
        ttk.Combobox(self, textvariable=self.subject_var,
                     values=subject_names or ["Add a subject first"],
                     state="readonly", width=30).pack(pady=5)

        tk.Label(self, text="Question:").pack(pady=(15, 5))
        self.question_entry = ttk.Entry(self, width=45)
        self.question_entry.pack(pady=5)

        self.choice_entries = {}
        for label in ["A", "B", "C", "D"]:
            tk.Label(self, text=f"Choice {label}:").pack(pady=(8, 2))
            entry = ttk.Entry(self, width=45)
            entry.pack(pady=2)
            self.choice_entries[label] = entry

        tk.Label(self, text="Correct Answer (A/B/C/D):").pack(pady=(12, 5))
        self.correct_entry = ttk.Entry(self, width=10)
        self.correct_entry.pack(pady=5)

        ttk.Button(self, text="Save Question", command=self.save).pack(pady=20)

    def save(self):
        subject_name = self.subject_var.get()
        subject_id = self.subject_map.get(subject_name)
        question_text = self.question_entry.get().strip()
        choices = {k: v.get().strip() for k, v in self.choice_entries.items()}
        correct = self.correct_entry.get().strip().upper()

        if not subject_id:
            messagebox.showwarning("Missing info", "Please add a subject first.")
            return
        if not question_text or not all(choices.values()) or correct not in ["A", "B", "C", "D"]:
            messagebox.showwarning("Missing info", "Please fill in all fields, and set correct answer to A, B, C, or D.")
            return

        add_question(subject_id, question_text,
                      choices["A"], choices["B"], choices["C"], choices["D"], correct)
        messagebox.showinfo("Saved", "Question added successfully.")
        self.destroy()


class ViewQuestionsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("View Questions")
        self.geometry("450x420")
        self.grab_set()

        subjects = get_subjects()
        self.subject_map = {name: sid for sid, name in subjects}
        subject_names = list(self.subject_map.keys())

        tk.Label(self, text="Select Subject:").pack(pady=(15, 5))
        self.subject_var = tk.StringVar(value=subject_names[0] if subject_names else "")
        subject_menu = ttk.Combobox(self, textvariable=self.subject_var,
                                     values=subject_names or ["No subjects yet"],
                                     state="readonly", width=30)
        subject_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_list(self.subject_var.get()))
        subject_menu.pack(pady=5)

        container = tk.Frame(self)
        container.pack(pady=10, fill="both", expand=True, padx=10)

        canvas = tk.Canvas(container, width=400, height=290, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas)

        self.list_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if subject_names:
            self.refresh_list(self.subject_var.get())

    def refresh_list(self, subject_name):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        subject_id = self.subject_map.get(subject_name)
        if not subject_id:
            return

        questions = get_questions_by_subject(subject_id)
        if not questions:
            tk.Label(self.list_frame, text="No questions yet for this subject.").pack(pady=10)
            return

        for q in questions:
            row = tk.Frame(self.list_frame, relief="groove", bd=1)
            row.pack(pady=4, padx=4, fill="x")

            text = (f"Q: {q[2]}\n"
                    f"A) {q[3]}   B) {q[4]}   C) {q[5]}   D) {q[6]}\n"
                    f"Correct: {q[7]}")
            tk.Label(row, text=text, justify="left", anchor="w",
                     wraplength=320, padx=10, pady=8).pack(side="left", fill="x", expand=True)

            ttk.Button(row, text="Delete", command=lambda qid=q[0]: self.delete_question(qid)).pack(
                side="right", padx=8)

    def delete_question(self, question_id):
        if messagebox.askyesno("Confirm", "Delete this question?"):
            delete_question(question_id)
            self.refresh_list(self.subject_var.get())

# RUN THE APP

if __name__ == "__main__":
    create_tables()  # makes sure reviewmate.db and its tables exist
    app = ReviewMateApp()
    app.mainloop()
