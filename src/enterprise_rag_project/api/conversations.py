
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from enterprise_rag_project.auth.dependencies import get_current_user
from enterprise_rag_project.db.models import User, Conversation, Message
from enterprise_rag_project.db.connection import get_db
from enterprise_rag_project.services.generate_conversation_title import (
    generate_conversation_title,
)


router = APIRouter()


# -------------------------
# Request models
# -------------------------

class ChatRequest(BaseModel):
    query: str
    thread_id: str


class ChatResumeRequest(BaseModel):
    thread_id: str
    selected_document_id: Optional[int] = None
    decision: Optional[bool] = None


# -------------------------
# Response model
# -------------------------

class ChatResponse(BaseModel):
    status: str
    answer: Optional[str] = None
    citations: list[dict] = Field(default_factory=list)
    thread_id: str
    message: Optional[str] = None
    question: Optional[str] = None
    documents: list[dict] = Field(default_factory=list)


# -------------------------
# Helper functions
# -------------------------

def get_conversation(db: Session, thread_id: str, user_id: int):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.thread_id == thread_id,
            Conversation.user_id == user_id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


def get_graph_config(thread_id: str, user_id: int, endpoint: str):
    return {
        "configurable": {
            "thread_id": thread_id,
        },
        "metadata": {
            "user_id": user_id,
            "thread_id": thread_id,
            "endpoint": endpoint,
        },
        "tags": [
            "enterprise-rag",
            "chat",
        ],
    }


def get_interrupt_response(result: dict):
    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return None

    interrupt_data = getattr(interrupts[0], "value", interrupts[0])

    if not isinstance(interrupt_data, dict):
        return {
            "type": "human_review",
            "question": "Please provide your decision.",
            "documents": [],
        }

    return interrupt_data


def build_pending_response(
    interrupt_data: dict,
    thread_id: str,
):
    interrupt_type = interrupt_data.get("type")

    status = (
        "document_selection"
        if interrupt_type == "document_selection"
        else "human_review"
    )

    return {
        "status": status,
        "answer": None,
        "citations": [],
        "thread_id": thread_id,
        "message": interrupt_data.get("question"),
        "question": interrupt_data.get("question"),
        "documents": interrupt_data.get("documents", []),
    }


def save_assistant_message(
    db: Session,
    conversation_id: int,
    answer: str,
):
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
    )

    db.add(assistant_message)
    db.commit()


# -------------------------
# Start chat
# -------------------------

@router.post("/chat", response_model=ChatResponse)
def chat(
    request_data: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation(
        db,
        request_data.thread_id,
        current_user.id,
    )

    if not conversation.title:
        conversation.title = generate_conversation_title(
            request_data.query
        )
        db.commit()

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request_data.query,
    )

    db.add(user_message)
    db.commit()

    initial_state = {
        "query": request_data.query,
        "user_id": current_user.id,
        "thread_id": request_data.thread_id,

        "messages": [
            HumanMessage(content=request_data.query)
        ],

        "contextualized_query": "",
        "documents": [],
        "reranked_documents": [],
        "selected_documents": [],

        "context_status": "insufficient",
        "retry_count": 0,

        "answer": "",
        "grounding_status": "not_grounded",
        "generation_attempts": 0,

        "citations": [],
        "human_decision": None,
    }

    config = get_graph_config(
        request_data.thread_id,
        current_user.id,
        "/chat",
    )

    graph = request.app.state.graph

    result = graph.invoke(
        initial_state,
        config=config,
    )

    # Check whether LangGraph paused for user input.
    interrupt_data = get_interrupt_response(result)

    if interrupt_data:
        return build_pending_response(
            interrupt_data,
            request_data.thread_id,
        )

    answer = result.get("answer")

    if answer is None:
        raise HTTPException(
            status_code=500,
            detail="Graph completed without generating an answer.",
        )

    save_assistant_message(
        db,
        conversation.id,
        answer,
    )

    return {
        "status": "completed",
        "answer": answer,
        "citations": result.get("citations", []),
        "thread_id": request_data.thread_id,
    }


# -------------------------
# Resume interrupted graph
# -------------------------

@router.post("/chat/resume", response_model=ChatResponse)
def chat_resume(
    request_data: ChatResumeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation(
        db,
        request_data.thread_id,
        current_user.id,
    )

    # Determine what the user is responding to.
    if request_data.selected_document_id is not None:
        resume_value = {
            "selected_document_id": request_data.selected_document_id
        }

    elif request_data.decision is not None:
        resume_value = request_data.decision

    else:
        raise HTTPException(
            status_code=400,
            detail="Provide selected_document_id or decision.",
        )

    config = get_graph_config(
        request_data.thread_id,
        current_user.id,
        "/chat/resume",
    )

    graph = request.app.state.graph

    result = graph.invoke(
        Command(resume=resume_value),
        config=config,
    )

    # The graph may request further clarification.
    interrupt_data = get_interrupt_response(result)

    if interrupt_data:
        return build_pending_response(
            interrupt_data,
            request_data.thread_id,
        )

    answer = result.get("answer")

    if answer is None:
        raise HTTPException(
            status_code=500,
            detail="Graph completed without generating an answer.",
        )

    save_assistant_message(
        db,
        conversation.id,
        answer,
    )

    return {
        "status": "completed",
        "answer": answer,
        "citations": result.get("citations", []),
        "thread_id": request_data.thread_id,
    }
