import streamlit as st
import requests
import pandas as pd
import sqlite3
import io
import os
import base64
import datetime

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="D.O.R.A AI", page_icon="🏥", layout="wide")

# =========================
# 🎨 CUSTOM UI (Modern Premium Look)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
}

[data-testid="stSidebar"] {
    background-color: #0f172a;
    color: #f8fafc;
}

[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

/* 📌 Sidebar Navigation Menu Enhancements */
[data-testid="stSidebar"] .stRadio > label {
    font-size: 22px !important;
    font-weight: 800 !important;
    margin-bottom: 25px !important;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 15px;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] [role="radiogroup"] > label {
    padding: 12px 15px;
    border-radius: 10px;
    background-color: rgba(255,255,255,0.03);
    transition: all 0.3s ease;
    margin-bottom: 5px;
    cursor: pointer;
}

[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.1);
    transform: translateX(5px);
}

[data-testid="stSidebar"] [role="radiogroup"] p {
    font-size: 18px !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

[data-testid="stForm"] {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    text-align: center;
}

[data-testid="stMetricValue"] {
    color: #0f172a;
    font-weight: 800;
}

[data-testid="stFormSubmitButton"] > button, .stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    padding: 10px 24px;
    transition: all 0.3s ease;
}

h1, h2, h3 {
    color: #0f172a;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🏥 HEADER
# =========================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_base64 = get_base64_image("logo.png")
if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 90px; object-fit: contain;">'
else:
    logo_html = '<div style="font-size: 45px;">🏥</div>'

st.markdown(f"""
<div style="background: white; padding: 25px 35px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 20px; margin-bottom: 10px; border: 1px solid #e2e8f0;">
    <div style="min-width: 80px; height: 80px; display: flex; align-items: center; justify-content: center;">
        {logo_html}
    </div>
    <div>
        <h1 style="margin: 0; font-size: 34px; color: #0f172a; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">RAMAIAH MEMORIAL HOSPITAL</h1>
        <h3 style="margin: 4px 0 0 0; font-size: 20px; color: #2563eb; font-weight: 800; letter-spacing: 0.5px;">D.O.R.A AI Assistant</h3>
        <p style="margin: 4px 0 0 0; font-size: 16px; color: #64748b; font-weight: 500;">AI Voice-Driven Hospital Assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# 🛠️ HELPERS
# =========================
def fetch_doctors(dept=None):
    try:
        params = {"department": dept} if dept and dept != "Any" else {}
        res = requests.get(f"{BASE_URL}/doctors", params=params)
        if res.status_code == 200:
            return [d["name"] for d in res.json()]
    except:
        pass
    return []

# =========================
# 📌 SIDEBAR
# =========================
menu = st.sidebar.radio(
    "Navigation Menu",
    ["📅 Book Appointment", "👨‍⚕️ Check Availability", "🔄 Reschedule", "❌ Cancel Appointment", "📊 Admin Dashboard"]
)

VALID_DEPARTMENTS = [
    "Accident & Emergency", "Cardiology", "Critical Care Medicine", 
    "Dermatology & Cosmetology", "ENT", "Endocrinology", 
    "General Medicine", "General Surgery", "Neurology", 
    "Neurosurgery", "Obstetrics & Gynecology", "Orthopaedics", 
    "Urology", "Vascular Surgery"
]

# =========================
# 📅 BOOK APPOINTMENT
# =========================
if menu == "📅 Book Appointment":
    st.subheader("📅 Book Appointment")

    with st.form("book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name")
            department = st.selectbox("🏥 Department", VALID_DEPARTMENTS)
            phone = st.text_input("📱 Phone Number", placeholder="10-digit number")

        with col2:
            date = st.date_input("📅 Date", min_value=datetime.date.today())
            available_doctors = fetch_doctors(department)
            doctor = st.selectbox("👨‍⚕️ Select Doctor", ["Any (Auto-assign)"] + available_doctors)

        reason = st.text_area("📝 Reason for Visit")

        submitted = st.form_submit_button("🚀 Book Appointment")

        if submitted:
            if not patient_name or not reason or not phone:
                st.error("⚠️ Please fill all required fields")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("⚠️ Enter valid 10-digit phone number")
            else:
                payload = {
                    "patient_name": patient_name,
                    "department": department,
                    "reason": reason,
                    "date": str(date),
                    "phone": phone,
                    "doctor": doctor if doctor != "Any (Auto-assign)" else None
                }

                try:
                    res = requests.post(f"{BASE_URL}/appointments", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ Appointment Booked & SMS Sent!")
                        st.info(f"👨‍⚕️ **Assigned Doctor:** {data.get('doctor')}")
                        st.warning(f"🚨 **Triage Priority:** {data.get('priority')}")
                    else:
                        st.error(f"❌ Error: {res.text}")
                except Exception as e:
                    st.error(f"🔌 Connection Error: {e}")

# =========================
# 👨‍⚕️ CHECK AVAILABILITY
# =========================
elif menu == "👨‍⚕️ Check Availability":
    st.subheader("🔍 Check Doctor Availability")

    with st.form("availability_form"):
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("🏥 Department", ["Any"] + VALID_DEPARTMENTS)
        with col2:
            available_doctors = fetch_doctors(department if department != "Any" else None)
            doctor = st.selectbox("👨‍⚕️ Doctor Name", ["Any"] + available_doctors)

        date = st.date_input("📅 Date", min_value=datetime.date.today())
        submitted = st.form_submit_button("🔍 Check")

        if submitted:
            params = {"date": str(date)}
            if doctor != "Any": params["doctor"] = doctor
            if department != "Any": params["department"] = department

            try:
                res = requests.get(f"{BASE_URL}/availability", params=params)
                if res.status_code == 200:
                    st.json(res.json())
                else:
                    st.error("❌ Failed to fetch availability")
            except Exception as e:
                st.error(f"🔌 Error: {e}")

# =========================
# 🔄 RESCHEDULE
# =========================
elif menu == "🔄 Reschedule":
    st.subheader("🔄 Reschedule Appointment")
    patient_name = st.text_input("👤 Patient Name")
    phone = st.text_input("📞 Phone Number")
    old_date = st.date_input("📅 Old Date")
    new_date = st.date_input("🗓️ New Date")

    if st.button("🔄 Reschedule"):
        payload = {
            "patient_name": patient_name,
            "old_date": str(old_date),
            "new_date": str(new_date),
            "phone": phone
        }
        try:
            res = requests.put(f"{BASE_URL}/appointments", json=payload)
            if res.status_code == 200:
                st.success("✅ Rescheduled Successfully")
            else:
                st.error(f"❌ {res.text}")
        except Exception as e:
            st.error(e)

# =========================
# ❌ CANCEL
# =========================
elif menu == "❌ Cancel Appointment":
    st.subheader("❌ Cancel Appointment")
    patient_name = st.text_input("👤 Patient Name")
    phone = st.text_input("📞 Phone Number")
    date = st.date_input("📅 Date")

    if st.button("❌ Cancel"):
        params = {"patient_name": patient_name, "date": str(date), "phone": phone}
        try:
            res = requests.delete(f"{BASE_URL}/appointments", params=params)
            if res.status_code == 200:
                st.success("✅ Cancelled Successfully")
            else:
                st.error(f"❌ {res.text}")
        except Exception as e:
            st.error(e)

# =========================
# 📊 ADMIN DASHBOARD
# =========================
elif menu == "📊 Admin Dashboard":
    st.subheader("📊 Admin Dashboard")
    try:
        conn = sqlite3.connect("hospital.db")
        df_app = pd.read_sql_query("SELECT * FROM appointments", conn)
        df_conv = pd.read_sql_query("SELECT * FROM conversations", conn)
        
        st.metric("Total Appointments", len(df_app))
        st.metric("Conversations", len(df_conv))
        
        st.write("### 📅 Recent Appointments")
        st.dataframe(df_app)
        
        output = io.BytesIO()
        df_app.to_excel(output, index=False)
        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="appointments.xlsx")
    except Exception as e:
        st.error(f"Database Error: {e}")