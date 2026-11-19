
from sqlalchemy.orm import Session

from enterprise_rag_project.db.connection import SessionLocal
from enterprise_rag_project.db.models import Document, Conversation
from enterprise_rag_project.agents.state import RAGState


def document_resolver(state: RAGState):
    db: Session = SessionLocal()

    try:
        conversation = db.query(Conversation).filter(
            Conversation.thread_id == state["thread_id"],
            Conversation.user_id == state["user_id"],
        ).first()

        if conversation is None:
            return {
                "available_documents": [],
                "document_status": "missing",
                "selected_document_id": None,
                "requested_document": None,
            }

        documents = db.query(Document).filter(
            Document.conversation_id == conversation.id,
            Document.user_id == state["user_id"],
            Document.status == "ready",
        ).all()

        available_documents = [
            {
                "document_id": doc.id,
                "filename": doc.filename,
            }
            for doc in documents
        ]

        return {
            "available_documents": available_documents,
        }

    finally:
        db.close()
