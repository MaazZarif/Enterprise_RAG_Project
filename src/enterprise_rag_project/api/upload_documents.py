from fastapi import APIRouter,UploadFile,File,HTTPException,Depends
from pydantic import BaseModel,Field
from pathlib import Path
import shutil
from enterprise_rag_project.ingestion.ingest_pipeline import ingest_pipeline
from enterprise_rag_project.db.models import Document
from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.auth.dependencies import get_current_user
from enterprise_rag_project.db.models import User
from sqlalchemy.orm import Session
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)



@router.post("/documents/upload")
def upload_documents(file: UploadFile = File(...),db:Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    allowed_extensions = {".pdf",".docx"}
    user_id = current_user.id

    suffix  = Path(file.filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    file_path = UPLOAD_DIR/file.filename 

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    document = Document(
        user_id = user_id,
        filename=file.filename,
        file_type = suffix,
        status = "processing"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        ids = ingest_pipeline(
            file_path=str(file_path),
            document_id=document.id,
            user_id=user_id,
        )

        document.status = "ready"
        db.commit()

    except Exception:
        document.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed")
        

    return {
        "message": "Document uploaded successfully",
        "filename": document.filename,
        "document_id": document.id,
        "chunks_created": len(ids),
    }



