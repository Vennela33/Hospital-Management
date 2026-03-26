'''from sqlalchemy.orm import Session
from app import models


def create_doctor(db: Session, doctor):
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def get_doctors(db: Session):
    return db.query(models.Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


def create_patient(db: Session, patient):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def get_patients(db: Session):
    return db.query(models.Patient).all()'''