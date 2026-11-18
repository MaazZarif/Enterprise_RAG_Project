from pathlib import Path
import json
from enterprise_rag_project.services.llm import get_llm
from enterprise_rag_project.ingestion.embeddings import get_embeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics.collections import (Faithfulness,AnswerRelevancy,FactualCorrectness)
import os

RESULTS_PATH = Path(__file__).parent / "results.json"
OUTPUT_PATH = Path(__file__).parent / "ragas_results.json"


llm = get_llm()

evaluator_llm = LangchainLLMWrapper(llm)

embeddings = get_embeddings()
evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings)

faithfulness = Faithfulness(llm=evaluator_llm)
answer_relevancy = AnswerRelevancy(llm=evaluator_llm,embeddings=evaluator_embeddings)
factual_correctness = FactualCorrectness(llm=evaluator_llm)


def evaluate():


    with open(RESULTS_PATH,"r",encoding="utf-8") as file:
        results  = json.load(file)

    evaluated = []

    for item in results: 
        question = item["question"]
        answer = item["answer"]
        ground_truth = item["ground_truth"]

        contexts = [chunk["page_content"] for chunk in item.get("reranked_documents",[]) if chunk.get("page_content")]


        scores = {
                "faithfulness": None,
                "answer_relevancy": None,
                "factual_correctness": None,
            }

        print(f"Evaluating {item["id"]}....")

        try:
            if answer.strip() and contexts:
                result = faithfulness.ascore(user_input=question,response=answer,retrieved_contexts=contexts)
                scores["faithfulness"] = result.value

            if answer.strip():
                result = answer_relevancy.ascore(
                    user_input=question,
                    response=answer
                )
                scores["answer_relevancy"]=result.value

                result = factual_correctness.ascore(
                    response=answer,
                    reference=ground_truth
                )
                scores["factual_correctness"]=result.value

        except Exception as e:
            print(f"Error evaluating {item["id"]}.....")

        evaluated.append({
            "id":item["id"],
            "question":question,
            "answer":answer,
            "ground_truth":ground_truth,
            "scores":scores
        })

        with open(OUTPUT_PATH,"w",encoding="utf-8") as file:
            json.dump(evaluated,file,indent=2,ensure_ascii=False)


        print("\n===== RAGAS QA EVALUATION =====")

        for metric in [
            "faithfulness",
            "answer_relevancy",
            "factual_correctness",
        ]:
            values = [
                row["scores"][metric]
                for row in evaluated
                if isinstance(row["scores"][metric], (int, float))
            ]

            if values:
                print(f"{metric}: {sum(values) / len(values):.3f}")
            else:
                print(f"{metric}: No scores available")

        print(f"\nSaved results to: {OUTPUT_PATH}")


if __name__ == "__main__":
    evaluate()









