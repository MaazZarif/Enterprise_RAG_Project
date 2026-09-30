from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm


def answer_generator(state: RAGState):
    llm = get_llm()

    documents = state["reranked_documents"]

    context = "\n\n".join(
        f"""
        Source {i}:

        Content:
        {doc.page_content}

        Metadata:
        {doc.metadata}
        """
        for i, doc in enumerate(documents)
    )

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"][-6:]
    )

    query = (
        state.get("contextualized_query")
        or state["query"]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an enterprise knowledge assistant.

            Answer the user's question using the retrieved
            document context.

            Use conversation history only to understand the user's
            intent and references.

            Company-specific factual claims must come from the
            retrieved context.

            Do not invent unsupported information.

            If the documents do not support the answer, say so.
            """
        ),
        (
            "human",
            """
            Conversation history:
            {history}

            User question:
            {query}

            Retrieved context:
            {context}
            """
        )
    ])

    chain = prompt | llm

    response = chain.invoke({
        "history": history,
        "query": query,
        "context": context,
    })

    return {
        "answer": response.content,
        "generation_attempts": state.get(
            "generation_attempts",
            0
        ) + 1,
    }