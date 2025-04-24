# demo_app.py
import streamlit as st

st.set_page_config(page_title="Secure Demo App")

st.title("🔐 Secure Demo App")

st.write("Welcome! This is a password-protected demo.")

# --- Basic password protection ---
password = st.text_input("Enter the password to continue:", type="password")
if password == "letmein":
    st.success("Access granted!")
    st.write("🎉 Now you can see this secure content.")
else:
    st.warning("Enter the correct password to proceed.")
