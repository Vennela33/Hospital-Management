from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float ,DateTime,UniqueConstraint
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)
    updated_by = Column(String)
    patients=relationship("Patient",back_populates="doctor")
    appointments=relationship("Appointment",back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String, nullable=False)
    doctor_id=Column(Integer,ForeignKey("doctors.id"))
    doctor=relationship("Doctor",back_populates="patients")
    appointments=relationship("Appointment",back_populates="patient")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)
    updated_by = Column(String)


class Appointment(Base):
    __tablename__="appointments"

    id=Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    appointment_date = Column(DateTime)
    status = Column(String, default="scheduled")
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

class Billing(Base):
    __tablename__ = "billings"
    __table_args__ = (
        UniqueConstraint('appointment_id', name='unique_appointment_billing'),)

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    consultation_fee = Column(Float)
    additional_charges = Column(Float, default=0)
    total_amount = Column(Float)
    payment_status = Column(String, default="pending")  # pending, paid, cancelled
    payment_mode = Column(String)  # cash, card, upi
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)