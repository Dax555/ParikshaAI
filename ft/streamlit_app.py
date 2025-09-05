import streamlit as st
import requests
import time
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:10000"  # Ensure this matches your backend port
GENERATE_URL = f"{BACKEND_URL}/exam/generate"
SUBMIT_CODE_URL = f"{BACKEND_URL}/exam/submit_code"
EXAM_DURATION_SECONDS = 600  # 10 minutes

# --- Page Setup ---
st.set_page_config(
    page_title="CodeCraft | Online Exam",
    page_icon="⚡",
    layout="wide"
)

# --- Custom CSS ---
def load_css():
    st.markdown("""
    <style>
        body { background-color: #f0f2f6; }
        .main .block-container { padding: 2rem; }
        .st-emotion-cache-1r6slb0 {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .stButton>button[kind="primary"] {
            background-color: #2c3e50;
            color: white;
            border-radius: 8px;
            border: 2px solid #2c3e50;
            padding: 10px 24px;
            font-weight: bold;
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #1abc9c;
            border-color: #1abc9c;
        }
        .st-emotion-cache-1b0udgb {
            font-size: 2.75rem;
            color: #1abc9c;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Session State ---
st.session_state.setdefault("started", False)
st.session_state.setdefault("question", "Loading question...")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("time_left", EXAM_DURATION_SECONDS)
st.session_state.setdefault("start_time", None)
st.session_state.setdefault("submitted", False)
st.session_state.setdefault("full_name", "")
st.session_state.setdefault("submission_triggered", False)
st.session_state.setdefault("disable_submit", False)  # ✅ disable submit button
st.session_state.setdefault("disable_start", False)   # ✅ disable start button

# --- Submission Logic ---
def submit_answer(reason=""):
    if st.session_state.submission_triggered:
        return

    st.session_state.submission_triggered = True
    st.session_state.disable_submit = True  # ✅ disable submit button once pressed

    if reason == "tab_switch":
        st.error("❌ Tab switched! To prevent cheating, your answer is being automatically submitted.")
        time.sleep(2)
    elif reason == "time_up":
        st.warning("⏰ Time is up! Auto-submitting your answer...")
        time.sleep(2)

    with st.spinner("Submitting your answer..."):
        try:
            payload = {
                "full_name": st.session_state.full_name,
                "code_answer": st.session_state.answer,
                "question": st.session_state.question
            }
            res = requests.post(SUBMIT_CODE_URL, json=payload)
            res.raise_for_status()
            st.session_state.submitted = True
            st.rerun()   # ✅ Immediately redirect to thank you page with balloons
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Submission failed: {e}")
            st.session_state.submission_triggered = False
            st.session_state.disable_submit = False  # re-enable if failed

# --- Main Title ---
st.title("⚡ CodeCraft Online Exam")
st.markdown("<h3 style='text-align: center; color: #555;'>Assess Your Shell Scripting Skills</h3>", unsafe_allow_html=True)
st.divider()

# --- Thank You Page ---
if st.session_state.submitted:
    with st.container():
        st.success("🎉 Thank You! Your submission has been recorded successfully.")
        st.markdown("<h2 style='text-align: center;'>The exam is now complete. You may close this window.</h2>", unsafe_allow_html=True)
        st.balloons()
    st.stop()

# --- Start Screen ---
if not st.session_state.started:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        with st.container():
            st.markdown("<h2 style='text-align: center;'>Welcome to the Exam</h2>", unsafe_allow_html=True)
            st.info("Please enter your full name and click 'Start Exam' to begin. You will have 10 minutes to complete the challenge.", icon="👋")
            full_name = st.text_input("Enter your full name:", placeholder="e.g., Ada Lovelace")

            if st.button("Start Exam",
                         type="primary",
                         use_container_width=True,
                         disabled=st.session_state.disable_start):  # ✅ disable start button
                if not full_name.strip():
                    st.error("Please enter your name before starting.")
                else:
                    st.session_state.disable_start = True  # ✅ disable after click
                    st.session_state.full_name = full_name.strip()
                    with st.spinner("Generating your question..."):
                        try:
                            res = requests.post(GENERATE_URL)
                            res.raise_for_status()
                            data = res.json()
                            st.session_state.question = data.get("code_question", "⚠️ No question received.")
                            st.session_state.started = True
                            st.session_state.start_time = time.time()
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"⚠️ Connection Error: Could not connect to the backend. {e}")
                            st.session_state.disable_start = False  # re-enable if failed
    st.stop()

# --- Timer Logic ---
if st.session_state.start_time:
    elapsed = int(time.time() - st.session_state.start_time)
    st.session_state.time_left = max(EXAM_DURATION_SECONDS - elapsed, 0)

st_autorefresh(interval=1000, key="timer_refresh")

# --- Tab Switch Detection ---
cheat_detection_component = st.components.v1.html(
    """<script>
    if (!window.visibilityListenerAttached) {
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') {
                window.parent.postMessage({
                    isStreamlitMessage: true, type: 'SET_COMPONENT_VALUE',
                    data: { "tab_switched": true }
                }, '*');
            }
        });
        window.visibilityListenerAttached = true;
    }
    </script>""", height=0,
)

if isinstance(cheat_detection_component, dict) and cheat_detection_component.get("tab_switched"):
    submit_answer(reason="tab_switch")

if st.session_state.time_left <= 0:
    submit_answer(reason="time_up")

# --- Main Exam Layout ---
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    with st.container():
        st.markdown("### 📝 Your Solution")
        st.caption(f"Candidate: **{st.session_state.full_name}**")

        st.session_state.answer = st.text_area(
            "Write your shell script here:",
            value=st.session_state.answer,
            height=400,
            placeholder="Enter your shell script code here...",
            label_visibility="collapsed"
        )

        if st.button("Submit Final Answer",
                     type="primary",
                     use_container_width=True,
                     disabled=st.session_state.disable_submit):  # ✅ disable submit button
            submit_answer(reason="manual")

with col2:
    with st.container():
        st.markdown("### ⏳ Status & Timer")
        mins, secs = divmod(st.session_state.time_left, 60)
        st.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
        st.progress((EXAM_DURATION_SECONDS - st.session_state.time_left) / EXAM_DURATION_SECONDS)

    st.write("")

    with st.container():
        st.markdown("### 🎯 Problem Description")
        st.info(st.session_state.question, icon="📌")


