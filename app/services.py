from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,Depends
from app import models
from app.dependencies import verify_token



def create_doctor(db: Session, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Create")
    existing = db.query(models.Doctor).filter(models.Doctor.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    doctor = models.Doctor(**data.dict(),created_by=user.get("sub"),updated_by=user.get("sub"))
    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def get_doctors(db, specialization=None, is_active=None,page: int=1, limit:int=10):
    query = db.query(models.Doctor)

    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))

    if is_active is not None:
        query = query.filter(models.Doctor.is_active == is_active)
    
    offset=(page-1)*limit
    return query.offset(offset).limit(limit).all()


def get_doctors_with_patients(db: Session):
    return db.query(models.Doctor).options(joinedload(models.Doctor.patients)).all()


def update_doctor_full(db: Session, doctor_id: int, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can update")
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.name = data.name
    doctor.specialization = data.specialization
    doctor.email = data.email
    doctor.is_active = data.is_active
    doctor.updates_by=user.get("sub")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_Code=400, detail="Email already exists")
    db.refresh(doctor)
    return doctor



def update_doctor_partial(db, doctor_id, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can update")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    doctor.updated_by=user.get("sub")
    db.commit()
    db.refresh(doctor)
    return doctor



def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor(db, doctor_id)
    doctor.is_active = False
    db.commit()

    return {"message": "Doctor deactivated successfully"}



def create_patient(db: Session, data,user):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == data.doctor_id).first()
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Create")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor is inactive")

    patient = models.Patient(**data.dict(),created_by=user.get("sub"),updated_by=user.get("sub"))
    db.add(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry")
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_patients(db: Session, age_gt=None,page: int=1, limit:int=10):
    query = db.query(models.Patient)

    if age_gt:
        query = query.filter(models.Patient.age == age_gt)
    offset=(page-1)*limit
    return query.offset(offset).limit(limit).all()

def get_patients_by_doctor(db: Session, doctor_id: int,user):
    doctor = get_doctor(db, doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")
    if user["role"]=="doctor" and user["sub"]!=str(doctor_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return db.query(models.Patient).filter(models.Patient.doctor_id==doctor_id).all()



def update_patient_full(db: Session, patient_id: int, data,user):
    patient = get_patient(db, patient_id)
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Update")
    doctor = get_doctor(db, data.doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")

    patient.name = data.name
    patient.age = data.age
    patient.phone = data.phone
    patient.doctor_id = data.doctor_id
    patient.updated_by=user.get("sub")
    db.commit()
    db.refresh(patient)
    return patient



def update_patient_partial(db, patient_id, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Update")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_data = data.dict(exclude_unset=True)
    if "doctor_id" in update_data:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == update_data["doctor_id"]).first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        if not doctor.is_active:
            raise HTTPException(status_code=400, detail="Doctor inactive")
    for key, value in update_data.items():
        setattr(patient, key, value)
    patient.updated_by=user.get("sub")
    db.commit()
    db.refresh(patient)
    return patient



def delete_patient(db: Session, patient_id: int,user=Depends(verify_token)):
    patient = get_patient(db, patient_id)
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Delete")
    db.delete(patient)
    db.commit()

    return {"message": "Patient deleted successfully"}




def paginate(query, page: int, limit: int):
    total = query.count()
    data = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }

def create_appointment(db, data):
    doctor = get_doctor(db, data.doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")

    patient = get_patient(db, data.patient_id)
    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == data.doctor_id,
        models.Appointment.appointment_date == data.appointment_date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Slot already booked")

    appointment = models.Appointment(**data.dict())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment

def get_appointments(db):
    return db.query(models.Appointment).all()

def get_appointment(db, appointment_id):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment

def update_appointment(db, appointment_id, data,user):
    if user['role']!='admin':
        raise HTTPException(status_code=403,detail="Only admin can update")
    appointment = get_appointment(db, appointment_id)
    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)

    return appointment

def delete_appointment(db, appointment_id):
    appointment = get_appointment(db, appointment_id)

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment deleted"}

def test_create_doctor():
    response = client.post("/doctors", json={...})
    assert response.status_code == 200


def get_patients(db):
    return db.query(models.Patient).options(
        joinedload(models.Patient.doctor)
    ).all()