from enterprise_rag_project.agents.state import RAGState


def route_grounding(state:RAGState):

    if state["grounding_status"] == "grounded":
        return "grounded"

    if state.get("generation_attempts",0) >= 3:
        return "fallback"

    return "regenerate"
