from enterprise_rag_project.agents.state import RAGState
from pydantic import BaseModel, Field
from enterprise_rag_project.services.llm import get_llm
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate


class QueryRoute(BaseModel):
    route: Literal["rag", "direct"] = Field(
        description="Whether the query requires company or document knowledge"
    )


def query_analyzer(state: RAGState):
    llm = get_llm()
    structured_llm = llm.with_structured_output(QueryRoute)

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state.get("messages", [])[-6:]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Analyze the user's latest query using the conversation history.

            Choose "rag" when the query:
            - Requires company-specific knowledge.
            - Asks about policies, procedures, manuals, or internal information.
            - Refers to information from a previously discussed or uploaded document.
            - Is a follow-up to a document-related question.

            Choose "direct" when the query is general knowledge
            and does not require company-specific or document information.

            If the query is ambiguous but appears to refer to a document
            or company information, choose "rag".
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

    chain = prompt | structured_llm

    result = chain.invoke({
        "history": history,
        "query": state["query"],
    })

    return {"route": result.route}