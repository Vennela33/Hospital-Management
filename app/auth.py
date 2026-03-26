from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
SECRET_KEY = "secret"
ALGORITHM = "HS256"


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

