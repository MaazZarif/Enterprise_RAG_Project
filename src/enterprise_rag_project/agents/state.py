
from typing import TypedDict, Annotated, Literal
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RAGState(TypedDict, total=False):

    # User and conversation
    query: str
    user_id: int
    thread_id: str

    # Conversation history
    messages: Annotated[list[BaseMessage], add_messages]

    # Query processing
    route: Literal["rag", "direct"]
    contextualized_query: str

    # Retrieval and reranking
    documents: list[Document]
    reranked_documents: list[Document]
    selected_documents: list[Document]

    # Document resolution
    available_documents: list[dict]
    selected_document_id: int | None
    document_status: Literal[
        "found",
        "missing",
        "ambiguous",
        "not_required",
    ]

    clarification_question: str | None
    requested_document: str | None
    document_clarification: str | None
    document_selection_response: dict | int | None

    # Context evaluation
    context_status: Literal[
        "sufficient",
        "insufficient",
    ]

    # Answer generation
    answer: str
    generation_attempts: int

    # Grounding verification
    grounding_status: Literal[
        "grounded",
        "not_grounded",
    ]
    unsupported_claims: list[str]

    # Human review
    human_decision: bool | None

    # Retry and citations
    retry_count: int
    citations: list[dict]
