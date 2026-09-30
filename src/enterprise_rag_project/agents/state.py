from typing import TypedDict,Annotated
from langchain_core.documents import Document
from typing import Literal,List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class RAGState(TypedDict):
    """
    Represents the state of the agent, including the conversation history and the current document.
    """
    query: str
    user_id: str
    documents: list[Document]
    route:Literal["rag", "direct"]
    answer:str
    context_status:Literal["sufficient","insufficient"]
    rewritten_query:str
    retry_count:str
    reranked_documents:list[Document]
    citations:List[dict]
    grounding_status: Literal["grounded", "not_grounded"]
    generation_attempts: int
    messages: Annotated[list[BaseMessage], add_messages]
    contextualized_query:str