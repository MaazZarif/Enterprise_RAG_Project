from fastapi import APIRouter, Depends
from enterprise_rag_project.db.connection import get_db
from sqlalchemy.orm import Session
from enterprise_rag_project.auth.dependencies import get_current_user
from enterprise_rag_project.db.models import Document, User


router = APIRouter()


@router.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return documents