import streamlit as st
import requests
import pandas as pd
import sqlite3
import io
import os
import base64

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="D.O.R.A AI", page_icon="🏥", layout="wide")

# =========================
# 🏥 HEADER
# =========================
st.title("🏥 Ramaiah Memorial Hospital — D.O.R.A AI")
st.caption("AI Voice-Driven Hospital Assistant")
st.divider()

# =========================
# 📌 SIDEBAR
# =========================
menu = st.sidebar.radio(
    "Navigation",
    ["📅 Book Appointment", "👨‍⚕️ Check Availability", "🔄 Reschedule", "❌ Cancel", "📊 Admin"]
)

# =========================
# 📅 BOOK APPOINTMENT
# =========================
if menu == "📅 Book Appointment":

    st.subheader("📅 Book Appointment")

    with st.form("book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name")
            department = st.selectbox("🏥 Department", [
                "General Medicine", "Cardiology", "Orthopedics",
                "Neurology", "Pediatrics"
            ])

        with col2:
            date = st.date_input("📅 Date")
            doctor = st.text_input("👨‍⚕️ Doctor (Optional)")

        # ✅ FIXED (PHONE FIELD)
        phone = st.text_input("📱 Phone Number", placeholder="10-digit number")

        reason = st.text_area("📝 Reason")

        submitted = st.form_submit_button("🚀 Book Appointment")

        if submitted:
            if not patient_name or not reason or not phone:
                st.error("All required fields must be filled")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("Enter valid 10-digit phone number")
            else:
                payload = {
                    "patient_name": patient_name,
                    "department": department,
                    "reason": reason,
                    "date": str(date),
                    "phone": phone,
                    "doctor": doctor if doctor else None
                }

                try:
                    res = requests.post(f"{BASE_URL}/appointments", json=payload)

                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ Appointment Booked & SMS Sent")

                        st.write("👨‍⚕️ Doctor:", data.get("doctor"))
                        st.write("🚨 Priority:", data.get("priority"))

                    else:
                        st.error(res.text)

                except Exception as e:
                    st.error(f"Connection error: {e}")

# =========================
# 👨‍⚕️ CHECK AVAILABILITY
# =========================
elif menu == "👨‍⚕️ Check Availability":

    st.subheader("🔍 Check Availability")

    doctor = st.text_input("Doctor Name (Optional)")
    department = st.selectbox("Department", [
        "Any", "General Medicine", "Cardiology",
        "Orthopedics", "Neurology", "Pediatrics"
    ])

    date = st.date_input("Date")

    if st.button("Check"):
        params = {"date": str(date)}

        if doctor:
            params["doctor"] = doctor
        if department != "Any":
            params["department"] = department

        try:
            res = requests.get(f"{BASE_URL}/availability", params=params)

            if res.status_code == 200:
                data = res.json()
                st.success("Available Data")

                st.json(data)

            else:
                st.error("Failed")

        except Exception as e:
            st.error(e)

# =========================
# 🔄 RESCHEDULE
# =========================
elif menu == "🔄 Reschedule":

    st.subheader("🔄 Reschedule Appointment")

    patient_name = st.text_input("Patient Name")
    old_date = st.date_input("Old Date")
    new_date = st.date_input("New Date")

    if st.button("Reschedule"):
        payload = {
            "patient_name": patient_name,
            "old_date": str(old_date),
            "new_date": str(new_date)
        }

        try:
            res = requests.put(f"{BASE_URL}/appointments", json=payload)

            if res.status_code == 200:
                st.success("Rescheduled Successfully")
            else:
                st.error(res.text)

        except Exception as e:
            st.error(e)

# =========================
# ❌ CANCEL
# =========================
elif menu == "❌ Cancel":

    st.subheader("❌ Cancel Appointment")

    patient_name = st.text_input("Patient Name")
    date = st.date_input("Date")

    if st.button("Cancel"):
        params = {
            "patient_name": patient_name,
            "date": str(date)
        }

        try:
            res = requests.delete(f"{BASE_URL}/appointments", params=params)

            if res.status_code == 200:
                st.success("Cancelled Successfully")
            else:
                st.error(res.text)

        except Exception as e:
            st.error(e)

# =========================
# 📊 ADMIN DASHBOARD
# =========================
elif menu == "📊 Admin":

    st.subheader("📊 Admin Dashboard")

    try:
        conn = sqlite3.connect("hospital.db")
        df_app = pd.read_sql_query("SELECT * FROM appointments", conn)
        df_conv = pd.read_sql_query("SELECT * FROM conversations", conn)

        st.metric("Total Appointments", len(df_app))
        st.metric("Total Conversations", len(df_conv))

        st.divider()

        st.dataframe(df_app)
        st.dataframe(df_conv)

        output = io.BytesIO()
        df_app.to_excel(output, index=False)

        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="appointments.xlsx"
        )

    except Exception as e:
        st.error(e)