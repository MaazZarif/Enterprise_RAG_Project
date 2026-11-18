import uuid

from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.db.models import Conversation, User,Message
from enterprise_rag_project.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post("")
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread_id = str(uuid.uuid4())

    conversation = Conversation(
        user_id=current_user.id,
        thread_id=thread_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "conversation_id": conversation.id,
        "thread_id": conversation.thread_id,
    }


@router.get("")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id
        )
        .order_by(Conversation.created_at.desc())
        .all()
    )  
    

    return conversations
    
    
    
    
@router.get("/{thread_id}")
def get_conversation(
    thread_id:str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
            db.query(Conversation)
            .filter(
                Conversation.thread_id == thread_id,
                Conversation.user_id == current_user.id
            )
            .first()
        )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    
    messages = db.query(Message).filter(Message.conversation_id == conversation.id )

    

    

    return {
        "conversation_id":conversation.id,
        "thread_id": conversation.thread_id,
        "messages":[
            {
                "role":message.role,
                "content":message.content
            }
            for message in messages
        ],  
    }