from langchain_text_splitters import RecursiveCharacterTextSplitter

from enterprise_rag_project.ingestion.loader import load_folder

def chunk_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )


    chunked_documents = text_splitter.split_documents(documents)
    return chunked_documents

# documents = load_folder("src/enterprise_rag_project/data")

# chunks = chunk_documents(documents)

# print(f"chunks[0]: {chunks[4]}")