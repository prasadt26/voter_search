import streamlit as st
import json
from pathlib import Path
import pandas as pd
# -------------------------------
# AUTH CONFIG (FROM users.json)
# -------------------------------
USERS_FILE = Path("users.json")
def save_voters(file_path, voters):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(voters, f, ensure_ascii=False, indent=2)
    st.cache_data.clear()


def contact_exists(voters, contact, current_epic):
    for v in voters:
        if (
            v.get("contact") == contact
            and v.get("epic_no") != current_epic
        ):
            return True
    return False

def load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def is_authenticated():
    return st.session_state.get("authenticated", False)

def login(username, password):
    users = load_users()
    user = users.get(username)

    if user and user.get("password") == password:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["divisions"] = user.get("divisions")
        return True

    return False


def logout():
    st.cache_data.clear()
    st.session_state.clear()


# -------------------------------
# LOGIN PAGE
# -------------------------------
if not is_authenticated():
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Voter Search Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if login(username, password):
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

# -------------------------------
# MAIN APP (YOUR CODE)
# -------------------------------

# CONFIG
# DATA_FILE = Path("voters_32.json")
# st.sidebar.header("📍 Division Selection")

allowed_divisions = st.session_state.get("divisions")

if allowed_divisions == "ALL":
    division_options = [f"Division-{i}" for i in range(1, 61)]
else:
    division_options = [f"Division-{i}" for i in allowed_divisions]

# division = st.sidebar.selectbox(
#     "Select Division",
#     options=division_options
# )
st.subheader("📍 Select Division")

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    division = st.selectbox(
        "Division",
        options=division_options,
        label_visibility="collapsed"
    )

division_number = division.split("-")[1]

DATA_FILE = Path("data") / f"division_{division_number}.json"

st.set_page_config(
    page_title="Voter Search",
    layout="wide"
)

# HEADER + LOGOUT
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.title("🗳️ Voter Search")
with col_logout:
    st.write("")
    if st.button("🚪 Logout"):
        logout()
        st.rerun()

# -------------------------------
# LOAD JSON
# -------------------------------
if not DATA_FILE.exists():
    st.error("❌ voters.json not found")
    st.stop()

# @st.cache_data(show_spinner=True)
# def load_voters():
#     with open(DATA_FILE, "r", encoding="utf-8") as f:
#         return json.load(f)
#
# voters = load_voters()
# st.caption(f"📂 {len(voters)} records loaded")
@st.cache_data(show_spinner=True)
def load_voters(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

if not DATA_FILE.exists():
    st.error(f"❌ No data found for {division}")
    st.stop()

voters = load_voters(DATA_FILE)
st.caption(f"📂 {division} • {len(voters)} records loaded")

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

st.subheader(f"📊 {len(results)} Voter(s)")

# -------------------------------
# RESULTS — NATIVE CARD UI
# -------------------------------
if query != "":
    for v in results:
        with st.container(border=True):

            st.markdown(f"### {v.get('name', 'N/A')}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Age", v.get("age", "N/A"))
            col2.metric("Sex", v.get("sex", "N/A"))
            col3.metric("EPIC", v.get("epic_no", "N/A"))
            col4.metric("Serial", v.get("record_serial", "N/A"))

            st.write(
                f"👨‍👩‍👧 **{v.get('relation_type','Relation')}**: {v.get('relation_name','N/A')}"
            )
            st.write(f"🏠 **Door No:** {v.get('door_no','N/A')}")
            st.write(
                f"🗺️ **AC / PS / SL:** "
                f"{v.get('ac_no','-')} / {v.get('ps_no','-')} / {v.get('sl_no','-')}"
            )
            # -------------------------------
            # CONTACT SECTION (ADD / UPDATE)
            # -------------------------------
            contact_key = f"contact_edit_{v.get('epic_no')}"
            existing_contact = v.get("contact")

            st.divider()
            st.markdown("📞 **Contact Information**")

            # Initialize edit mode flag
            if contact_key not in st.session_state:
                st.session_state[contact_key] = False

            # ---------- CONTACT EXISTS ----------
            if existing_contact and not st.session_state[contact_key]:

                col_val, col_btn = st.columns([3, 1])

                with col_val:
                    st.text_input(
                        "Contact Number",
                        value=existing_contact,
                        disabled=True,
                        key=f"view_{v.get('epic_no')}"
                    )

                with col_btn:
                    if st.button("✏️ Update", key=f"update_{v.get('epic_no')}"):
                        st.session_state[contact_key] = True
                        st.rerun()

            # ---------- ADD / EDIT MODE ----------
            else:
                contact_input = st.text_input(
                    "Contact Number",
                    value=existing_contact or "",
                    placeholder="Enter 10-digit mobile number",
                    key=f"edit_{v.get('epic_no')}"
                )

                col_save, col_cancel = st.columns([1, 1])

                with col_save:
                    if st.button("💾 Save", key=f"save_{v.get('epic_no')}"):

                        if not contact_input.strip():
                            st.warning("⚠️ Contact cannot be empty")

                        elif contact_exists(voters, contact_input, v.get("epic_no")):
                            st.error("❌ This contact number already exists for another voter")

                        else:
                            for voter in voters:
                                if voter.get("epic_no") == v.get("epic_no"):
                                    voter["contact"] = contact_input
                                    break

                            save_voters(DATA_FILE, voters)
                            st.session_state[contact_key] = False
                            st.success("✅ Contact saved successfully")
                            st.rerun()

                with col_cancel:
                    if existing_contact and st.button("❌ Cancel", key=f"cancel_{v.get('epic_no')}"):
                        st.session_state[contact_key] = False
                        st.rerun()
            # -------------------------------
            # VOTER FEEDBACK SECTION
            # -------------------------------
            st.divider()
            st.markdown("🗳️ **Voter Preference (Pre-Poll Feedback)**")

            feedback = v.get("feedback", {})

            party = st.selectbox(
                "Preferred Party",
                ["", "INC", "BJP", "BRS", "Others", "Undecided"],
                index=(
                    ["", "INC", "BJP", "BRS", "Others", "Undecided"]
                    .index(feedback.get("party", ""))
                    if feedback.get("party", "") in ["INC", "BJP", "BRS", "Others", "Undecided"] else 0
                ),
                key=f"party_{v['epic_no']}"
            )

            candidate = st.text_input(
                "Preferred Candidate",
                value=feedback.get("candidate", ""),
                key=f"candidate_{v['epic_no']}"
            )

            confidence = st.radio(
                "Confidence Level",
                ["Strong", "Leaning", "Undecided"],
                index=(
                    ["Strong", "Leaning", "Undecided"]
                    .index(feedback.get("confidence"))
                    if feedback.get("confidence") in ["Strong", "Leaning", "Undecided"] else 2
                ),
                horizontal=True,
                key=f"confidence_{v['epic_no']}"
            )

            if st.button("📊 Save Feedback", key=f"save_feedback_{v['epic_no']}"):

                for voter in voters:
                    if voter.get("epic_no") == v.get("epic_no"):
                        voter["feedback"] = {
                            "party": party,
                            "candidate": candidate,
                            "confidence": confidence,
                            "updated_by": st.session_state.get("username"),
                            "updated_on": str(pd.Timestamp.now().date())
                        }
                        break

                save_voters(DATA_FILE, voters)
                st.success("✅ Voter feedback saved")
                st.rerun()
