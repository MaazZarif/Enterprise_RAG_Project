import json
from pathlib import Path

from langchain_core.messages import HumanMessage

from enterprise_rag_project.agents.graph import build_graph
from enterprise_rag_project.db.checkpointer import get_checkpointer


def load_dataset():

    dataset_path = Path(__file__).parent / "dataset.json"

    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():

    dataset = load_dataset()
    dataset = dataset[:10]

    with get_checkpointer() as checkpointer:

        graph = build_graph(checkpointer)

        results = []

        for item in dataset:

            question = item["question"]

            print(f"Running {item['id']}: {question}")

            initial_state = {
                "query": question,
                "user_id": 3,

                "messages": [
                    HumanMessage(content=question)
                ],

                "documents": [],
                "reranked_documents": [],

                "retry_count": 0,
                "generation_attempts": 0,

                "citations": [],
            }

            config = {
                "configurable": {
                    "thread_id": f"evaluation-{item['id']}"
                }
            }

            result = graph.invoke(
                initial_state,
                config=config
            )

            results.append({
                "id": item["id"],
                "question": question,
                "ground_truth": item["ground_truth"],
                "answer": result.get("answer", ""),
                "citations": result.get("citations", []),
                "retry_count": result.get("retry_count", 0),
                "generation_attempts": result.get(
                    "generation_attempts", 0
                )
            })

    output_path = (
        Path(__file__).parent / "results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nEvaluation completed!")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    evaluate()