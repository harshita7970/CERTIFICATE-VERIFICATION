import streamlit as st
import hashlib
import json
from time import time
from datetime import date
import uuid

# ---------------------------
# Blockchain Class
# ---------------------------

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending = []
        self.create_block(previous_hash="0")  # Genesis block

    def create_block(self, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "certificates": self.pending,
            "previous_hash": previous_hash
        }
        block["hash"] = self.hash(block)
        self.pending = []  # reset pending list
        self.chain.append(block)
        return block

    def add_certificate(self, cert_data):
        """Add certificate dictionary to pending list"""
        self.pending.append(cert_data)
        return cert_data

    @staticmethod
    def hash(block):
        copy = block.copy()
        copy.pop("hash", None)
        return hashlib.sha256(json.dumps(copy, sort_keys=True).encode()).hexdigest()

    def verify(self, cert_id):
        """Check if certificate ID exists in blockchain"""
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["certificate_id"] == cert_id:
                    return True, cert, block
        return False, None, None

    def get_chain(self):
        return self.chain


# ---------------------------
# Initialize
# ---------------------------

if "bc" not in st.session_state:
    st.session_state.bc = Blockchain()

st.set_page_config(page_title="Blockchain Certificate Verification", layout="wide")
st.title("🎓 Blockchain-based Student Certificate Verification")
st.caption("Tamper-proof storage and verification of student certificates using Blockchain.")


# ---------------------------
# Tabs
# ---------------------------

tabs = st.tabs(["📄 Issue Certificate", "⛏️ Mine Block", "🔍 Verify Certificate", "📦 Blockchain Ledger"])

# ---- Tab 1: Issue Certificate ----
with tabs[0]:
    st.header("📄 Issue a New Certificate")
    with st.form("form_issue"):
        col1, col2 = st.columns(2)

        with col1:
            student = st.text_input("Student Name")
            university = st.text_input("University Name")
            course = st.text_input("Course Name")

        with col2:
            issue_date = st.date_input("Date of Issue", value=date.today())
            cert_type = st.selectbox(
                "Type of Certificate",
                ["Academic", "Participation", "Merit", "Completion", "Sports", "Cultural", "Other"]
            )
            cert_id = str(uuid.uuid4())[:8]  # short unique ID

        submit = st.form_submit_button("Add to Pending List")
        if submit:
            if student and university and course:
                cert_data = {
                    "certificate_id": cert_id,
                    "student": student,
                    "university": university,
                    "course": course,
                    "issue_date": str(issue_date),
                    "type": cert_type
                }
                st.session_state.bc.add_certificate(cert_data)
                st.success(f"✅ Certificate issued for {student} (ID: {cert_id}) added to pending list.")
            else:
                st.warning("⚠️ Please fill all mandatory fields (Student, University, Course).")


# ---- Tab 2: Mine Block ----
with tabs[1]:
    st.header("⛏️ Mine Certificates into a Block")
    if st.button("Mine Block"):
        if len(st.session_state.bc.pending) == 0:
            st.info("No pending certificates to mine yet.")
        else:
            prev_hash = st.session_state.bc.chain[-1]["hash"]
            block = st.session_state.bc.create_block(prev_hash)
            st.success(f"Block #{block['index']} mined successfully!")
            st.json(block)


# ---- Tab 3: Verify Certificate ----
with tabs[2]:
    st.header("🔍 Verify Certificate by ID")
    cert_id_search = st.text_input("Enter Certificate ID")
    if st.button("Verify"):
        found, cert, block = st.session_state.bc.verify(cert_id_search)
        if found:
            st.success("✅ Certificate Found in Blockchain!")
            st.write(f"**Student:** {cert['student']}")
            st.write(f"**University:** {cert['university']}")
            st.write(f"**Course:** {cert['course']}")
            st.write(f"**Date of Issue:** {cert['issue_date']}")
            st.write(f"**Type:** {cert['type']}")
            st.write(f"**Block #:** {block['index']}")
            st.code(f"Block Hash: {block['hash']}")
        else:
            st.error("❌ Certificate not found.")


# ---- Tab 4: Blockchain Ledger ----
with tabs[3]:
    st.header("📦 Blockchain Ledger")
    for block in st.session_state.bc.get_chain():
        with st.expander(f"Block #{block['index']}"):
            st.write(f"⏰ Timestamp: {block['timestamp']}")
            st.write(f"🔗 Previous Hash: {block['previous_hash']}")
            st.json(block["certificates"])
            st.write(f"🧾 Block Hash: {block['hash']}")
