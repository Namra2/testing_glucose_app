import streamlit as st
import sqlite3
import re

# --- SETUP DATABASE ---
conn = sqlite3.connect("patient_data.db", check_same_thread=False)
c = conn.cursor()

# Create a table if not exists
c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY
    )
""")
conn.commit()

# --- FUNCTIONS ---
def is_valid_id(pid):
    return bool(re.match("^[a-zA-Z0-9]{1,20}$", pid))

def patient_exists(pid):
    c.execute("SELECT * FROM patients WHERE patient_id = ?", (pid,))
    return c.fetchone() is not None

def add_new_patient(pid):
    c.execute("INSERT INTO patients (patient_id) VALUES (?)", (pid,))
    conn.commit()

# --- UI STARTS ---
st.title("🔐 Secure Patient Entry App")

st.markdown("""
Enter your **Patient ID** below. This can be any ID you choose, up to 20 letters/numbers.  
- Use the same ID later to add or view your entries.
""")

patient_id = st.text_input("Enter Patient ID (max 20 alphanumeric characters)")

if patient_id:
    if not is_valid_id(patient_id):
        st.error("Invalid ID. Use only letters and numbers, up to 20 characters.")
        st.stop()

    if patient_exists(patient_id):
        st.success(f"✅ Welcome back, `{patient_id}`!")
    else:
        add_new_patient(patient_id)
        st.success(f"🎉 New ID `{patient_id}` created successfully!")

    # Use patient_id for further app logic below (e.g., entering lab values, history, etc.)
    st.write(f"Now you can continue using your ID: **{patient_id}**")

else:
    st.info("Please enter a Patient ID to begin.")
