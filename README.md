# Hospital API

A simple REST API built using FastAPI to manage Doctors and Patients.

##  Tech Stack

- Python 3.9+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT (python-jose)
- Uvicorn
- Docker

## Project Structure

hospital_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── routes/
│   │   ├── doctors.py
│   │   └── patients.py
│
├── README.md
└── requirements.txt


##  Features

###  Doctor Management
- Create, update (PUT, PATCH), and soft delete doctors
- Unique email validation
- Filter by specialization and active status

###  Patient Management
- Assign patients to doctors (One-to-Many relationship)
- Prevent assignment to non-existing or inactive doctors
- CRUD operations for patients

###  Relationship API
- Get all patients for a specific doctor:
  GET /api/v1/doctors/{doctor_id}/patients

###  Validation
- Email validation using Pydantic
- Age must be > 0
- Phone must be exactly 10 digits

###  Pagination
- page & limit support
- Returns total records

###  Filtering
- Doctors:
  - /doctors?specialization=cardiology
  - /doctors?is_active=true
- Patients:
  - /patients?age_gt=30

###  Authentication
- JWT-based authentication
- Login endpoint
- Protected APIs

###  Production Features
- Modular structure (routes, services)
- SQLite database (SQLAlchemy)
- Environment variables
- CORS enabled

---
## Setup Instructions

### 1. Create virtual environment
python -m venv venv

### 2. Install dependencies
pip install -r requirements.txt