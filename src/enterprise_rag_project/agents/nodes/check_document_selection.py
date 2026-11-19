from enterprise_rag_project.agents.state import RAGState

def check_document_selection(state: RAGState):
    available_documents = state.get("available_documents", [])
    retrieved_documents = state.get("reranked_documents", [])

    # No documents are uploaded in this conversation.
    if not available_documents:
        return {
            "document_status": "missing",
            "selected_document_id": None,
            "selected_documents": [],
        }

    query = state.get("contextualized_query") or state.get("query", "")
    query_lower = query.lower()

    # First, check whether the user explicitly mentioned a filename.
    matched_documents = [
        doc for doc in available_documents
        if doc["filename"].lower() in query_lower
    ]

    if len(matched_documents) == 1:
        return {
            "document_status": "found",
            "selected_document_id": matched_documents[0]["document_id"],
        }

    if len(matched_documents) > 1:
        return {
            "document_status": "ambiguous",
            "selected_document_id": None,
        }

    # Otherwise, identify the documents represented in retrieved chunks.
    retrieved_ids = {
        doc.metadata.get("document_id")
        for doc in retrieved_documents
        if doc.metadata.get("document_id") is not None
    }

    if len(retrieved_ids) == 1:
        return {
            "document_status": "found",
            "selected_document_id": retrieved_ids.pop(),
        }

    if len(retrieved_ids) > 1:
        return {
            "document_status": "ambiguous",
            "selected_document_id": None,
        }

    # No clear document match. Let the context checker handle this.
    return {
        "document_status": "not_required",
        "selected_document_id": None,
    }