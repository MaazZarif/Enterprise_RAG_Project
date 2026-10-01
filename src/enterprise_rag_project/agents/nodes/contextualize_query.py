
from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm


def contextualize_query(state: RAGState):
    llm = get_llm()

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"][-6:]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Rewrite the latest user query into a clear standalone query.

            Use the conversation history only to resolve references
            such as "it", "that", "those days", "this policy", etc.

            Do not answer the question.

            Preserve the user's original intent.
            """
        ),
        (
            "human",
            """
            Conversation history:
            {history}

            Latest query:
            {query}
            """
        )
    ])

    chain = prompt | llm

    response = chain.invoke({
        "history": history,
        "query": state["query"],
    })

    return {
        "contextualized_query": response.content
    }