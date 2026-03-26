from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,Depends
from app import models
from app.dependencies import verify_token
from sqlalchemy import func


def create_billing(db, data,user):
    if user['role']!="admin":
        raise HTTPException(status_code=403,detail="Only admin can create")
    doctor = db.query(models.Doctor).filter(
        models.Doctor.id == data.doctor_id
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")
    patient = db.query(models.Patient).filter(
        models.Patient.id == data.patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if data.appointment_id:
        appointment = db.query(models.Appointment).filter(
            models.Appointment.id == data.appointment_id
        ).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.doctor_id != data.doctor_id or appointment.patient_id != data.patient_id:
            raise HTTPException(status_code=400, detail="Appointment mismatch")
        if appointment.status == "cancelled":
            raise HTTPException(status_code=400, detail="Cannot bill cancelled appointment")
        existing = db.query(models.Billing).filter(
            models.Billing.appointment_id == data.appointment_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Billing already exists for this appointment")
    total = data.consultation_fee + data.additional_charges
    billing = models.Billing(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        appointment_id=data.appointment_id,
        consultation_fee=data.consultation_fee,
        additional_charges=data.additional_charges,
        total_amount=total,
        payment_mode=data.payment_mode
    )
    db.add(billing)
    if appointment:
        appointment.status='completed'
    try:
        db.commit()
        db.refresh(billing)
        return billing
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")


def get_billings(
    db,
    payment_status=None,
    doctor_id=None,
    patient_id=None,
    start_date=None,
    end_date=None,
    page=1,
    limit=10 ):
    query = db.query(models.Billing).filter(models.Billing.is_active == True)
    if payment_status:
        query = query.filter(models.Billing.payment_status == payment_status)
    if doctor_id:
        query = query.filter(models.Billing.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(models.Billing.patient_id == patient_id)
    if start_date and end_date:
        query = query.filter(models.Billing.created_at.between(start_date, end_date))
    total = query.count()
    data = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }


def get_billing(db, billing_id):
    billing = db.query(models.Billing).filter(models.Billing.id == billing_id,models.Billing.is_active == True).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")
    return billing


def update_billing(db, billing_id, data,user):
    if user['role']!="admin":
        raise HTTPException(status_code=403, detail="Only admin can update")
    billing = get_billing(db, billing_id)
    billing.consultation_fee = data.consultation_fee
    billing.additional_charges = data.additional_charges
    billing.payment_status = data.payment_status
    billing.total_amount = billing.consultation_fee + billing.additional_charges
    db.commit()
    db.refresh(billing)
    return billing


def update_billing_partial(db, billing_id, data,user):
    if user['role']!='admin':
        raise HTTPException(status_code=403, detail="Only admin can update")
    billing = get_billing(db, billing_id)
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(billing, key, value)
    billing.total_amount = billing.consultation_fee + billing.additional_charges
    db.commit()
    db.refresh(billing)
    return billing


def delete_billing(db, billing_id,user):
    if user['role']!='admin':
        raise HTTPException(status_code=403,detail="Only admin can delete")
    billing = get_billing(db, billing_id)
    billing.is_active = False
    db.commit()
    return {"message": "Billing deleted"}


def get_billings_by_patient(db, patient_id):
    return db.query(models.Billing).filter(
        models.Billing.patient_id == patient_id
    ).all()


def get_billings_by_doctor(db, doctor_id):
    return db.query(models.Billing).filter(
        models.Billing.doctor_id == doctor_id,
        models.Billing.is_active == True
    ).all()


def revenue_per_doctor(db):
    result = db.query(
        models.Billing.doctor_id,
        func.sum(models.Billing.total_amount).label("total_revenue")
    ).group_by(models.Billing.doctor_id).all()

    return  [
        {
            "doctor_id": str(r[0]),
            "total_revenue": float(r[1])
        }
        for r in result
    ]
    

def revenue_per_day(db):
    result = db.query(
        func.date(models.Billing.created_at),
        func.sum(models.Billing.total_amount)
    ).group_by(func.date(models.Billing.created_at)).all()

    return [
        {
            "date": str(r[0]),
            "total_revenue": float(r[1])
        }
        for r in result
    ]
    

def revenue_report(db, doctor_id=None, start=None, end=None):
    query = db.query(func.sum(models.Billing.total_amount))
    if doctor_id:
        query = query.filter(models.Billing.doctor_id == doctor_id)
    if start and end:
        query = query.filter(
            models.Billing.created_at.between(start, end)
        )
    total = query.scalar()
    return {"total_revenue": total or 0}