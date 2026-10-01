
from enterprise_rag_project.ingestion.vectore_store import initialize_collection

if __name__ == "__main__":
    initialize_collection()
    print("Qdrant initialized successfully")