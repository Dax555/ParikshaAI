# from fastapi import FastAPI
# from app.services import question_bank, grading
# from pydantic import BaseModel
# import pandas as pd
# import os
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.services import question_bank, grading
# from pydantic import BaseModel
# import pandas as pd
# import os
# from typing import Optional
#
# # Using a relative path for the results file.
# EXCEL_PATH = "D:/testAI/results.xlsx"
#
# # Initialize Excel if not exists
# if not os.path.exists(EXCEL_PATH):
#     df = pd.DataFrame(columns=["Full Name", "Code Score"])
#     df.to_excel(EXCEL_PATH, index=False)
#
# app = FastAPI()
#
# # --- THE FIX IS HERE: Add CORS Middleware ---
# origins = [
#     "http://localhost:3000",  # The origin of your Next.js frontend
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"], # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"], # Allows all headers
# )
#
# # --- Pydantic Models ---
# class CodeSubmission(BaseModel):
#     full_name: str
#     code_answer: str
#     question: Optional[str] = None
#
# # --- API Endpoints ---
# @app.get("/")
# def root():
#     return {"message": "Exam backend running 🚀"}
#
# @app.post("/exam/generate")
# def generate_exam():
#     return question_bank.get_random_questions()
#
# @app.post("/exam/submit_code")
# def submit_code(submission: CodeSubmission):
#     # Pass the question to the grader for more accurate results
#     code_score = grading.grade_code(submission.code_answer, submission.question)
#
#     try:
#         # Check if file is empty or corrupted, create headers if needed
#         try:
#             df = pd.read_excel(EXCEL_PATH)
#             if "Full Name" not in df.columns or "Code Score" not in df.columns:
#                 df = pd.DataFrame(columns=["Full Name", "Code Score"])
#         except (pd.errors.EmptyDataError, FileNotFoundError):
#             df = pd.DataFrame(columns=["Full Name", "Code Score"])
#
#         # Update or add the new submission
#         if submission.full_name in df["Full Name"].values:
#             df.loc[df["Full Name"] == submission.full_name, "Code Score"] = code_score
#         else:
#             new_row = pd.DataFrame([{"Full Name": submission.full_name, "Code Score": code_score}])
#             df = pd.concat([df, new_row], ignore_index=True)
#
#         df.to_excel(EXCEL_PATH, index=False)
#     except Exception as e:
#         print(f"Error updating Excel file: {e}") # Log error for debugging
#
#     return {"message": "✅ Code submitted", "code_score": code_score}
#


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services import question_bank, grading
from pydantic import BaseModel
import sqlite3
from typing import Optional

# --- Configuration & Database Setup ---
DB_PATH = "exam_results.db"

def setup_database():
    """Initializes the database and creates the results table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL UNIQUE,
        code_score REAL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

# Run setup on application startup
setup_database()

app = FastAPI()

# --- THE FIX IS HERE: Add all possible frontend origins ---
origins = [
    "http://localhost:3000",      # For accessing from the same machine
    "http://10.1.89.131:10002",    # Alternative for localhost
    "http://192.168.1.162:3000",  # Your specific Network URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class CodeSubmission(BaseModel):
    full_name: str
    code_answer: str
    question: Optional[str] = None

# --- API Endpoints ---
@app.get("/")
def root():
    return {"message": "Exam backend running with SQLite 🚀"}

@app.post("/exam/generate")
def generate_exam():
    return question_bank.get_random_questions()

@app.post("/exam/submit_code")
def submit_code(submission: CodeSubmission):
    code_score = grading.grade_code(submission.code_answer, submission.question)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE results SET code_score = ? WHERE full_name = ?",
            (code_score, submission.full_name)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO results (full_name, code_score) VALUES (?, ?)",
                (submission.full_name, code_score)
            )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Error saving to database", "code_score": code_score}
    return {"message": "✅ Code submitted", "code_score": code_score}

