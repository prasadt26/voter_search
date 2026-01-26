import streamlit as st
import json
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
DATA_FILE = Path("voters_32.json")

st.set_page_config(
    page_title="Voter Search",
    layout="wide"
)

st.title("🗳️ Voter Search")

# -------------------------------
# LOAD JSON
# -------------------------------
if not DATA_FILE.exists():
    st.error("❌ voters.json not found")
    st.stop()

@st.cache_data(show_spinner=True)
def load_voters():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

voters = load_voters()
st.caption(f"📂 {len(voters)} records loaded")

# -------------------------------
# SEARCH (SINGLE INPUT)
# -------------------------------
query = st.text_input(
    "🔍 Search by Name / EPIC / Door / Relation",
    placeholder="Type anything…"
)

# -------------------------------
# APPLY SEARCH
# -------------------------------
results = voters

if query:
    q = query.lower()
    results = [
        v for v in voters
        if q in (
            f"{v.get('record_serial', '')} "
            f"{v.get('name','')} "
            f"{v.get('epic_no','')} "
            f"{v.get('door_no','')} "
            f"{v.get('relation_name','')}"
        ).lower()
    ]

st.subheader(f"📊 {len(results)} result(s)")

# -------------------------------
# RESULTS — NATIVE CARD UI
# -------------------------------
if query != "":

    for v in results:
        with st.container(border=True):

            # NAME
            st.markdown(f"### {v.get('name', 'N/A')}")

            # META ROW
            col1, col2, col3 , col4 = st.columns(4)
            col1.metric("Age", v.get("age", "N/A"))
            col2.metric("Sex", v.get("sex", "N/A"))
            col3.metric("EPIC", v.get("epic_no", "N/A"))
            col4.metric("Serial", v.get("record_serial", "N/A"))
            # DETAILS (COMPACT)
            st.write(
                f"👨‍👩‍👧 **{v.get('relation_type','Relation')}**: {v.get('relation_name','N/A')}"
            )
            st.write(f"🏠 **Door No:** {v.get('door_no','N/A')}")
            st.write(
                f"🗺️ **AC / PS / SL:** "
                f"{v.get('ac_no','-')} / {v.get('ps_no','-')} / {v.get('sl_no','-')}"
            )
