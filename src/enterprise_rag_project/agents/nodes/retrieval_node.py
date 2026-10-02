from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.ingestion.retriever import get_retriever    

def retrieval_node(state: RAGState):

    query = (
        # state.get("rewritten_query")
        state.get("contextualized_query")
        or state["query"]
    )

    retriever = get_retriever(
        user_id=state["user_id"],
        k=5,
    )

    documents = retriever.invoke(query)

    return {
        "documents": documents
    }