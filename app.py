import streamlit as st
import hashlib
import json
import time
import pandas as pd
from fpdf import FPDF
import io

# ---------------- Blockchain Classes ---------------- #
class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data  # certificate details
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", time.time(), {"Genesis Block": "Initial Block"})

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def mine_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), latest_block.hash, time.time(), data)
        self.add_block(new_block)
        return new_block

    def verify_certificate(self, student_name, course_name):
        for block in self.chain[1:]:  # skip genesis block
            data = block.data
            if (data["Student Name"].lower() == student_name.lower() and
                data["Course"].lower() == course_name.lower()):
                return True, data
        return False, None


# ---------------- PDF Generator ---------------- #
def generate_certificate_pdf(cert_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "🎓 Blockchain Certificate", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    for key, value in cert_data.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="Blockchain Certificate Verification", layout="wide")

# Session state blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

blockchain = st.session_state.blockchain

st.title("🎓 Blockchain-based Student Certificate Verification System")

# Tabs for different sheets
tabs = st.tabs([
    "➕ Issue Certificate",
    "📑 Stored Certificates",
    "✅ Verify Certificate",
    "🔗 Blockchain Calculation"
])

# ---------------- Tab 1: Issue Certificate ---------------- #
with tabs[0]:
    st.header("➕ Issue a New Certificate")

    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("👤 Student Name")
        course_name = st.text_input("📘 Course Name")
        university = st.text_input("🏫 University / Institution")
        cert_type = st.selectbox("📜 Type of Certificate",
                                 ["Academic", "Participation", "Excellence", "Sports", "Cultural", "Other"])

    with col2:
        date_of_issue = st.date_input("📅 Date of Issue")
        issuer = st.text_input("🖊️ Issued By (Authority/Professor)")
        grade = st.text_input("📊 Grade / Score (Optional)", value="N/A")
        remarks = st.text_area("📝 Remarks", placeholder="Additional comments (optional)")

    if st.button("⛏️ Mine & Issue Certificate"):
        cert_data = {
            "Student Name": student_name,
            "Course": course_name,
            "University": university,
            "Type": cert_type,
            "Date of Issue": str(date_of_issue),
            "Issuer": issuer,
            "Grade": grade,
            "Remarks": remarks
        }
        new_block = blockchain.mine_block(cert_data)
        st.success(f"✅ Certificate for {student_name} issued successfully and added to blockchain!")

        # --- Download issued certificate as PDF ---
        pdf_file = generate_certificate_pdf(cert_data)
        st.download_button(
            label="⬇️ Download This Certificate (PDF)",
            data=pdf_file,
            file_name=f"certificate_{student_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )


# ---------------- Tab 2: Stored Certificates ---------------- #
with tabs[1]:
    st.header("📑 Stored Certificates (Blockchain Ledger)")

    if len(blockchain.chain) > 1:
        records = []
        for block in blockchain.chain[1:]:  # skip genesis
            data = block.data
            record = {
                "Block Index": block.index,
                "Student Name": data["Student Name"],
                "Course": data["Course"],
                "University": data["University"],
                "Type": data["Type"],
                "Date of Issue": data["Date of Issue"],
                "Issuer": data["Issuer"],
                "Grade": data["Grade"],
                "Remarks": data["Remarks"],
                "Hash": block.hash
            }
            records.append(record)

        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)

        # --- Download all certificates ---
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download All Certificates (CSV)",
            data=csv,
            file_name="certificates_blockchain.csv",
            mime="text/csv"
        )

        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Certificates")
        excel_bytes.seek(0)

        st.download_button(
            label="⬇️ Download All Certificates (Excel)",
            data=excel_bytes,
            file_name="certificates_blockchain.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("⚠️ No certificates have been issued yet.")


# ---------------- Tab 3: Verify Certificate ---------------- #
with tabs[2]:
    st.header("✅ Verify a Certificate")

    col1, col2 = st.columns(2)

    with col1:
        search_name = st.text_input("👤 Enter Student Name")
    with col2:
        search_course = st.text_input("📘 Enter Course Name")

    if st.button("🔍 Verify"):
        if search_name and search_course:
            found, details = blockchain.verify_certificate(search_name, search_course)
            if found:
                st.success(f"✅ Certificate Found for {search_name} in {search_course}!")
                st.json(details)
            else:
                st.error("❌ Certificate not found in the blockchain.")
        else:
            st.warning("⚠️ Please enter both Student Name and Course Name for verification.")


# ---------------- Tab 4: Blockchain Calculation ---------------- #
with tabs[3]:
    st.header("🔗 Blockchain Structure & Calculation")

    for block in blockchain.chain:
        with st.expander(f"Block {block.index}"):
            st.write(f"**Timestamp:** {time.ctime(block.timestamp)}")
            st.write(f"**Previous Hash:** {block.previous_hash}")
            st.write(f"**Current Hash:** {block.hash}")
            st.json(block.data)
