from fastapi import APIRouter, Depends, HTTPException
from enterprise_rag_project.auth.schema import UserResponse,RegisterRequest
from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.db.models import User
from sqlalchemy.orm import Session
from enterprise_rag_project.auth.security import hash_password
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm




from enterprise_rag_project.auth.security import (
    verify_password,
    create_access_token,
)


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }