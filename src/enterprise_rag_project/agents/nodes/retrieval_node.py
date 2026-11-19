from enterprise_rag_project.agents.state import RAGState
from enterprise_rag_project.ingestion.retriever import get_retriever

import time


def retrieval_node(state: RAGState):

    query = (
        state.get("contextualized_query")
        or state["query"]
    )

    start = time.perf_counter()

    retriever = get_retriever(
        user_id=state["user_id"],
        thread_id=state["thread_id"],
        k=10,
    )

    print(f"Retriever creation: {time.perf_counter() - start:.3f}s")

    start = time.perf_counter()

    documents = retriever.invoke(query)

    print(f"Actual retrieval: {time.perf_counter() - start:.3f}s")

    return {
        "documents": documents
    }