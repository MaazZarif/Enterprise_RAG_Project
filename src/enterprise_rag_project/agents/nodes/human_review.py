from langgraph.types import interrupt
from enterprise_rag_project.agents.state import RAGState


def human_review(state:RAGState):

    decision = interrupt({
        "question":state["query"],
        "documents":state["documents"],
        "message": "Are these documents sufficient to answer the question?"

    })

    return{
        "human_decision":decision
    }