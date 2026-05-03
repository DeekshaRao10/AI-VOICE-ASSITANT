# =========================
# 🔌 IMPORTS
# =========================
from database import init_db, seed_data, Appointment, Conversation, Doctor, get_db
init_db()
seed_data()

from fastapi import FastAPI, Depends, HTTPException
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
            "department": a.department,
            "doctor": a.doctor
        })

    pd.DataFrame(data).to_excel("appointments_summary.xlsx", index=False)


# =========================
# 📩 SMS FUNCTION (FIXED)
# =========================
def send_sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"

    params = {
        "authorization": "YOUR_API_KEY",  # 🔴 PUT YOUR KEY
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone
    }

    try:
        response = requests.get(url, params=params)
        print("SMS RESPONSE:", response.json())  # 🔥 DEBUG
    except Exception as e:
        print("SMS Failed:", e)


# =========================
# 🧠 TRIAGE
# =========================
def detect_priority(reason: str):
    urgent_keywords = ["chest pain", "breathing", "accident"]
    return "HIGH" if any(k in reason.lower() for k in urgent_keywords) else "NORMAL"


# =========================
# 👨‍⚕️ DOCTOR ASSIGNMENT
# =========================
def assign_doctor(db, department):
    return db.query(Doctor).filter(Doctor.department == department).first()


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


class LogRequest(BaseModel):
    patient_name: str
    transcript: str


# =========================
# 🚀 APIs
# =========================

# ✅ BOOK
@app.post("/appointments")
def book_appointment(request: BookAppointmentRequest, db: Session = Depends(get_db)):

    doctor = request.doctor or assign_doctor(db, request.department)
    if not doctor:
        raise HTTPException(status_code=404, detail="No doctor found")

    doctor_name = doctor if isinstance(doctor, str) else doctor.name

    appointment = Appointment(
        patient_name=request.patient_name,
        phone=request.phone,   # ✅ STORE PHONE
        department=request.department,
        reason=request.reason,
        doctor=doctor_name,
        date=request.date,
        priority=detect_priority(request.reason)
    )

    db.add(appointment)
    db.commit()

    export_appointments_to_excel(db)

    # 📩 SMS
    send_sms(request.phone,
             f"Hi {request.patient_name}, appointment confirmed with {doctor_name} on {request.date}")

    return {"message": "Booked successfully"}


# ✅ CANCEL
@app.delete("/appointments")
def cancel_appointment(patient_name: str, date: str, db: Session = Depends(get_db)):

    appointment = db.query(Appointment).filter(
        Appointment.patient_name == patient_name,
        Appointment.date == date
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    phone = appointment.phone  # ✅ FETCH FROM DB

    db.delete(appointment)
    db.commit()

    export_appointments_to_excel(db)

    send_sms(phone, f"Hi {patient_name}, your appointment on {date} is cancelled")

    return {"message": "Cancelled"}


# ✅ RESCHEDULE
@app.put("/appointments")
def reschedule_appointment(request: RescheduleRequest, db: Session = Depends(get_db)):

    appointment = db.query(Appointment).filter(
        Appointment.patient_name == request.patient_name,
        Appointment.date == request.old_date
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    phone = appointment.phone  # ✅ FETCH

    appointment.date = request.new_date
    db.commit()

    export_appointments_to_excel(db)

    send_sms(phone,
             f"Hi {request.patient_name}, appointment moved to {request.new_date}")

    return {"message": "Rescheduled"}


# =========================
# ▶️ RUN
# =========================
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)