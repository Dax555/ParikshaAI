import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Configuration ---
DB_PATH = "D:/testAI/backend/exam_results.db"  # Assumes the DB is in the same folder as this script

# --- Page Setup ---
st.set_page_config(
    page_title="Exam Results Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Exam Results Dashboard")
st.markdown("This dashboard displays the results from the CodeCraft Online Exam.")


# --- Database Connection ---
def fetch_data():
    """Connects to the SQLite database and fetches all results."""
    if not os.path.exists(DB_PATH):
        st.error(
            f"Database file not found at '{DB_PATH}'. Please make sure the backend has run and created the database.")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        # Use pandas to easily read the SQL query into a DataFrame
        df = pd.read_sql_query("SELECT full_name, code_score FROM results ORDER BY code_score DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"An error occurred while connecting to the database: {e}")
        return None


# --- Main Dashboard ---
data = fetch_data()

if data is not None:
    if st.button("🔄 Refresh Data"):
        st.rerun()

    st.divider()

    # --- Key Metrics ---
    col1, col2, col3 = st.columns(3)
    total_submissions = len(data)
    average_score = data['code_score'].mean() if not data.empty else 0
    highest_score = data['code_score'].max() if not data.empty else 0

    col1.metric("Total Submissions", f"{total_submissions} 🧑‍🎓")
    col2.metric("Average Score", f"{average_score:.2f} / 3.0")
    col3.metric("Highest Score", f"{highest_score:.2f} ⭐")

    st.divider()

    # --- Data Table and Chart ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 All Submissions")
        # Display the dataframe with an interactive table
        st.dataframe(data, use_container_width=True, height=500)

    with col2:
        st.markdown("### 📈 Score Distribution")
        if not data.empty:
            # Create a simple bar chart of scores
            st.bar_chart(data.set_index('full_name')['code_score'])
        else:
            st.info("No data available to display chart.")

else:
    st.warning("Could not load data to display the dashboard.")