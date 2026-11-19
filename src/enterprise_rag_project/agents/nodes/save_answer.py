
from langchain_core.messages import AIMessage

from enterprise_rag_project.agents.state import RAGState


def save_answer(state: RAGState):

    answer = state.get("answer")

    if not answer:
        raise ValueError(
            "Cannot save an empty answer to conversation history."
        )

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }
