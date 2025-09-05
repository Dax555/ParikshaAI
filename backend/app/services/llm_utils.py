import os
import google.generativeai as genai

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyCFEeEf9aWPfahv_TZiWbWwFuzg_-cffHg"
if not GEMINI_API_KEY:
    raise ValueError("Set GEMINI_API_KEY in environment variables or directly in the code.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text if response and response.text else ""
