from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas
from app.dependencies import verify_token, admin_required, doctor_required
from app import models
from app.services import billing
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/revenue",dependencies=[Depends(verify_token)])
def get_revenue(
    doctor_id: int = None,
    from_date: datetime = None,
    to_date: datetime = None,
    db: Session = Depends(get_db)
):
    return billing.revenue_report(db, doctor_id, from_date, to_date)

@router.get("/revenue/doctor",dependencies=[Depends(verify_token)])
def revenue_doctor(db: Session = Depends(get_db)):
    return billing.revenue_per_doctor(db)

@router.get("/revenue/day",dependencies=[Depends(verify_token)])
def revenue_day(db: Session = Depends(get_db)):
    return billing.revenue_per_day(db)


