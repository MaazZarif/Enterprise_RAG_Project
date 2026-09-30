
from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm
from pydantic import BaseModel,Field
from langchain_core.prompts import ChatPromptTemplate
from typing import List


class RankedDocuments(BaseModel):
     ranked_indices: list[int] = Field(
        description="Indices of documents ordered from most relevant to least relevant"
    )

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

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        RankedDocuments
    )

    # Use the query that produced the current retrieval results
    query = (
        state.get("rewritten_query")
        or state.get("contextualized_query")
        or state["query"]
    )

    documents = state["documents"]

    # Safety check
    if not documents:
        return {
            "reranked_documents": []
        }

    formatted_documents = "\n\n".join(
        f"""
Document {i}:
{doc.page_content}
"""
        for i, doc in enumerate(documents)
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a document reranker.

Given a user search query and retrieved documents,
rank the documents from most relevant to least relevant.

Return the document indices in ranked order.

Do not answer the user's question.
Do not invent document indices.
"""
        ),
        (
            "human",
            """
Query:
{query}

Documents:
{documents}
"""
        )
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "query": query,
        "documents": formatted_documents,
    })

    reranked_documents = [
        documents[i]
        for i in result.ranked_indices
        if 0 <= i < len(documents)
    ]

    return {
        "reranked_documents": reranked_documents
    }