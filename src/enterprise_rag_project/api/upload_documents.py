
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Form,
)
from pathlib import Path
import shutil

from sqlalchemy.orm import Session

from enterprise_rag_project.ingestion.ingest_pipeline import ingest_pipeline
from enterprise_rag_project.db.models import Document, Conversation, User
from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.auth.dependencies import get_current_user


router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/documents/upload")
def upload_documents(
    file: UploadFile = File(...),
    thread_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_extensions = {".pdf", ".docx"}

    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    # Verify that this conversation belongs to the logged-in user.
    conversation = db.query(Conversation).filter(
        Conversation.thread_id == thread_id,
        Conversation.user_id == current_user.id,
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    document = Document(
        user_id=current_user.id,
        conversation_id=conversation.id,
        filename=Path(file.filename).name,
        file_type=suffix,
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    document_dir = UPLOAD_DIR / f"user_{current_user.id}"
    document_dir.mkdir(parents=True, exist_ok=True)

    file_path = document_dir / f"document_{document.id}{suffix}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ids = ingest_pipeline(
            file_path=str(file_path),
            document_id=document.id,
            user_id=current_user.id,
            thread_id=thread_id,
        )

        document.status = "ready"
        db.commit()

    except Exception as exc:
        db.rollback()

        failed_document = db.query(Document).filter(
            Document.id == document.id
        ).first()

        if failed_document:
            failed_document.status = "failed"
            db.commit()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        ) from exc

    finally:
        file.file.close()

    return {
        "message": "Document uploaded successfully",
        "filename": document.filename,
        "document_id": document.id,
        "thread_id": thread_id,
        "chunks_created": len(ids),
    }
