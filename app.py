import streamlit as st
import hashlib
import json
from time import time

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

    def add_certificate(self, student, course):
        cert = {"student": student, "course": course}
        self.pending.append(cert)
        return cert

    @staticmethod
    def hash(block):
        copy = block.copy()
        copy.pop("hash", None)
        return hashlib.sha256(json.dumps(copy, sort_keys=True).encode()).hexdigest()

    def verify(self, student):
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["student"].lower() == student.lower():
                    return True, cert, block
        return False, None, None


# ---------------------------
# Streamlit UI
# ---------------------------

if "bc" not in st.session_state:
    st.session_state.bc = Blockchain()

st.title("🎓 Blockchain-based Student Certificate Verification")
st.caption("Tamper-proof storage and verification of student certificates")

# ---- Issue Certificate ----
st.subheader("📄 Issue Certificate")
with st.form("form_issue"):
    student = st.text_input("Student Name")
    course = st.text_input("Course Name")
    submitted = st.form_submit_button("Add to Pending")
    if submitted:
        if student and course:
            st.session_state.bc.add_certificate(student, course)
            st.success(f"✅ Certificate for {student} added to pending list.")
        else:
            st.warning("⚠️ Please enter both Student and Course.")

# ---- Mine Block ----
st.subheader("⛏️ Mine Certificates into Block")
if st.button("Mine Block"):
    if len(st.session_state.bc.pending) == 0:
        st.info("No certificates to mine yet.")
    else:
        prev_hash = st.session_state.bc.chain[-1]["hash"]
        block = st.session_state.bc.create_block(prev_hash)
        st.success(f"Block #{block['index']} mined successfully!")
        st.json(block)

# ---- Verify Certificate ----
st.subheader("🔍 Verify Certificate")
student_search = st.text_input("Enter Student Name to Verify")
if st.button("Verify"):
    found, cert, block = st.session_state.bc.verify(student_search)
    if found:
        st.success(f"✅ Certificate Found!\n\n"
                   f"**Student:** {cert['student']}\n\n"
                   f"**Course:** {cert['course']}\n\n"
                   f"**Block #:** {block['index']}\n\n"
                   f"**Block Hash:** {block['hash']}")
    else:
        st.error("❌ Certificate not found.")

# ---- Show Blockchain ----
st.subheader("📦 Blockchain Ledger")
for block in st.session_state.bc.chain:
    with st.expander(f"Block #{block['index']}"):
        st.write(f"Timestamp: {block['timestamp']}")
        st.write(f"Previous Hash: {block['previous_hash']}")
        st.json(block["certificates"])
        st.write(f"Block Hash: {block['hash']}")
