from enterprise_rag_project.ingestion.embeddings import get_embeddings
from enterprise_rag_project.ingestion.vectore_store import get_vector_store, initialize_collection
from enterprise_rag_project.ingestion.loader import load_document
from enterprise_rag_project.ingestion.chunker import chunk_documents
from pathlib import Path



def ingest_pipeline(file_path, document_id, user_id):

    documents = load_document(file_path)

    chunks = chunk_documents(documents)

    for index,chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["user_id"] = user_id
        chunk.metadata["chunk_index"] = index  
        chunk.metadata["filename"] = Path(file_path).name

    vector_store = get_vector_store()
    ids = vector_store.add_documents(chunks)

    return ids