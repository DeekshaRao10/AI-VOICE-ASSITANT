# =========================
# 🔌 IMPORTS
# =========================
from database import init_db, seed_data, Appointment, Conversation, Doctor, get_db
init_db()
seed_data()

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
import pandas as pd
import requests

app = FastAPI(title="D.O.R.A AI Backend — MS Ramaiah Memorial Hospital")

# =========================
# 📊 EXCEL EXPORT
# =========================
def export_appointments_to_excel(db: Session):
    appointments = db.query(Appointment).all()

    data = []
    for a in appointments:
        data.append({
            "patient_id": a.id,
            "patient_name": a.patient_name,
            "phone": a.phone,
            "reason": a.reason,
            "date": a.date,
            "department": a.department,
            "doctor": a.doctor
        })

    df = pd.DataFrame(data)
    df.to_excel("appointments_summary.xlsx", index=False)

def export_conversations_to_excel(db: Session):
    convos = db.query(Conversation).all()

    data = []
    for c in convos:
        data.append({
            "patient_name": c.patient_name,
            "transcript": c.transcript,
            "timestamp": str(c.timestamp)
        })

    df = pd.DataFrame(data)
    df.to_excel("conversation_logs.xlsx", index=False)

# =========================
# 📩 FAST2SMS FUNCTION
# =========================
def send_sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone,
        "flash": "0"
    }

    headers = {
        "authorization": "RdMt85eOcSg0mzYaTULQ4sNCup9wWXjIKxB6G7oJlqA23hnb1D2CbniU3DwayOsZL98GQjfW6xPAdhXu"  # 🔴 Replace with your Fast2SMS API Key
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        print("SMS RESPONSE:", response.json())
    except Exception as e:
        print("SMS Failed:", e)

# =========================
# 📲 WHATSAPP NOTIFICATION (CallMeBot - Free)
# =========================
# HOW TO ACTIVATE (one-time setup per number):
# 1. Save +34 644 59 21 64 in contacts as "CallMeBot"
# 2. Send this WhatsApp message to that number:
#    "I allow callmebot to send me messages"
# 3. You will receive your API key via WhatsApp
# 4. Replace CALLMEBOT_API_KEY below with your key

CALLMEBOT_API_KEY = "YOUR_CALLMEBOT_API_KEY"  # 🔴 Replace with your CallMeBot API key

def send_whatsapp(phone, message):
    """
    Sends a WhatsApp popup message to the given phone number via CallMeBot.
    Phone must include country code without '+', e.g. '919876543210' for India.
    """
    import urllib.parse
    # Add India country code if 10-digit number
    if len(str(phone)) == 10:
        full_phone = f"91{phone}"
    else:
        full_phone = str(phone)

    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={full_phone}&text={encoded_message}&apikey={CALLMEBOT_API_KEY}"

    try:
        response = requests.get(url)
        print("WhatsApp RESPONSE:", response.status_code, response.text[:200])
        return response.status_code == 200
    except Exception as e:
        print("WhatsApp Failed:", e)
        return False


def send_appointment_notifications(phone, patient_name, doctor_name, department, date, priority, wait_time):
    """
    Sends both SMS and WhatsApp notification to patient's phone number.
    """
    priority_emoji = "🚨 URGENT" if priority == "HIGH" else "✅ Confirmed"

    # --- Detailed WhatsApp Message ---
    whatsapp_msg = (
        f"🏥 *RAMAIAH MEMORIAL HOSPITAL*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 *Appointment {priority_emoji}*\n\n"
        f"👤 *Patient:* {patient_name}\n"
        f"👨‍⚕️ *Doctor:* {doctor_name}\n"
        f"🏷️ *Department:* {department}\n"
        f"📅 *Date:* {date}\n"
        f"⏱️ *Est. Wait:* {wait_time} minutes\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 MS Ramaiah Memorial Hospital\n"
        f"Please arrive 15 mins early. Carry a valid ID.\n"
        f"For queries call: 080-23608888"
    )

    # --- Concise SMS Message ---
    sms_msg = (
        f"RAMAIAH HOSPITAL: Hi {patient_name}, your appointment with {doctor_name} "
        f"({department}) on {date} is CONFIRMED. "
        f"Est. wait: {wait_time} mins. Arrive 15 mins early. "
        f"Queries: 080-23608888"
    )

    # Send both
    send_sms(phone, sms_msg)
    send_whatsapp(phone, whatsapp_msg)

# =========================
# 🔔 WINDOWS DESKTOP NOTIFICATION
# =========================
def send_system_popup(patient_name, doctor_name, department, date, priority):
    """
    Shows a Windows 10/11 toast popup notification on this system
    for bookings, cancellations, and reschedules.
    """
    try:
        from winotify import Notification, audio

        if priority == "HIGH":
            title = f"🚨 URGENT Appointment Booked!"
            sound = audio.Reminder
        elif priority == "CANCEL":
            title = f"❌ Appointment Cancelled"
            sound = audio.Default
        elif priority == "RESCHEDULE":
            title = f"🔄 Appointment Rescheduled"
            sound = audio.Default
        else:
            title = f"✅ New Appointment Booked!"
            sound = audio.Default

        toast = Notification(
            app_id="D.O.R.A AI — Ramaiah Memorial Hospital",
            title=title,
            msg=(
                f"Patient : {patient_name}\n"
                f"Doctor  : {doctor_name}\n"
                f"Dept    : {department}\n"
                f"Date    : {date}"
            ),
            duration="long",
        )
        toast.set_audio(sound, loop=False)
        toast.show()
        print(f"✅ System popup [{priority}] shown for: {patient_name}")
    except Exception as e:
        print(f"System notification failed: {e}")

# =========================
# 🏥 DEPARTMENTS
# =========================
VALID_DEPARTMENTS = [
    "Accident & Emergency", "Cardiology", "Critical Care Medicine", 
    "Dermatology & Cosmetology", "ENT", "Endocrinology", 
    "General Medicine", "General Surgery", "Neurology", 
    "Neurosurgery", "Obstetrics & Gynecology", "Orthopaedics", 
    "Urology", "Vascular Surgery"
]

# =========================
# 🧠 TRIAGE
# =========================
def detect_priority(reason: str):
    urgent_keywords = [
        "chest pain", "breathing", "bleeding", "accident",
        "stroke", "unconscious", "seizure", "heart attack", "emergency", "trauma"
    ]
    for word in urgent_keywords:
        if word in reason.lower():
            return "HIGH"
    return "NORMAL"

# =========================
# 👨‍⚕️ DOCTOR ASSIGNMENT
# =========================
def assign_doctor(db, department):
    return db.query(Doctor).filter(Doctor.department == department).first()

# =========================
# ⏳ WAIT TIME
# =========================
def estimate_wait_time(db, doctor_name):
    count = db.query(Appointment).filter(Appointment.doctor == doctor_name).count()
    return count * 10

# =========================
# 📦 SCHEMAS
# =========================
class BookAppointmentRequest(BaseModel):
    patient_name: str
    department: str
    reason: str
    date: str
    phone: str
    doctor: str | None = None

class RescheduleRequest(BaseModel):
    patient_name: str
    old_date: str
    new_date: str
    phone: str | None = None   # optional — fetched from DB if not provided
    doctor: str | None = None

class CancelRequest(BaseModel):
    patient_name: str
    date: str
    phone: str | None = None   # optional — fetched from DB if not provided

class LogRequest(BaseModel):
    patient_name: str
    transcript: str


# =========================
# 🚀 APIs
# =========================

# ✅ BOOK
@app.post("/appointments")
def book_appointment(request: BookAppointmentRequest, db: Session = Depends(get_db)):
    # Case-insensitive department matching (voice may say 'cardiology' not 'Cardiology')
    matched_dept = next(
        (d for d in VALID_DEPARTMENTS if d.lower() == request.department.lower()), None
    )
    if not matched_dept:
        raise HTTPException(status_code=400, detail=f"Invalid department: '{request.department}'. Valid: {VALID_DEPARTMENTS}")
    request.department = matched_dept  # normalize to correct casing

    priority = detect_priority(request.reason)

    if request.doctor:
        doctor_name = request.doctor
    else:
        doctor = assign_doctor(db, request.department)
        if not doctor:
            raise HTTPException(status_code=404, detail="No doctor available")
        doctor_name = doctor.name

    wait_time = estimate_wait_time(db, doctor_name)

    appointment = Appointment(
        patient_name=request.patient_name,
        phone=request.phone,
        department=request.department,
        reason=request.reason,
        doctor=doctor_name,
        date=request.date,
        priority=priority
    )

    db.add(appointment)
    db.commit()

    export_appointments_to_excel(db)

    # 📨 Send WhatsApp popup + SMS to patient's phone number
    send_appointment_notifications(
        phone=request.phone,
        patient_name=request.patient_name,
        doctor_name=doctor_name,
        department=request.department,
        date=request.date,
        priority=priority,
        wait_time=wait_time
    )

    # 🔔 Show Windows desktop popup on this system
    send_system_popup(
        patient_name=request.patient_name,
        doctor_name=doctor_name,
        department=request.department,
        date=request.date,
        priority=priority
    )

    return {
        "message": "Appointment booked",
        "doctor": doctor_name,
        "priority": priority,
        "wait_time": f"{wait_time} minutes"
    }

# ✅ AVAILABILITY
@app.get("/availability")
def check_availability(
    doctor: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date: str | None = Query(default=None),
    show_list: bool = Query(default=True, description="Always returns list for voice assistant"),
    db: Session = Depends(get_db)
):
    # Case-insensitive doctor search
    if doctor:
        doc = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor}%")).first()
        if not doc:
            raise HTTPException(status_code=404, detail=f"Doctor '{doctor}' not found")
        slots = doc.available_slots.split(",") if doc.available_slots else ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"]
        return {
            "doctor": doc.name,
            "department": doc.department,
            "available_slots": slots,
            "message": f"Dr. {doc.name} is available in {doc.department} at: {', '.join(slots)}"
        }

    query = db.query(Doctor)
    # Case-insensitive department filter
    if department and department.lower() != "any":
        query = query.filter(Doctor.department.ilike(f"%{department}%"))

    doctors = query.all()
    if not doctors:
        return {"message": f"No doctors found for department: {department}"}

    # Always return full list so voice assistant can read names aloud
    return {
        "department": department if department else "All",
        "total_doctors_available": len(doctors),
        "available_doctors": [
            {
                "name": d.name,
                "department": d.department,
                "slots": d.available_slots.split(",") if d.available_slots else ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"]
            }
            for d in doctors
        ],
        "message": f"There are {len(doctors)} doctors available: {', '.join([d.name for d in doctors])}"
    }

