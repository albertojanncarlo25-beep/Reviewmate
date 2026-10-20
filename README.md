# 📚 ReviewMate

ReviewMate is a Student Reviewer and Quiz Management System built with
Python and Streamlit. Students can create question sets, take practice
quizzes, get their scores automatically, and review their past attempts.

## ✨ Features

- 👤 Simple name-based login (no password needed)
- 🏠 Dashboard with totals for subjects, quizzes, questions, attempts, and users
- ➕ Create questions in three types:
  - Multiple Choice
  - Identification (case-insensitive checking)
  - Enumeration (order doesn't matter)
- 📝 Take quizzes by subject and quiz name, with automatic scoring
- 🔎 Answer review showing your answer vs. the correct answer
- 📋 Question Sets: view questions grouped by quiz, and delete questions
- 📊 Quiz History of all previous attempts
- 👥 Users page showing who is active and how many quizzes each took

## 🛠️ Tech Stack

- Python 3
- Streamlit (user interface)
- SQLite (database, created automatically as `reviewmate.db`)

## 🚀 Installation

1. Clone the repository:
```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
```
2. Install the requirements:
```bash
   pip install -r requirements.txt
```
3. Run the app:
```bash
   streamlit run app.py
```
4. Open the link shown in the terminal (usually http://localhost:8501).

## 📖 How to Use

1. Enter your name to open ReviewMate.
2. Go to **Create Question** and add questions under a subject and quiz name.
3. Go to **Take Quiz**, pick a subject and quiz, then press **Start Quiz**.
4. Submit your answers to see your score and the answer review.
5. Check **Quiz History** and **Users** anytime.

## 📁 Project Structure
ReviewMate/
├── app.py            # Main application
├── requirements.txt  # Dependencies
├── reviewmate.db     # SQLite database (auto-created)
└── README.md
