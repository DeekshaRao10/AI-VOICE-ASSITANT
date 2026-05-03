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
    gap: 15px; /* Increases distance between radio items */
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] [role="radiogroup"] > label {
    padding: 12px 15px; /* Breathing room */
    border-radius: 10px;
    background-color: rgba(255,255,255,0.03); /* Subtle background */
    transition: all 0.3s ease;
    margin-bottom: 5px; /* Distance between items */
    cursor: pointer;
}

[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.1);
    transform: translateX(5px); /* Slight shift on hover */
}

[data-testid="stSidebar"] [role="radiogroup"] p {
    font-size: 18px !important; /* Larger font size */
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

[data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    color: white;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
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
# Helper to load image
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_base64 = get_base64_image("logo.png")
if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 90px; object-fit: contain;">'
    icon_container_style = "background: transparent; display: flex; align-items: center; justify-content: center; padding-right: 10px;"
else:
    logo_html = '<div style="font-size: 45px;">🏥</div>'
    icon_container_style = "background: linear-gradient(135deg, #eff6ff, #dbeafe); min-width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border-radius: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);"

st.markdown(f"""
<div style="background: white; padding: 25px 35px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 20px; margin-bottom: 10px; border: 1px solid #e2e8f0;">
    <div style="{icon_container_style}">
        {logo_html}
    </div>
    <div>
        <h1 style="margin: 0; font-size: 34px; color: #0f172a; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">RAMAIAH MEMORIAL HOSPITAL</h1>
        <h3 style="margin: 4px 0 0 0; font-size: 20px; color: #2563eb; font-weight: 800; letter-spacing: 0.5px;">D.O.R.A AI</h3>
        <p style="margin: 4px 0 0 0; font-size: 16px; color: #64748b; font-weight: 500;">AI Voice-Driven Hospital Assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.toast("🤖 System Ready", icon="🚀")
st.divider()

# =========================
# 📌 SIDEBAR
# =========================
menu = st.sidebar.radio(
    "Navigation Menu",
    ["📅 Book Appointment", "👨‍⚕️ Check Availability", "🔄 Reschedule", "❌ Cancel Appointment", "📊 Admin Dashboard"]
)
 
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
# 📅 BOOK
# =========================
if menu == "📅 Book Appointment":
    st.subheader("📅 Book a New Appointment")
    st.markdown("Fill out the details below to schedule a visit.")
    
    with st.form("book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name", placeholder="e.g. John Doe")
            department = st.selectbox("🏥 Department", [
                "Accident & Emergency", "Cardiology", "Critical Care Medicine", 
                "Dermatology & Cosmetology", "ENT", "Endocrinology", 
                "General Medicine", "General Surgery", "Neurology", 
                "Neurosurgery", "Obstetrics & Gynecology", "Orthopaedics", 
                "Urology", "Vascular Surgery"
            ])
            phone = st.text_input("📞 Phone Number", placeholder="e.g. 9876543210")

        with col2:
            date = st.date_input("📅 Appointment Date", min_value=datetime.date.today())
            # Fetch doctors based on selected department
            available_doctors = fetch_doctors(department)
            doctor = st.selectbox("👨‍⚕️ Select Doctor", ["Select Doctor"] + available_doctors)

        reason = st.text_area("📝 Symptoms & Reason for Visit", placeholder="Briefly describe your symptoms...")

        submitted = st.form_submit_button("🚀 Confirm Booking", width="stretch")

        if submitted:
            if not patient_name or not reason:
                st.error("⚠️ Patient Name and Symptoms are required!")
            else:
                payload = {
                    "patient_name": patient_name,
                    "department": department,
                    "reason": reason,
                    "date": str(date),
                    "phone": phone,
                    "doctor": doctor if doctor != "Select Doctor" else None
                }
                try:
                    res = requests.post(f"{BASE_URL}/appointments", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ Appointment Confirmed Successfully!")
                        col_r1, col_r2 = st.columns(2)
                        col_r1.info(f"👨‍⚕️ Assigned Doctor: **{data.get('doctor', 'N/A')}**")
                        priority_color = "🔴" if data.get('priority') == "HIGH" else "🟢"
                        col_r2.warning(f"{priority_color} Triage Priority: **{data.get('priority', 'NORMAL')}**")
                    else:
                        st.error(f"❌ Failed to book: {res.text}")
                except Exception as e:
                    st.error(f"🔌 Connection Error: {e}")

# =========================
# 👨‍⚕️ AVAILABILITY
# =========================
elif menu == "👨‍⚕️ Check Availability":
    st.subheader("🔍 Check Doctor Availability")
    st.markdown("Find open slots for your preferred doctor or department.")

    with st.form("availability_form"):
        col1, col2 = st.columns(2)

        with col1:
            department = st.selectbox("🏥 Department", ["Any", "Accident & Emergency", "Cardiology", "Critical Care Medicine", "Dermatology & Cosmetology", "ENT", "Endocrinology", "General Medicine", "General Surgery", "Neurology", "Neurosurgery", "Obstetrics & Gynecology", "Orthopaedics", "Urology", "Vascular Surgery"])
        with col2:
            available_doctors = fetch_doctors(department)
            doctor = st.selectbox("👨‍⚕️ Doctor Name", ["Any"] + available_doctors)

        date = st.date_input("📅 Date", min_value=datetime.date.today())

        submitted = st.form_submit_button("🔍 Check Availability", width="stretch")

        if submitted:
            params = {"date": str(date)}
            if doctor != "Any": params["doctor"] = doctor
            if department != "Any": params["department"] = department

            try:
                res = requests.get(f"{BASE_URL}/availability", params=params)
                if res.status_code == 200:
                    data = res.json()
                    st.success("✅ Availability Retrieved")
                    
                    if "available_slots" in data:
                        st.info(f"🕒 **Available Slots:** {', '.join(data['available_slots'])}")
                    if "available_doctors" in data:
                        st.info(f"👨‍⚕️ **Available Doctors:** {', '.join([d['name'] for d in data['available_doctors']])}")
                else:
                    st.error("❌ Failed to fetch availability")
            except Exception as e:
                st.error(f"🔌 Connection Error: {e}")

# =========================
# 🔄 RESCHEDULE
# =========================
elif menu == "🔄 Reschedule":
    st.subheader("🔄 Reschedule Appointment")
    st.markdown("Change the date of an existing appointment.")

    with st.form("reschedule_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name", placeholder="e.g. John Doe")
            phone = st.text_input("📞 Phone Number", placeholder="e.g. 9876543210")
            doctor = st.text_input("👨‍⚕️ Doctor Name (Optional)", placeholder="e.g. Dr. Smith")

        with col2:
            old_date = st.date_input("📅 Current Date", min_value=datetime.date.today())
            new_date = st.date_input("🗓️ New Date", min_value=datetime.date.today())

        submitted = st.form_submit_button("🔄 Confirm Reschedule", width="stretch")

        if submitted:
            if not patient_name:
                st.error("⚠️ Patient Name is required!")
            else:
                payload = {
                    "patient_name": patient_name,
                    "doctor": doctor if doctor else None,
                    "old_date": str(old_date),
                    "new_date": str(new_date),
                    "phone": phone
                }
                try:
                    res = requests.put(f"{BASE_URL}/appointments", json=payload)
                    if res.status_code == 200:
                        st.success("✅ Appointment Rescheduled Successfully!")
                    else:
                        st.error("❌ Failed: Appointment not found or invalid details.")
                except Exception as e:
                    st.error(f"🔌 Connection Error: {e}")

# =========================
# ❌ CANCEL
# =========================
elif menu == "❌ Cancel Appointment":
    st.subheader("❌ Cancel Appointment")
    st.markdown("Cancel an upcoming scheduled visit.")

    with st.form("cancel_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name", placeholder="e.g. John Doe")
            phone = st.text_input("📞 Phone Number", placeholder="e.g. 9876543210")
        with col2:
            doctor = st.text_input("👨‍⚕️ Doctor Name (Optional)", placeholder="e.g. Dr. Smith")

        date = st.date_input("📅 Date of Appointment", min_value=datetime.date.today())

        submitted = st.form_submit_button("❌ Confirm Cancellation", width="stretch")

        if submitted:
            if not patient_name:
                st.error("⚠️ Patient Name is required!")
            else:
                try:
                    params = {
                        "patient_name": patient_name,
                        "date": str(date),
                        "phone": phone
                    }
                    if doctor: params["doctor"] = doctor
                    
                    res = requests.delete(f"{BASE_URL}/appointments", params=params)
                    if res.status_code == 200:
                        st.success("✅ Appointment Cancelled Successfully!")
                    else:
                        st.error("❌ Failed: Appointment not found.")
                except Exception as e:
                    st.error(f"🔌 Connection Error: {e}")

# =========================
# 📊 ADMIN PANEL
# =========================
elif menu == "📊 Admin Dashboard":
    st.subheader("📊 Admin Analytics Dashboard")
    
    try:
        conn = sqlite3.connect("hospital.db")
        df_app = pd.read_sql_query("SELECT * FROM appointments", conn)
        df_conv = pd.read_sql_query("SELECT * FROM conversations", conn)

        # High-level Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 Total Appointments", len(df_app))
        col2.metric("💬 Total Conversations", len(df_conv))
        high_priority = len(df_app[df_app["priority"] == "HIGH"]) if not df_app.empty and "priority" in df_app.columns else 0
        col3.metric("🚨 High Priority Cases", high_priority)

        st.divider()

        # Visualizations
        if not df_app.empty:
            st.markdown("### 📈 Appointments Overview")
            v_col1, v_col2 = st.columns(2)
            
            with v_col1:
                st.markdown("**Appointments by Department**")
                if "department" in df_app.columns:
                    dept_counts = df_app["department"].value_counts().reset_index()
                    dept_counts.columns = ["Department", "Count"]
                    st.bar_chart(dept_counts.set_index("Department"))

            with v_col2:
                st.markdown("**Appointments by Date**")
                if "date" in df_app.columns:
                    date_counts = df_app["date"].value_counts().reset_index()
                    date_counts.columns = ["Date", "Count"]
                    # Sort dates
                    date_counts = date_counts.sort_values(by="Date")
                    st.line_chart(date_counts.set_index("Date"))

        st.divider()

        # Data Tables
        st.markdown("### 🗂️ Appointment Records")
        st.dataframe(df_app, width="stretch", hide_index=True)

        with st.expander("Show Conversation Logs 💬"):
            st.dataframe(df_conv, width="stretch", hide_index=True)

        st.divider()
        # Download Data
        st.markdown("### 📥 Export Data")
        
        output = io.BytesIO()
        df_app.to_excel(output, index=False)
        st.download_button(
            label="📄 Download Appointments as Excel",
            data=output.getvalue(),
            file_name="appointments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

    except Exception as e:
        st.error(f"Database error: {e}")