# ✅ DOCTORS LIST API
@app.get("/doctors")
def get_doctors(department: str | None = Query(default=None), show_list: bool = Query(default=False), db: Session = Depends(get_db)):
    query = db.query(Doctor)
    if department and department != "Any":
        query = query.filter(Doctor.department == department)
    doctors = query.all()
    if not doctors:
        return {"message": "No doctors found"}
    
    response = {"total": len(doctors)}
    if show_list:
        response["doctors"] = [{"name": d.name, "department": d.department} for d in doctors]
    else:
        response["message"] = "Ask specifically for their names."
        
    return response

# ✅ CANCEL
# Accepts both JSON body (Vapi/voice) and query params (frontend)
@app.delete("/appointments")
def cancel_appointment(
    request: CancelRequest | None = None,
    patient_name: str | None = Query(default=None),
    date: str | None = Query(default=None),
    phone: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    # Support both JSON body (voice) and query params (frontend form)
    p_name = (request.patient_name if request else None) or patient_name
    p_date = (request.date if request else None) or date
    p_phone = (request.phone if request else None) or phone

    if not p_name or not p_date:
        raise HTTPException(status_code=400, detail="patient_name and date are required")

    # Case-insensitive patient name match
    query = select(Appointment).where(
        Appointment.patient_name.ilike(f"%{p_name}%"),
        Appointment.date == p_date
    )

    result = db.execute(query)
    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail=f"No appointment found for '{p_name}' on {p_date}")

    phone_num = appointment.phone if appointment.phone else p_phone
    actual_name = appointment.patient_name

    db.delete(appointment)
    db.commit()
    export_appointments_to_excel(db)

    if phone_num:
        send_sms(phone_num, f"Hello {actual_name}, your appointment on {p_date} has been cancelled. — Ramaiah Hospital")

    # 🔔 Windows desktop popup
    send_system_popup(
        patient_name=actual_name,
        doctor_name=appointment.doctor or "N/A",
        department=appointment.department or "N/A",
        date=p_date,
        priority="CANCEL"
    )

    return {"message": f"Appointment for {actual_name} on {p_date} has been cancelled successfully."}

