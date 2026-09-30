from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from enterprise_rag_project.ingestion.embeddings import get_embeddings
import os
from functools import lru_cache

load_dotenv()  # Load environment variables from .env file

@lru_cache(maxsize=1)
def get_qdrant_client():
    """
    Create and return a QdrantClient instance.

    Returns:
        QdrantClient: An instance of QdrantClient.
    """
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_HOST"), api_key=os.getenv("QDRANT_API_KEY")
    )
    return qdrant_client


def initialize_collection():
    client = get_qdrant_client()
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    if not client.collection_exists(collection_name):
        embeddings = get_embeddings()

        vector_size = len(embeddings.embed_query("dimension test"))

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    collection_info = client.get_collection(collection_name)

    if "metadata.user_id" not in collection_info.payload_schema:

        client.create_payload_index(
            collection_name=collection_name,
            field_name="metadata.user_id",
            field_schema=PayloadSchemaType.INTEGER,
        )


def get_vector_store():
    """
    Create and return a QdrantVectorStore instance.

    Returns:
        QdrantVectorStore: An instance of QdrantVectorStore.
    """
    qdrant_client = get_qdrant_client()
    embeddings = get_embeddings()

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        embedding=embeddings,
    )

    return vector_store
