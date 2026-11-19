from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm


class ContextCheck(BaseModel):
    context_status: Literal[
        "sufficient",
        "insufficient"
    ] = Field(
        description="Whether the retrieved documents contain enough information to answer the query"
    )


def context_check(state: RAGState):

    documents = (
        state.get("reranked_documents")
        or state.get("documents", [])
    )

    if not documents:
        return {
            "context_status": "insufficient"
        }

    query = (
        state.get("contextualized_query")
        or state["query"]
    )

    context = "\n\n".join(
        f"""
Filename: {doc.metadata.get("filename", "Unknown")}
Content:
{doc.page_content}
"""
        for doc in documents
    )

    llm = get_llm()

    structured_llm = llm.with_structured_output(ContextCheck)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are evaluating retrieved document context.

            Return "sufficient" only when the provided context contains
            enough relevant and reliable information to answer the query.

            Return "insufficient" when:
            - The context is unrelated.
            - Important information is missing.
            - The context does not support a reliable answer.

            Do not use outside knowledge.
            Do not answer the user's question.
            """
        ),
        (
            "human",
            """
            Query:
            {query}

            Retrieved context:
            {context}
            """
        )
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "query": query,
        "context": context,
    })

    return {
        "context_status": result.context_status
    }