# ✅ RESCHEDULE
@app.put("/appointments")
def reschedule_appointment(request: RescheduleRequest, db: Session = Depends(get_db)):
    # Case-insensitive patient name match
    query = select(Appointment).where(
        Appointment.patient_name.ilike(f"%{request.patient_name}%"),
        Appointment.date == request.old_date
    )

    result = db.execute(query)
    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail=f"No appointment found for '{request.patient_name}' on {request.old_date}")

    phone_num = appointment.phone if appointment.phone else request.phone
    actual_name = appointment.patient_name

    appointment.date = request.new_date
    if request.doctor:
        appointment.doctor = request.doctor
    db.commit()
    export_appointments_to_excel(db)

    if phone_num:
        send_sms(
            phone_num,
            f"Hello {actual_name}, your appointment has been rescheduled from {request.old_date} to {request.new_date}. — Ramaiah Hospital"
        )

    # 🔔 Windows desktop popup
    send_system_popup(
        patient_name=actual_name,
        doctor_name=appointment.doctor or "N/A",
        department=appointment.department or "N/A",
        date=request.new_date,
        priority="RESCHEDULE"
    )

    return {
        "message": f"Appointment for {actual_name} successfully rescheduled to {request.new_date}.",
        "patient_name": actual_name,
        "new_date": request.new_date,
        "doctor": appointment.doctor
    }

# ✅ LOG
@app.post("/conversations")
def log_conversation(request: LogRequest, db: Session = Depends(get_db)):
    convo = Conversation(
        patient_name=request.patient_name,
        transcript=request.transcript
    )

    db.add(convo)
    db.commit()

    export_conversations_to_excel(db)

    return {"message": "Logged"}


# =========================
# ▶️ RUN
# =========================
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)