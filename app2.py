import streamlit as st
import json
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
DATA_FILE = Path("voters.json")

st.set_page_config(
    page_title="Voter Search",
    layout="wide"
)

st.title("🗳️ Voter Search")

# -------------------------------
# LOAD JSON
# -------------------------------
if not DATA_FILE.exists():
    st.error("❌ voters.json not found in application directory")
    st.stop()

@st.cache_data(show_spinner=True)
def load_voters():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

voters = load_voters()

st.success(f"Loaded {len(voters)} voter records")

# -------------------------------
# SEARCH CONTROLS
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    query = st.text_input(
        "🔍 Search (Name / EPIC / Door / Relation)"
    )

with col2:
    sex_filter = st.selectbox(
        "Sex",
        ["All", "M", "F"]
    )

with col3:
    age_min = st.number_input(
        "Minimum Age",
        min_value=0,
        max_value=120,
        value=0
    )

# -------------------------------
# APPLY SEARCH
# -------------------------------
results = voters

if query:
    q = query.lower()
    results = [
        v for v in results
        if q in (
            f"{v.get('name','')} "
            f"{v.get('epic_no','')} "
            f"{v.get('door_no','')} "
            f"{v.get('relation_name','')}"
        ).lower()
    ]

if sex_filter != "All":
    results = [
        v for v in results
        if v.get("sex") == sex_filter
    ]

results = [
    v for v in results
    if v.get("age", 0) >= age_min
]

# -------------------------------
# RESULTS
# -------------------------------
st.markdown(f"### 📊 Results: **{len(results)}** records")

for v in results:
    with st.container():
        st.markdown(
            f"""
            <div style="
                border:1px solid #ddd;
                border-radius:10px;
                padding:14px;
                margin-bottom:10px;
                background-color:#ffffff;
            ">
                <h4 style="margin-bottom:5px;">{v.get('name', 'N/A')}</h4>
                <b>EPIC:</b> {v.get('epic_no', 'N/A')} &nbsp; | &nbsp;
                <b>Age:</b> {v.get('age', 'N/A')} &nbsp; | &nbsp;
                <b>Sex:</b> {v.get('sex', 'N/A')}<br>
                <b>Relation:</b> {v.get('relation_type', '')} {v.get('relation_name', '')}<br>
                <b>Door No:</b> {v.get('door_no', 'N/A')}<br>
                <b>AC / PS / SL:</b> {v.get('ac_no')} / {v.get('ps_no')} / {v.get('sl_no')}
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📄 Full Details"):
            st.json(v)
