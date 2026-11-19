
from langgraph.types import interrupt
from enterprise_rag_project.agents.state import RAGState


def human_document_review(state: RAGState):

    available_documents = state.get("available_documents", [])
    retrieved_documents = state.get("reranked_documents", [])

    # Get document IDs found in retrieved chunks.
    candidate_ids = {
        doc.metadata.get("document_id")
        for doc in retrieved_documents
        if doc.metadata.get("document_id") is not None
    }

    # Only show documents represented in retrieval results.
    candidates = [
        doc for doc in available_documents
        if doc["document_id"] in candidate_ids
    ]

    # No relevant document was retrieved.
    if not candidates:
        return {
            "document_status": "missing",
            "clarification_question": (
                "I couldn't find relevant information in your uploaded "
                "documents. Please upload the document you want me to use."
            ),
        }

    response = interrupt({
        "type": "document_selection",
        "question": "Which document are you referring to?",
        "documents": candidates,
    })

    if isinstance(response, dict):
        selected_document_id = response.get("selected_document_id")
    else:
        selected_document_id = response

    valid_ids = {
        doc["document_id"] for doc in candidates
    }

    if selected_document_id not in valid_ids:
        raise ValueError("Invalid document selection.")

    return {
        "selected_document_id": selected_document_id,
        "document_status": "found",
    }
