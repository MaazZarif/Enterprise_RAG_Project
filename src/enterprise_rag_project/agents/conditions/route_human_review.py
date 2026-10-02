
from enterprise_rag_project.agents.state import RAGState

def route_human_review(state:RAGState):

    if state["human_decision"]:
        return "proceed"

    return "reject"