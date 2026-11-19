from langgraph.types import interrupt
from enterprise_rag_project.agents.state import RAGState

def human_document_review(state: RAGState):

    available_documents = state.get("available_documents", [])

    question = (
        "I found multiple relevant documents. "
        "Which document would you like me to use?"
    )

    response = interrupt({
        "type": "document_selection",
        "question": question,
        "documents": available_documents,
    })

    # The API should resume the graph with a document ID.
    if isinstance(response, dict):
        selected_document_id = response.get("selected_document_id")
    else:
        selected_document_id = response

    valid_ids = {
        doc["document_id"]
        for doc in available_documents
    }

    if selected_document_id not in valid_ids:
        raise ValueError("Invalid document selection.")

    return {
        "selected_document_id": selected_document_id,
        "document_status": "found",
    }   