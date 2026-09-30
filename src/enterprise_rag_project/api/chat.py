from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field 
from typing import List
from fastapi import Request
from enterprise_rag_project.auth.dependencies import get_current_user
from enterprise_rag_project.db.models import User,Conversation,Message
from sqlalchemy.orm import Session
from enterprise_rag_project.db.connection import get_db
from langchain_core.messages import HumanMessage
from enterprise_rag_project.services.generate_conversation_title import generate_conversation_title



router = APIRouter()


class ChatRequest(BaseModel):
    query:str
    thread_id:str


class ChatResponse(BaseModel):
    answer:str
    citations: List[dict]
    thread_id:str



@router.post("/chat",response_model=ChatResponse)
def chat(
    request_data: ChatRequest,
    request:Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.thread_id == request_data.thread_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
    
    if not conversation.title:
        title = generate_conversation_title(request_data.query)
        conversation.title = title
        db.commit()


    user_message = Message(
        conversation_id = conversation.id,
        role = "user",
        content = request_data.query
    )
    db.add(user_message)
    db.commit()

    
    initial_state = {
        "query": request_data.query,
        "user_id": current_user.id,

        "messages": [
            HumanMessage(content=request_data.query)
        ],

        "contextualized_query": "",
        "rewritten_query": "",

        "documents": [],
        "reranked_documents": [],

        "context_status": "insufficient",
        "retry_count": 0,

        "answer": "",
        "grounding_status": "not_grounded",
        "generation_attempts": 0,

        "citations": [],
    }

    config = {
    "configurable": {
        "thread_id": request_data.thread_id
    },
    "metadata": {
        "user_id": current_user.id,
        "thread_id": request_data.thread_id,
        "endpoint": "/chat",
    },
    "tags": [
        "enterprise-rag",
        "chat"
    ]
}
    graph = request.app.state.graph

    result = graph.invoke(
        initial_state,
        config=config
    )

    assistant_message = Message(
        conversation_id = conversation.id,
        role = "assistant",
        content = result["answer"]
        )
    
    db.add(assistant_message)
    db.commit()

    return {
        "answer": result["answer"],
        "citations": result.get("citations", []),
        "thread_id": request_data.thread_id,
    }