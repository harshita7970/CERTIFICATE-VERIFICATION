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
        self.pending_certificates = []
        self.create_block(previous_hash="0")  # Genesis block

    # ---------------------------
    # Core Blockchain Functions
    # ---------------------------
    def create_block(self, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "certificates": self.pending_certificates,
            "previous_hash": previous_hash
        }
        block["hash"] = self.hash(block)
        self.pending_certificates = []  # Reset pending certificates
        self.chain.append(block)
        return block

    def add_certificate(self, student_name, course_name):
        certificate = {"student_name": student_name, "course_name": course_name}
        self.pending_certificates.append(certificate)
        return certificate

    @staticmethod
    def hash(block):
        block_copy = block.copy()
        block_copy.pop("hash", None)
        return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()

    # ---------------------------
    # Verification Functions
    # ---------------------------
    def verify_certificate(self, student_name):
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["student_name"].lower() == student_name.lower():
                    return True, cert, block["index"], block["hash"]
        return False, None, None, None

    def search_by_course(self, course_name):
        results = []
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["course_name"].lower() == course_name.lower():
                    results.append((cert, block["index"], block["hash"]))
        return results

    def get_chain(self):
        return self.chain

# ---------------------------
# Helper Functions for Streamlit
# ---------------------------

def issue_certificate_ui():
    st.header("📄 Issue a New Certificate")
    with st.form("issue_cert_form"):
        student_name = st.text_input("Student Name")
        course_name = st.text_input("Course Name")
        submit_cert = st.form_submit_button("Issue Certificate")
        if submit_cert:
            if student_name.strip() == "" or course_name.strip() == "":
                st.warning("Please provide both student name and course name.")
            else:
                certificate = st.session_state.blockchain.add_certificate(student_name, course_name)
                st.success(f"Certificate added for {student_name} - {course_name}. ✅")

def mine_block_ui():
    st.header("⛏️ Mine Certificates to Blockchain")
    if st.button("Mine Block"):
        if len(st.session_state.blockchain.pending_certificates) == 0:
            st.warning("No certificates to mine!")
        else:
            last_hash = st.session_state.blockchain.chain[-1]["hash"]
            block = st.session_state.blockchain.create_block(last_hash)
            st.success(f"Block #{block['index']} mined successfully! 🔗")
            st.json(block)

def verify_certificate_ui():
    st.header("🔍 Verify Certificate")
    search_name = st.text_input("Enter Student Name to Verify")
    if st.button("Verify"):
        if search_name.strip() == "":
            st.warning("Enter a student name.")
        else:
            found, cert, block_index, bl_
