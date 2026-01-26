import streamlit as st
from auth import login

st.set_page_config(page_title="Login", layout="centered")

st.title("🔐 Login")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit:
    if login(username, password):
        st.success("✅ Login successful")
        st.switch_page("appv1.py")
    else:
        st.error("❌ Invalid credentials")
