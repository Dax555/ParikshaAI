import os
import re
import json
import logging
from typing import Optional
from dotenv import load_dotenv

# FIXED: Using a relative path for the .env file.
# This assumes your .env file is in the root directory of your backend project.
load_dotenv("D:/testAI/backend/app/.env")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===== Config =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

CODE_MAX = 3.0

# Initialize Gemini model
_MODEL = None
if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)
        logger.info("✅ Gemini model initialized successfully for grading.")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize Gemini: {e}")
        _MODEL = None
else:
    if not GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY not set in .env file. Using heuristic grading fallback.")
    if not genai:
        logger.warning("⚠️ 'google-generativeai' not installed. Using heuristic grading fallback.")

# ===== Helper Functions =====
def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _round_quarter(x: float) -> float:
    return round(round(x * 4) / 4, 2)

def _parse_json_maybe(text: str) -> Optional[dict]:
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", s, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None

def _call_gemini(prompt: str) -> Optional[dict]:
    if not _MODEL:
        return None
    try:
        resp = _MODEL.generate_content(prompt)
        text = getattr(resp, "text", "") or ""
        return _parse_json_maybe(text)
    except Exception as e:
        logger.error(f"❌ Gemini API call failed: {e}")
        return None

# ===== Heuristic Fallback (if Gemini fails) =====
def _heuristic_score_code(answer: str, max_marks: float) -> float:
    logger.info("Using heuristic fallback for code grading.")
    if not answer or not answer.strip():
        return 0.0
    score = 0.5
    if "#!/bin/bash" in answer: score += 0.5
    if re.search(r"\b(find|grep|awk|sed|ps|sort)\b", answer): score += 0.5
    if re.search(r"\b(for|while|if)\b", answer): score += 0.5
    if re.search(r"set -[euo]", answer): score += 0.25
    if re.search(r"\[\[.*\]\]", answer): score += 0.25
    return _clamp(_round_quarter(score), 0.0, max_marks)

# ===== Public API (used by the main FastAPI route) =====
def grade_code(code_answer: str, question: Optional[str] = None) -> float:
    max_marks = CODE_MAX
    prompt = f"""
You are an expert examiner grading a shell-scripting exam question.

The Question:
{question or "A standard shell scripting task involving file operations, process management, or text manipulation."}

The Student's Submitted Answer:
```bash
{code_answer}
```

Please grade the answer based on the following rubric:
- Correctness: Does the script achieve the goal?
- Best Practices: Does it use quotes correctly? Does it handle potential errors?
- Efficiency: Is the use of commands and pipelines logical?

Return your response in JSON format ONLY, with no other text or code fences. The JSON must have this exact schema:
{{
  "marks": <a number between 0.0 and {max_marks}, in increments of 0.25>,
  "feedback": "<A concise, one-sentence feedback for the student.>"
}}
"""
    data = _call_gemini(prompt)
    if data and "marks" in data:
        try:
            marks = float(data["marks"])
            logger.info(f"Gemini graded with score: {marks}. Feedback: {data.get('feedback', 'N/A')}")
            return _clamp(_round_quarter(marks), 0.0, max_marks)
        except (ValueError, TypeError):
            logger.warning("Gemini returned invalid marks. Falling back to heuristic grading.")
            pass

    return _heuristic_score_code(code_answer, max_marks)
