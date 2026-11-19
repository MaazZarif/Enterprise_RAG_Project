from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm


class RankedDocuments(BaseModel):
    ranked_indices: List[int] = Field(
        description="Document indices ordered from most relevant to least relevant"
    )


def rerank_documents(state: RAGState):

    documents = state.get("documents", [])

    if not documents:
        return {"reranked_documents": []}

    llm = get_llm()
    structured_llm = llm.with_structured_output(RankedDocuments)

    query = (
        state.get("contextualized_query")
        or state["query"]
    )

    formatted_documents = "\n\n".join(
        f"""
Document index: {i}
Filename: {doc.metadata.get("filename", "Unknown")}
Content:
{doc.page_content}
"""
        for i, doc in enumerate(documents)
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a document relevance reranker.

            Rank the retrieved document chunks according to their
            relevance to the user's query.

            Consider:
            - How directly the content answers the query.
            - Whether the content contains the required information.
            - Whether it is relevant to the user's actual intent.

            Return valid document indices only.
            Do not answer the query.
            Do not invent information or indices.
            """
        ),
        (
            "human",
            """
            Query:
            {query}

            Retrieved documents:
            {documents}
            """
        )
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "query": query,
        "documents": formatted_documents,
    })

    # Keep only valid, unique indices.
    valid_indices = []
    for index in result.ranked_indices:
        if (
            isinstance(index, int)
            and 0 <= index < len(documents)
            and index not in valid_indices
        ):
            valid_indices.append(index)

    # Preserve any documents the LLM omitted.
    valid_indices.extend(
        i for i in range(len(documents))
        if i not in valid_indices
    )

    reranked_documents = [
        documents[i] for i in valid_indices
    ]

    return {
        "reranked_documents": reranked_documents
    }