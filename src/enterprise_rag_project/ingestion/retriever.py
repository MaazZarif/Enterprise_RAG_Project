from qdrant_client.models import Filter, FieldCondition, MatchValue
from enterprise_rag_project.ingestion.vectore_store import get_vector_store

def get_retriever(
    user_id: int,
    thread_id: str,
    k: int = 10,
):
    vector_store = get_vector_store()

    qdrant_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.user_id",
                match=MatchValue(value=user_id),
            ),
            FieldCondition(
                key="metadata.thread_id",
                match=MatchValue(value=thread_id),
            ),
        ]
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "filter": qdrant_filter,
        },
    )