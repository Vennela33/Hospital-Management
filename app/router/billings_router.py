from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas
from app.dependencies import verify_token, admin_required, doctor_required
from app import models
from app.services import billing
from datetime import datetime
from fastapi.responses import FileResponse

router = APIRouter(prefix="/billings", tags=["Billings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/",dependencies=[Depends(admin_required)])
def create(data: schemas.BillingCreate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return billing.create_billing(db, data,user)

@router.get("/{billing_id}",dependencies=[Depends(verify_token)])
def get_one(billing_id: int, db: Session = Depends(get_db)):
    return billing.get_billing(db, billing_id)

@router.put("/{billing_id}",dependencies=[Depends(admin_required)])
def update(billing_id: int, data: schemas.BillingUpdate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return billing.update_billing(db, billing_id, data,user)

@router.patch("/{billing_id}",dependencies=[Depends(admin_required)])
def update_partial(billing_id: int, data: schemas.BillingUpdate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return billing.update_billing_partial(db, billing_id, data,user)

@router.delete("/{billing_id}",status_code=200,dependencies=[Depends(admin_required)])
def delete(billing_id: int, db: Session = Depends(get_db),user=Depends(verify_token)):
    return billing.delete_billing(db, billing_id,user)

@router.get("/doctors/{doctor_id}/billing")
def doctor_billings(
    doctor_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    if user["role"] == "doctor" and str(doctor_id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return billing.get_billings_by_doctor(db, doctor_id)


@router.get("/patients/{patient_id}/billing", status_code=200,dependencies=[Depends(verify_token)])
def get_billings_by_patient(patient_id: int, db: Session = Depends(get_db)):
    return db.query(models.Billing).filter(
        models.Billing.patient_id == patient_id
    ).all()

@router.get("/",dependencies=[Depends(verify_token)])
def list_all_billings(
    payment_status: str = Query(None),
    doctor_id: int = Query(None),
    patient_id: int = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return billing.get_billings(
        db,
        payment_status,
        doctor_id,
        patient_id,
        start_date,
        end_date,
        page,
        limit
    )

@router.post("/{billing_id}/pay")
def make_payment(
    billing_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    billing = db.query(models.Billing).filter(models.Billing.id == billing_id).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")

    if billing.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Already paid")
    billing.payment_status = "paid"

    db.commit()
    db.refresh(billing)

    return {
        "message": "Payment successful",
        "billing_id": billing.id,
        "status": billing.payment_status
    }