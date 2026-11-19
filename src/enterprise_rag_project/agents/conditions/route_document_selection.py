from enterprise_rag_project.agents.state import RAGState

def route_document_selection(state: RAGState):

    if state.get("document_status") == "ambiguous":
        return "human_document_review"

    return "proceed"