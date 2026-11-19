from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm


def contextualize_query(state: RAGState):
    llm = get_llm()

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state.get("messages", [])[-6:]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Rewrite the latest user query into a clear standalone query.

            Instructions:
            - Use conversation history to resolve references such as
              "it", "that document", "this policy", and "those rules".
            - Preserve the user's original intent.
            - Do not answer the question.
            - Do not invent information.
            - Do not assume which document the user means if multiple
              documents could match.
            - If the document identity is unclear, preserve that ambiguity
              rather than guessing.
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
        "contextualized_query": response.content.strip()
    }