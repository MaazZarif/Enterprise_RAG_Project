from enterprise_rag_project.agents.state import RAGState


def citation_builder(state: RAGState):

    citations = []

    for i, doc in enumerate(state["reranked_documents"]):

        citations.append({
            "source_id": i,
            "document_id": doc.metadata.get("document_id"),
            "filename": doc.metadata.get("filename"),
            "page": doc.metadata.get("page"),
            "chunk_index": doc.metadata.get("chunk_index"),
        })

    return {
        "citations": citations
    }