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

    documents = state["documents"]

    # No retrieved documents = automatically insufficient
    if not documents:
        return {
            "context_status": "insufficient"
        }

    query = (
        # state.get("rewritten_query")
        state.get("contextualized_query")
        or state["query"]
    )

    

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ContextCheck
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are checking whether retrieved document context is sufficient
to answer the user's query.

Return "sufficient" if the context contains enough relevant
information to answer the query reliably.

Return "insufficient" if the context is missing important
information, is unrelated, or cannot support a reliable answer.

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