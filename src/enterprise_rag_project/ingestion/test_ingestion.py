from enterprise_rag_project.ingestion.vectore_store import initialize_collection
from enterprise_rag_project.ingestion.ingest_pipeline import ingest_pipeline


initialize_collection()

ids = ingest_pipeline(
    file_path="src/enterprise_rag_project/data/Information_Security_Policy.pdf",
    document_id=1,
    user_id=1,
)

print(f"Ingested {len(ids)} chunks")