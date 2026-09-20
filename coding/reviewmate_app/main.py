
import tkinter as tk
from tkinter import ttk, messagebox
from database import db_helper


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
        db_helper.add_subject(name)
        messagebox.showinfo("Saved", f"Subject '{name}' added.")
        self.destroy()


class AddQuestionWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Question")
        self.geometry("400x520")
        self.grab_set()

        subjects = db_helper.get_subjects()
        self.subject_map = {name: sid for sid, name in subjects}
        subject_names = list(self.subject_map.keys())

        tk.Label(self, text="Subject:").pack(pady=(15, 5))
        self.subject_var = tk.StringVar(value=subject_names[0] if subject_names else "")
        subject_menu = ttk.Combobox(self, textvariable=self.subject_var,
                                     values=subject_names or ["Add a subject first"],
                                     state="readonly", width=30)
        subject_menu.pack(pady=5)

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

        db_helper.add_question(subject_id, question_text,
                                choices["A"], choices["B"], choices["C"], choices["D"], correct)
        messagebox.showinfo("Saved", "Question added successfully.")
        self.destroy()


class ViewQuestionsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("View Questions")
        self.geometry("450x420")
        self.grab_set()

        subjects = db_helper.get_subjects()
        self.subject_map = {name: sid for sid, name in subjects}
        subject_names = list(self.subject_map.keys())

        tk.Label(self, text="Select Subject:").pack(pady=(15, 5))
        self.subject_var = tk.StringVar(value=subject_names[0] if subject_names else "")
        subject_menu = ttk.Combobox(self, textvariable=self.subject_var,
                                     values=subject_names or ["No subjects yet"],
                                     state="readonly", width=30)
        subject_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_list(self.subject_var.get()))
        subject_menu.pack(pady=5)

        # Scrollable area built 
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

        questions = db_helper.get_questions_by_subject(subject_id)
        if not questions:
            tk.Label(self.list_frame, text="No questions yet for this subject.").pack(pady=10)
            return

        for q in questions:
            text = (f"Q: {q[2]}\n"
                    f"A) {q[3]}   B) {q[4]}   C) {q[5]}   D) {q[6]}\n"
                    f"Correct: {q[7]}")
            tk.Label(self.list_frame, text=text, justify="left", anchor="w",
                     wraplength=370, padx=10, pady=8, relief="groove", bd=1).pack(
                pady=4, padx=4, fill="x")


if __name__ == "__main__":
    app = ReviewMateApp()
    app.mainloop()
