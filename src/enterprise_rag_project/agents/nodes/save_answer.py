from langchain_core.messages import AIMessage

from enterprise_rag_project.agents.state import RAGState


def save_answer(state: RAGState):

    return {
        "messages": [
            AIMessage(content=state["answer"])
        ]
    }