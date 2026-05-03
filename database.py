import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./hospital.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ✅ Appointment Table
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    department = Column(String)
    reason = Column(String)
    doctor = Column(String, nullable=True)
    date = Column(String, index=True)
    priority = Column(String, default="NORMAL")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


# ✅ Doctor Table
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    department = Column(String, index=True)


# ✅ Conversation Table
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    transcript = Column(String)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)


# ✅ Create Tables
def init_db():
    Base.metadata.create_all(bind=engine)

# ✅ Seed Data
def seed_data():
    db = SessionLocal()
    try:
        if db.query(Doctor).count() == 0:
            sample_doctors = [
                Doctor(name="Dr. Arjun Dev", department="Cardiology"),
                Doctor(name="Dr. Priya Sharma", department="Cardiology"),
                Doctor(name="Dr. Ravi Kumar", department="Neurology"),
                Doctor(name="Dr. Sneha Rao", department="Neurology"),
                Doctor(name="Dr. Vikram Singh", department="Orthopaedics"),
                Doctor(name="Dr. Ananya Iyer", department="Orthopaedics"),
                Doctor(name="Dr. Sanjay Gupta", department="General Medicine"),
                Doctor(name="Dr. Meera Reddy", department="General Medicine"),
                Doctor(name="Dr. Kishore Bhatt", department="Accident & Emergency"),
                Doctor(name="Dr. Lakshmi Nair", department="Obstetrics & Gynecology"),
            ]
            db.add_all(sample_doctors)
            db.commit()
    finally:
        db.close()


# ✅ DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Run directly to create DB
if __name__ == "__main__":
    init_db()
    seed_data()