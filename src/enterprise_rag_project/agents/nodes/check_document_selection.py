
from enterprise_rag_project.agents.state import RAGState


def check_document_selection(state: RAGState):
    available_documents = state.get("available_documents", [])
    retrieved_documents = state.get("reranked_documents", [])

    # No documents uploaded in this conversation.
    if not available_documents:
        return {
            "document_status": "missing",
            "selected_document_id": None,
            "selected_documents": [],
            "clarification_question": (
                "I couldn't find any uploaded documents in this conversation. "
                "Please upload the document you want me to use."
            ),
        }

    query = (
        state.get("contextualized_query")
        or state.get("query", "")
    ).lower()

    # Check whether the user explicitly mentioned a filename.
    matched_documents = [
        doc for doc in available_documents
        if doc["filename"].lower() in query
    ]

    if len(matched_documents) == 1:
        selected_id = matched_documents[0]["document_id"]

    elif len(matched_documents) > 1:
        return {
            "document_status": "ambiguous",
            "selected_document_id": None,
            "selected_documents": [],
        }

    else:
        # Identify documents represented in retrieval results.
        retrieved_ids = {
            doc.metadata.get("document_id")
            for doc in retrieved_documents
            if doc.metadata.get("document_id") is not None
        }

        if len(retrieved_ids) == 0:
            return {
                "document_status": "missing",
                "selected_document_id": None,
                "selected_documents": [],
                "clarification_question": (
                    "I couldn't find relevant information in your uploaded "
                    "documents. Please upload the document you want me to use."
                ),
            }

        elif len(retrieved_ids) == 1:
            selected_id = next(iter(retrieved_ids))

        else:
            return {
                "document_status": "ambiguous",
                "selected_document_id": None,
                "selected_documents": [],
            }

    selected_documents = [
        doc for doc in retrieved_documents
        if doc.metadata.get("document_id") == selected_id
    ]

    return {
        "document_status": "found",
        "selected_document_id": selected_id,
        "selected_documents": selected_documents,
    }
