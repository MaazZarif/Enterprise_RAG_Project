
from enterprise_rag_project.agents.state import RAGState

def missing_document(state: RAGState):
    return {
        "clarification_question": (
            "I couldn't find the document you're referring to "
            "in this conversation. Please upload it so I can answer "
            "your question."
        )
    }