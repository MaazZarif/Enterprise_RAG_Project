# from enterprise_rag_project.agents.state import RAGState
# from langchain_core.prompts import ChatPromptTemplate
# from enterprise_rag_project.services.llm import get_llm


# def rewrite_query(state: RAGState):
#     llm = get_llm()

#     query = (
#         state.get("contextualized_query")
#         or state["query"]
#     )

#     prompt = ChatPromptTemplate.from_messages([
#         (
#             "system",
#             """
#             Rewrite the search query to improve document retrieval.

#             Make it more precise and retrieval-friendly.

#             Preserve the original intent.

#             Do not answer the question.
#             """
#         ),
#         (
#             "human",
#             """
#             Query:
#             {query}
#             """
#         )
#     ])

#     chain = prompt | llm

#     response = chain.invoke({
#         "query": query
#     })

#     return {
#         "rewritten_query": response.content,
#         "retry_count": state.get("retry_count", 0) + 1,
#     }
