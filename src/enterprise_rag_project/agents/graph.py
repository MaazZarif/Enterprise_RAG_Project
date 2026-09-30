from enterprise_rag_project.agents.state import RAGState
from langgraph.graph import StateGraph, START, END
from enterprise_rag_project.agents.nodes.retrieval_node import retrieval_node
from enterprise_rag_project.agents.nodes.query_analyzer import query_analyzer
from enterprise_rag_project.agents.nodes.direct_answer import direct_answer
from enterprise_rag_project.agents.conditions.route_query import route_query
from enterprise_rag_project.agents.conditions.route_context import route_context
from enterprise_rag_project.agents.nodes.context_check import context_check
from enterprise_rag_project.agents.nodes.rewrite_query import rewrite_query
from enterprise_rag_project.agents.nodes.reranker import rerank_documents
from enterprise_rag_project.agents.nodes.answer_generator import answer_generator
from enterprise_rag_project.agents.nodes.citation_builder import citation_builder
from enterprise_rag_project.agents.nodes.grounding_check import grounding_check
from enterprise_rag_project.agents.conditions.route_grounding_check import route_grounding
from enterprise_rag_project.agents.nodes.fallback_answer import fallback_answer
from enterprise_rag_project.agents.nodes.contextualize_query import contextualize_query
from enterprise_rag_project.agents.nodes.save_answer import save_answer
from enterprise_rag_project.db.checkpointer import get_checkpointer
from langchain_core.messages import HumanMessage



graph_builder = StateGraph(RAGState)

graph_builder.add_node("query_analyzer",query_analyzer)
graph_builder.add_node("retrieval_node",retrieval_node)
graph_builder.add_node("direct_answer",direct_answer)
graph_builder.add_node("context_check",context_check)
graph_builder.add_node("rewrite_query",rewrite_query)
graph_builder.add_node("reranker",rerank_documents)
graph_builder.add_node("answer_generator",answer_generator)
graph_builder.add_node("citation_builder",citation_builder)
graph_builder.add_node("grounding_check",grounding_check)
graph_builder.add_node("fallback_answer",fallback_answer)

graph_builder.add_node("contextualize_query", contextualize_query)
graph_builder.add_node("save_answer", save_answer)


graph_builder.add_edge(START, "query_analyzer")
graph_builder.add_conditional_edges(
    "query_analyzer",
    route_query,
    {
        "rag": "contextualize_query",
        "direct": "direct_answer"
    }
)

graph_builder.add_edge(
    "contextualize_query",
    "retrieval_node"
)
graph_builder.add_edge("retrieval_node","context_check")
graph_builder.add_edge("direct_answer",END)
graph_builder.add_conditional_edges("context_check",route_context,{"proceed":"reranker","fallback":"fallback_answer", "rewrite":"rewrite_query"})
graph_builder.add_edge("rewrite_query","retrieval_node")
graph_builder.add_edge("reranker","answer_generator")


graph_builder.add_edge(
    "answer_generator",
    "grounding_check"
)
graph_builder.add_conditional_edges(
    "grounding_check",
    route_grounding,
    {
        "grounded": "save_answer",
        "fallback": "fallback_answer",
        "regenerate": "answer_generator"
    }
)

graph_builder.add_edge(
    "save_answer",
    "citation_builder"
)
graph_builder.add_edge("citation_builder",END)
graph_builder.add_edge("fallback_answer",END)


def build_graph(checkpointer):
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph

if __name__ ==  "__main__":

    with get_checkpointer() as checkpointer:

        graph = graph_builder.compile(
            checkpointer=checkpointer
        )

    initial_state = {
    "query": "explain the company prohibited activities ?",
    "user_id": 1,

    "messages": [
        HumanMessage(
            content="explain the company prohibited activities ?"
        )
    ],

    "documents": [],
    "reranked_documents": [],

    "retry_count": 0,
    "generation_attempts": 0,
    "citations": [],
}

    config = {
    "configurable": {
        "thread_id": "test-thread-1"
    }
}

    for event in graph.stream(
        initial_state,
        config=config
    ):
        print(event)
        print("-" * 50)








