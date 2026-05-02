import streamlit as st
import requests
import pandas as pd
import sqlite3
import io
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="D.O.R.A AI", layout="wide")

st.title("🏥 D.O.R.A AI - Hospital Assistant")
st.subheader("Ramaiah Memorial Hospital")

# Sidebar
menu = st.sidebar.selectbox(
    "Select Operation",
    ["Book Appointment", "Check Availability", "Cancel Appointment", "Reschedule Appointment", "Admin Panel"]
)

# =========================
# 📅 BOOK APPOINTMENT
# =========================
if menu == "Book Appointment":
    st.header("📅 Book Appointment")

    patient_name = st.text_input("Patient Name")
    department = st.selectbox("Department", ["General Medicine", "Cardiology", "Orthopedics"])
    reason = st.text_area("Reason / Symptoms")
    date = st.text_input("Date (YYYY-MM-DD)")
    doctor = st.text_input("Doctor (Optional)")

    if st.button("Book"):
        payload = {
            "patient_name": patient_name,
            "department": department,
            "reason": reason,
            "date": date,
            "doctor": doctor if doctor else None
        }

        res = requests.post(f"{BASE_URL}/appointments", json=payload)

        if res.status_code == 200:
            st.success(res.json()["message"])
            st.write("Doctor:", res.json()["doctor"])
            st.write("Priority:", res.json()["priority"])
        else:
            st.error("Failed to book appointment")


# =========================
# 👨‍⚕️ CHECK AVAILABILITY
# =========================
elif menu == "Check Availability":
    st.header("👨‍⚕️ Check Availability")

    doctor = st.text_input("Doctor (optional)")
    department = st.text_input("Department")
    date = st.text_input("Date")

    if st.button("Check"):
        params = {
            "doctor": doctor,
            "department": department,
            "date": date
        }

        res = requests.get(f"{BASE_URL}/availability", params=params)

        if res.status_code == 200:
            data = res.json()
            st.json(data)
        else:
            st.error("Error fetching availability")


# =========================
# ❌ CANCEL APPOINTMENT
# =========================
elif menu == "Cancel Appointment":
    st.header("❌ Cancel Appointment")

    patient_name = st.text_input("Patient Name")
    doctor = st.text_input("Doctor")
    date = st.text_input("Date")

    if st.button("Cancel"):
        params = {
            "patient_name": patient_name,
            "doctor": doctor,
            "date": date
        }

        res = requests.delete(f"{BASE_URL}/appointments", params=params)

        if res.status_code == 200:
            st.success(res.json()["message"])
        else:
            st.error("Appointment not found")


# =========================
# 🔄 RESCHEDULE
# =========================
elif menu == "Reschedule Appointment":
    st.header("🔄 Reschedule Appointment")

    patient_name = st.text_input("Patient Name")
    doctor = st.text_input("Doctor")
    old_date = st.text_input("Old Date")
    new_date = st.text_input("New Date")

    if st.button("Reschedule"):
        payload = {
            "patient_name": patient_name,
            "doctor": doctor,
            "old_date": old_date,
            "new_date": new_date
        }

        res = requests.put(f"{BASE_URL}/appointments", json=payload)

        if res.status_code == 200:
            st.success(res.json()["message"])
        else:
            st.error("Reschedule failed")


# =========================
# 📊 ADMIN PANEL
# =========================
elif menu == "Admin Panel":
    st.header("📊 Admin Dashboard")

    # Connect to SQLite directly
    conn = sqlite3.connect("hospital.db")

    # Appointments Table
    st.subheader("Appointments")
    df_app = pd.read_sql_query("SELECT * FROM appointments", conn)
    st.dataframe(df_app)

    # Conversations (hidden but exportable)
    st.subheader("Conversation Logs (Hidden from main UI)")
    df_conv = pd.read_sql_query("SELECT * FROM conversations", conn)

    if st.checkbox("Show Conversations"):
        st.dataframe(df_conv)

    # Download buttons
    st.subheader("Download Data")

    # Appointments Excel
    output_app = io.BytesIO()
    df_app.to_excel(output_app, index=False)
    
    st.download_button(
        label="Download Appointments Excel",
        data=output_app.getvalue(),
        file_name="appointments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Conversations Excel
    output_conv = io.BytesIO()
    df_conv.to_excel(output_conv, index=False)
    
    st.download_button(
        label="Download Conversations Excel",
        data=output_conv.getvalue(),
        file_name="conversations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )