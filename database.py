import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# =========================
# 🔧 DATABASE CONFIG
# =========================
DATABASE_URL = "sqlite:///./hospital.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# =========================
# 👨‍⚕️ DOCTOR TABLE
# =========================
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)
    available_slots = Column(String)  # Example: "10AM,2PM,4PM"


# =========================
# 📅 APPOINTMENT TABLE
# =========================
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)

    phone = Column(String)  # ✅ ADDED (VERY IMPORTANT)

    department = Column(String)
    reason = Column(String)
    doctor = Column(String, nullable=True)

    date = Column(String, index=True)
    priority = Column(String, default="NORMAL")

    created_at = Column(DateTime, default=dt.datetime.utcnow)



# ✅ Conversation Table
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    transcript = Column(String)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)


# =========================
# 🔧 INIT DB
# =========================
def init_db():
    Base.metadata.create_all(bind=engine)


# =========================
# 🌱 SEED DOCTOR DATA
# =========================
def seed_data():
    db = SessionLocal()

    if not db.query(Doctor).first():
        doctors = [
            Doctor(name="Dr. Aruna C Ramesh",        department="Accident & Emergency",      available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Gurappa Shetty Gojanur", department="Cardiology",                available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Anupama V Hegde",        department="Cardiology",                available_slots="10AM,1PM,3PM"),
            Doctor(name="Dr. Deepak T S",             department="Critical Care Medicine",    available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. T. K. Sumathy",          department="Dermatology & Cosmetology", available_slots="10AM,12PM,3PM"),
            Doctor(name="Dr. Chandrakiran C",         department="ENT",                       available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Pramila Kalra",          department="Endocrinology",             available_slots="10AM,1PM,4PM"),
            Doctor(name="Dr. Shaikh Mohammed Aslam S",department="General Medicine",          available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Shashank G",             department="General Surgery",           available_slots="9AM,12PM,3PM"),
            Doctor(name="Dr. Mahendra J V",           department="Neurology",                 available_slots="10AM,1PM,4PM"),
            Doctor(name="Dr. A. S. Hegde",            department="Neurosurgery",              available_slots="9AM,11AM,2PM"),
            Doctor(name="Dr. Jyothi G S",             department="Obstetrics & Gynecology",   available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Ravikumar T V",          department="Orthopaedics",              available_slots="10AM,12PM,3PM"),
            Doctor(name="Dr. Prasad Mylarappa",       department="Urology",                   available_slots="9AM,11AM,2PM,4PM"),
            Doctor(name="Dr. Sanjay C Desai",         department="Vascular Surgery",          available_slots="10AM,1PM,3PM"),
        ]

        db.add_all(doctors)
        db.commit()

    db.close()


# =========================
# 🔌 DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ▶️ RUN FILE DIRECTLY
# =========================
if __name__ == "__main__":
    init_db()
    seed_data()