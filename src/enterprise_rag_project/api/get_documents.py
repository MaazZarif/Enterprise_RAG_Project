
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.auth.dependencies import get_current_user
from enterprise_rag_project.db.models import Document, Conversation, User


router = APIRouter()


@router.get("/documents")
def get_documents(
    thread_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify conversation ownership
    conversation = db.query(Conversation).filter(
        Conversation.thread_id == thread_id,
        Conversation.user_id == current_user.id,
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.conversation_id == conversation.id,
        )
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status,
            "created_at": document.created_at,
        }
        for document in documents
    ]
