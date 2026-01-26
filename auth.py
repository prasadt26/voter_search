import streamlit as st
import json
from pathlib import Path

USERS_FILE = Path("users.json")

def load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def login(username, password):
    users = load_users()
    if users.get(username) == password:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    st.session_state.clear()

def is_authenticated():
    return st.session_state.get("authenticated", False)
