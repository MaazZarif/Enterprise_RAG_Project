
from enterprise_rag_project.agents.state import RAGState


def citation_builder(state: RAGState):

    # Use the same documents selected for answer generation.
    if state.get("selected_document_id") is not None:
        documents = state.get("selected_documents", [])
    else:
        documents = (
            state.get("selected_documents")
            if state.get("selected_documents") is not None
            else state.get("reranked_documents", [])
        )

    citations = []

    for i, doc in enumerate(documents):

        citations.append({
            "source_id": i + 1,
            "document_id": doc.metadata.get("document_id"),
            "filename": doc.metadata.get("filename"),
            "page": doc.metadata.get("page"),
            "chunk_index": doc.metadata.get("chunk_index"),
        })

    return {
        "citations": citations
    }
