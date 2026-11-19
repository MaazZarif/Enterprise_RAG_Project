from enterprise_rag_project.agents.state import RAGState

def filter_selected_document(state: RAGState):

    selected_document_id = state.get("selected_document_id")
    documents = state.get("reranked_documents", [])

    if selected_document_id is None:
        return {
            "selected_documents": documents,
        }

    selected_documents = [
        doc for doc in documents
        if doc.metadata.get("document_id") == selected_document_id
    ]

    return {
        "selected_documents": selected_documents,
    }