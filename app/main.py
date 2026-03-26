from fastapi import FastAPI,HTTPException,Request
from app.database import engine
from app import models
from app.router import doctors, patients,Appointments
from app.auth import create_token
import time
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital API v1",description="API for managing doctors, patients, and appointments",version="1.0.0")

@app.middleware("http")
async def log_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "details": str(exc)
        }
    )
@app.post("/doctors", summary="Create a doctor", description="Add new doctor")

@app.post("/login")
def login(username: str, password: str):
    if username == "admin":
        role="admin"
    elif username=='doctor':
        role='doctor'
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": username,"role":role})

    return {"access_token": token, "token_type": "bearer"}
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(Appointments.router)


