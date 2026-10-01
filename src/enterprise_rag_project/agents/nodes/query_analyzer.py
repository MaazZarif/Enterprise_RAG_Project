from enterprise_rag_project.agents.state import RAGState
from pydantic import BaseModel, Field
from enterprise_rag_project.services.llm import get_llm
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate


class QueryRoute(BaseModel):
    route: Literal["rag", "direct"] = Field(
        description="Route the query to RAG or direct answering"
    )


def query_analyzer(state: RAGState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(QueryRoute)

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"][-6:]
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Analyze the user's latest query.

            Use the conversation history to understand references
            such as "it", "that", "those days", "this policy", etc.

            Choose "rag" if the query requires company-specific
            documents, policies, procedures, manuals, internal
            knowledge, or uploaded files.

            Choose "direct" if it is a general knowledge question
            that does not require company-specific information.
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

    return {
        "route": result.route
    }