from langgraph.types import interrupt
from enterprise_rag_project.agents.state import RAGState


def human_review(state: RAGState):

    if state.get("selected_document_id") is not None:
        documents = state.get("selected_documents", [])
    else:
        documents = (
            state.get("selected_documents")
            if state.get("selected_documents") is not None
            else state.get("reranked_documents", [])
        )

    decision = interrupt({
        "question": state["query"],
        "documents": [
            {
                "filename": doc.metadata.get("filename"),
                "content": doc.page_content,
            }
            for doc in documents
        ],
        "message": "Are these documents sufficient to answer the question?"
    })

    return {
        "human_decision": decision
    }