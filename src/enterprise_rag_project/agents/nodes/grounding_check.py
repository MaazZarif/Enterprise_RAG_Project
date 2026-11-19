from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.services.llm import get_llm
from enterprise_rag_project.services.document_context import get_active_documents


class GroundingCheck(BaseModel):
    grounding_status: Literal["grounded", "not_grounded"] = Field(
        description="Whether the generated answer is fully supported by the provided context"
    )


def grounding_check(state: RAGState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        GroundingCheck
    )


   

    documents = get_active_documents(state)

    if not documents:
        return {
            "grounding_status": "not_grounded",
        }

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Determine whether the generated answer is fully supported
            by the provided document context.

            Return "grounded" if the important factual claims are
            supported.

            Return "not_grounded" if the answer contains unsupported
            or invented claims.
            """
        ),
        (
            "human",
            """
            Context:
            {context}

            Answer:
            {answer}
            """
        )
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "context": context,
        "answer": state["answer"],
    })

    return {
        "grounding_status": result.grounding_status
    }