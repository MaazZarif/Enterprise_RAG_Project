from enterprise_rag_project.agents.state import RAGState

def route_human_document_review(state: RAGState):
    status = state.get("document_status")

    if status == "found":
        return "proceed"

    if status == "missing":
        return "missing_document"

    raise ValueError(
        f"Unexpected document status after human review: {status}"
    )