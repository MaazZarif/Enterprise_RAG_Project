from enterprise_rag_project.agents.state import RAGState


def get_active_documents(state: RAGState):
    # Direct answers do not need document context
    if state.get("route") == "direct":
        return []

    # No document was found
    if state.get("document_status") == "missing":
        return []

    # Only use the explicitly selected document
    if state.get("document_status") == "found":
        selected_id = state.get("selected_document_id")
        selected_documents = state.get("selected_documents", [])

        if selected_id is None:
            return []

        return [
            doc for doc in selected_documents
            if doc.metadata.get("document_id") == selected_id
        ]

    return []