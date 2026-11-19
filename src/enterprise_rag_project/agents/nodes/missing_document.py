def missing_document(state):
    question = state.get("clarification_question")

    if not question:
        question = "Please upload the document you want me to analyze."

    return {
        "answer": question,
        "clarification_question": question,
        "selected_document_id": None,
        "selected_documents": [],
        "citations": [],
    }