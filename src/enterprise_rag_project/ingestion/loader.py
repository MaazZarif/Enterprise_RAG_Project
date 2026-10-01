from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
)
from pathlib import Path



def load_document(file_path: str):
    """
    Load documents from the given file path based on the file type.

    Args:
        file_path (str): The path to the document file.

    Returns:
        List[Document]: A list of loaded documents.
    """

    all_documents=[]
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if file_path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(file_path))

    elif file_path.suffix.lower() == ".docx":
        loader = Docx2txtLoader(str(file_path))

    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    documents = loader.load()


    return documents


def load_folder(folder_path: str):
    """
    Load documents from all supported files in the given folder.

    Args:
        folder_path (str): The path to the folder containing document files.    

    Returns:
        List[Document]: A list of loaded documents from the folder.
    """
    
    all_documents = []
    folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        raise NotADirectoryError(f"The path {folder_path} is not a valid directory.")

    for file in folder_path.iterdir():
        if file.suffix.lower() in [".pdf", ".docx"]:
            documents = load_document(str(file))
            all_documents.extend(documents)

    return all_documents


        


 