
from enterprise_rag_project.agents.state import RAGState


def route_document_selection(state: RAGState):
    status = state.get("document_status")

    if status == "ambiguous":
        return "human_document_review"

    if status == "missing":
        return "missing_document"

    return "proceed"
