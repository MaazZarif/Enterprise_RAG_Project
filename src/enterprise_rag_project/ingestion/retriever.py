from qdrant_client.models import Filter, FieldCondition, MatchValue

from enterprise_rag_project.ingestion.vectore_store import get_vector_store

def get_retriever(
    user_id: int,
    search_type: str = "similarity",
    k: int = 5,
):
    vector_store = get_vector_store()

    qdrant_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.user_id",
                match=MatchValue(value=user_id),
            )
        ]
    )

    return vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": k,
            "filter": qdrant_filter,
        },
    )