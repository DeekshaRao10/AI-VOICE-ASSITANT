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
            "reason": a.reason,
            "date": a.date,
            "time": "N/A",
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
        "numbers": phone
    }

    headers = {
        "authorization": "RdMt85eOcSg0mzYaTULQ4sNCup9wWXjIKxB6G7oJlqA23hnb1D2CbniU3DwayOsZL98GQjfW6xPAdhXu"  # 🔴 Replace with your Fast2SMS API Key
    }

    try:
        requests.post(url, data=payload, headers=headers)
    except Exception as e:
        print("SMS Failed:", e)


# =========================
# 🏥 DEPARTMENTS
# =========================
VALID_DEPARTMENTS = [
    "Accident & Emergency",
    "Cardiology",
    "Critical Care Medicine",
    "Dermatology & Cosmetology",
    "ENT",
    "Endocrinology",
    "General Medicine",
    "General Surgery",
    "Neurology",
    "Neurosurgery",
    "Obstetrics & Gynecology",
    "Orthopaedics",
    "Urology",
    "Vascular Surgery",
]


# =========================
# 🧠 TRIAGE
# =========================
def detect_priority(reason: str):
    urgent_keywords = [
        "chest pain", "breathing", "bleeding", "accident",
        "stroke", "unconscious", "seizure", "heart attack"
    ]
    for word in urgent_keywords:
        if word in reason.lower():
            return "HIGH"
    return "NORMAL"


# ✅ DOCTORS LIST API
@app.get("/doctors")
def get_doctors(department: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Doctor)
    if department and department != "Any":
        query = query.filter(Doctor.department == department)
    doctors = query.all()
    return [{"name": d.name, "department": d.department} for d in doctors]


# ✅ AVAILABILITY API
@app.get("/availability")
def check_availability(
    doctor: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    if doctor:
        doc = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor}%")).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return {
            "doctor": doc.name,
            "department": doc.department,
            "available_slots": ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"]
        }

    query = db.query(Doctor)
    if department and department != "Any":
        query = query.filter(Doctor.department == department)
    
    doctors = query.all()
    return {
        "department": department if department else "All",
        "available_doctors": [d.name for d in doctors],
        "available_slots": ["10:00 AM", "12:00 PM", "03:00 PM"]
    }


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


class LogRequest(BaseModel):
    patient_name: str
    transcript: str


class RescheduleRequest(BaseModel):
    patient_name: str
    old_date: str
    new_date: str
    phone: str
    doctor: str | None = None


# =========================
# 🚀 APIs
# =========================

# ✅ BOOK
@app.post("/appointments")
def book_appointment(request: BookAppointmentRequest, db: Session = Depends(get_db)):

    if request.department not in VALID_DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department")

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
        department=request.department,
        reason=request.reason,
        doctor=doctor_name,
        date=request.date,
        priority=priority
    )

    db.add(appointment)
    db.commit()

    # 📊 Excel
    export_appointments_to_excel(db)

    # 📩 SMS
    message = f"Hello {request.patient_name}, your appointment with {doctor_name} on {request.date} is confirmed."
    send_sms(request.phone, message)

    return {
        "message": "Appointment booked",
        "doctor": doctor_name,
        "priority": priority,
        "wait_time": f"{wait_time} minutes"
    }


# ✅ CANCEL
@app.delete("/appointments")
def cancel_appointment(
    patient_name: str,
    date: str,
    phone: str,
    db: Session = Depends(get_db)
):
    query = select(Appointment).where(
        Appointment.patient_name == patient_name,
        Appointment.date == date
    )

    result = db.execute(query)
    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    db.delete(appointment)
    db.commit()

    export_appointments_to_excel(db)

    send_sms(phone, f"Hello {patient_name}, your appointment on {date} has been cancelled.")

    return {"message": "Cancelled"}


# ✅ RESCHEDULE
@app.put("/appointments")
def reschedule_appointment(request: RescheduleRequest, db: Session = Depends(get_db)):

    query = select(Appointment).where(
        Appointment.patient_name == request.patient_name,
        Appointment.date == request.old_date
    )

    result = db.execute(query)
    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    appointment.date = request.new_date
    db.commit()

    export_appointments_to_excel(db)

    send_sms(request.phone,
             f"Hello {request.patient_name}, your appointment is rescheduled to {request.new_date}.")

    return {"message": "Rescheduled"}


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