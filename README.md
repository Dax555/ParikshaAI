ParikshaAI Online Exam Platform

CodeCraft is a full-stack web application designed to conduct online coding exams, specifically for shell scripting. It features an AI-powered grading system, anti-cheating measures, and a real-time dashboard for viewing results.

✨ Features

AI-Powered Grading: Automatically grades shell script submissions using the Google Gemini API, providing a score and feedback.

Real-time Timer: A countdown timer tracks the exam duration and auto-submits the answer when time runs out.

Anti-Cheating Measures: The exam auto-submits if a student switches browser tabs or minimizes the window.

Persistent Storage: Uses a SQLite database to reliably store student scores, handling simultaneous submissions gracefully.

Modern Frontend: A clean, responsive user interface built with Next.js and React, featuring a syntax-highlighted code editor.

Results Dashboard: A separate Streamlit dashboard to view all student scores and exam statistics in real-time.

🛠️ Tech Stack

Frontend:

Framework: Next.js (React)

Styling: Tailwind CSS

Code Editor: react-simple-code-editor with Prism.js for syntax highlighting

Backend:

Framework: FastAPI (Python)

Database: SQLite

AI Grading: Google Gemini API

Server: Uvicorn with Gunicorn for production

Dashboard:

Streamlit & Pandas

🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

Prerequisites

Node.js (v18.17 or later)

Python (v3.8 or later)

A Google Gemini API Key

1. Backend Setup

First, set up and start the Python backend server.

# 1. Navigate to the backend directory
cd backend

# 2. Create a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required Python libraries
pip install -r requirements.txt

# 4. Create an environment file
# Create a file named .env in the `backend` directory and add your API key:
# GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# 5. Run the backend server
# The server will run on [http://127.0.0.1:10000](http://127.0.0.1:10000)
uvicorn app.main:app --host 127.0.0.1 --port 10000 --reload


2. Frontend Setup

In a new terminal, set up and start the Next.js frontend.

# 1. Navigate to the frontend directory
cd frontend

# 2. Install the necessary npm packages
npm install

# 3. Run the development server
# The frontend will be available at http://localhost:3000
npm run dev


3. Usage

Open your browser and go to http://localhost:3000.

Enter your name and click "Start Exam".

The frontend will fetch a question from the backend and start the timer.

Write your code in the syntax-highlighted editor.

Click "Submit Final Answer" to have your code graded and the score saved to the SQLite database.

4. Viewing the Dashboard

To view the results stored in the database:

# 1. In your backend terminal (with the virtual environment active),
#    stop the main server (Ctrl+C).

# 2. Run the Streamlit dashboard app
streamlit run dashboard.py


This will open a new browser tab with the results dashboard.
