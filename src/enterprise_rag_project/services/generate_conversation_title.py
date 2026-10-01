from enterprise_rag_project.services.llm import get_llm


def generate_conversation_title(query: str) -> str:
    llm = get_llm()

    prompt = f"""
Generate a short conversation title for the user's query.

Rules:
- Maximum 5 words
- Be concise
- Do not answer the query
- Return only the title

User query:
{query}
"""

    response = llm.invoke(prompt)

    return response.content.strip()