from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import os
import jwt




SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
):
    return password_hash.verify(
        plain_password,
        hashed_password
    )

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )