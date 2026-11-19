from enterprise_rag_project.agents.state import RAGState


def route_context(state: RAGState):

    if state["context_status"] == "sufficient":
        return "proceed"

    return "human_review"