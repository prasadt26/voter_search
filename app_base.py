import streamlit as st
import json
import tempfile
from parser2 import parse_voter_txt

st.set_page_config(page_title="Voter Search App", layout="wide")

st.title("🗳️ Voter List Ingestion")

uploaded_file = st.file_uploader("Upload voter TXT file", type=["txt"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    voters = parse_voter_txt(tmp_path)

    st.success(f"Loaded {len(voters)} voter records")

    search = st.text_input("🔍 Search by Name / EPIC / Door No / Relation")

    if search:
        results = [
            v for v in voters
            if search.lower() in json.dumps(v).lower()
        ]
    else:
        results = voters

    st.write(f"Showing {len(results)} records")

    for v in results:
        with st.expander(f"{v.get('name')} ({v.get('epic_no')})"):
            st.json(v)

    # Download JSON
    st.download_button(
        label="⬇️ Download JSON",
        data=json.dumps(voters, indent=2, ensure_ascii=False),
        file_name="voters.json",
        mime="application/json"
    )
