from enterprise_rag_project.agents.state import RAGState

def filter_selected_document(state: RAGState):
    selected_id = state.get("selected_document_id")

    if selected_id is None:
        return {
            "selected_documents": [],
        }

    documents = state.get("reranked_documents", [])

    selected_documents = [
        doc for doc in documents
        if doc.metadata.get("document_id") == selected_id
    ]

    return {
        "selected_documents": selected_documents,
    }