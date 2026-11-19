
from enterprise_rag_project.agents.state import RAGState

from enterprise_rag_project.services.document_context import get_active_documents

def citation_builder(state):
    documents = get_active_documents(state)

    citations = []

    for doc in documents:
        citations.append({
            "document_id": doc.metadata.get("document_id"),
            "filename": doc.metadata.get("filename"),
            "page": doc.metadata.get("page"),
        })

    return {"citations": citations}