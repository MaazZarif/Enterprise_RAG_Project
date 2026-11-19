from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm

def answer_generator(state: RAGState):

    llm = get_llm()

    # Prefer document-resolved chunks.
    documents = (
    state.get("selected_documents")
    or state.get("reranked_documents")
    or state.get("documents", [])
)

    if not documents:
        return {
            "answer": "I couldn't find relevant information in the documents available in this conversation.",
            "generation_attempts": state.get("generation_attempts", 0) + 1,
        }

    context = "\n\n".join(
        f"""
        Source {i + 1}
        Filename: {doc.metadata.get("filename", "Unknown")}
        Document ID: {doc.metadata.get("document_id", "Unknown")}

        Content:
        {doc.page_content}
        """
        for i, doc in enumerate(documents)
    )

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state.get("messages", [])[-6:]
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

            Answer the user's question using the provided document context.

            Rules:

            1. Company-specific factual claims must be supported
               by the provided document context.

            2. Do not use general knowledge to fill gaps in company-specific
               information.

            3. Do not invent facts, policies, dates, figures, or procedures.

            4. Use conversation history only to understand references
               and user intent. It is not a factual source.

            5. If the context does not contain enough information,
               clearly explain what information is missing.

            6. Keep the answer clear and easy to understand.
            """
        ),
        (
            "human",
            """
            Conversation history:
            {history}

            User question:
            {query}

            Document context:
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
            "generation_attempts", 0
        ) + 1,
    }