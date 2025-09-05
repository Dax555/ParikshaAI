import streamlit as st

st.set_page_config(page_title="Exam Completed", page_icon="✅", layout="wide")

st.success("🎉 Thank You! Your submission has been recorded successfully.")
st.markdown("<h2 style='text-align: center;'>The exam is now complete. You may close this window.</h2>", unsafe_allow_html=True)
st.balloons()
