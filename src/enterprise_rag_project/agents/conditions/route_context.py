from enterprise_rag_project.agents.state import RAGState


def route_context(state: RAGState):

    if state["context_status"] == "sufficient":
        return "proceed"

    if state.get("retry_count",0) >= 2:
        return "fallback"

    return "rewrite"