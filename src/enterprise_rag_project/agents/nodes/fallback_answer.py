from enterprise_rag_project.agents.state import RAGState


def fallback_answer(state: RAGState):

    return {
        "answer": (
            "I couldn't generate an answer that is reliably supported "
            "by the available documents."
        ),
        "citations": []
    }