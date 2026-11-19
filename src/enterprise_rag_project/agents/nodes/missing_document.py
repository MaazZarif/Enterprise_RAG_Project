
from enterprise_rag_project.agents.state import RAGState


def missing_document(state: RAGState):
    message = (
        "I couldn't find the document you're referring to "
        "in this conversation. Please upload that document "
        "so I can answer your question."
    )

    return {
        "answer": message,
        "clarification_question": message,
        "citations": [],
    }
