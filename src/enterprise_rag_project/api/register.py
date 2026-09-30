from fastapi import APIRouter, Depends, HTTPException
from enterprise_rag_project.auth.schema import UserResponse,RegisterRequest
from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.db.models import User
from sqlalchemy.orm import Session
from enterprise_rag_project.auth.security import hash_password



router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse)
def register(request:RegisterRequest,db:Session=Depends(get_db)):

    existing_user = db.query(User).filter(User.email==request.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email = request.email,
        hashed_password= hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
