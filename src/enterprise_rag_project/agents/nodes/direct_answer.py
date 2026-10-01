from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate



def direct_answer(state: RAGState):
    llm = get_llm()

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"][-6:]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an enterprise AI assistant.

            Answer the user's latest question clearly and concisely.

            Use conversation history when needed to understand
            follow-up questions.

            Do not invent company-specific information.
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
        "answer": response.content,
        "messages": [response],
    }