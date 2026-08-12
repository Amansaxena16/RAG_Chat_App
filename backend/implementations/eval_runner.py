import json
import os
from collections import defaultdict

from langchain_core.messages import HumanMessage

from answer import answer_question, llm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'eval_dataset.jsonl')
RESULTS_PATH = os.path.join(BASE_DIR, 'eval_results.json')


def load_dataset():
    cases = []
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def check_retrieval(docs, expected_doc_type):
    if expected_doc_type is None:
        return None
    retrieved_types = {d.metadata.get('doc_type') for d in docs}
    return expected_doc_type in retrieved_types


def judge_answer(answer, expected_fact, expected_doc_type):
    if expected_doc_type is None:
        prompt = (
            "The following answer should correctly admit that the information "
            "is not known or not available, rather than guessing.\n"
            f"Answer: {answer}\n"
            "Does it correctly admit it doesn't know? Reply only YES or NO."
        )
    else:
        prompt = (
            f"Expected fact: {expected_fact}\n"
            f"Actual answer: {answer}\n"
            "Does the actual answer correctly state this fact? Reply only YES or NO."
        )
    response = llm.invoke([HumanMessage(content=prompt)])
    verdict = response.content.strip().upper()
    return verdict.startswith('YES')


def run_eval():
    cases = load_dataset()
    results = []

    for i, case in enumerate(cases, start=1):
        question = case['question']
        expected_fact = case['expected_fact']
        expected_doc_type = case.get('expected_doc_type')
        history = case.get('history', [])

        answer, docs = answer_question(question, history)

        retrieval_pass = check_retrieval(docs, expected_doc_type)
        answer_pass = judge_answer(answer, expected_fact, expected_doc_type)

        result = {
            'question': question,
            'expected_doc_type': expected_doc_type,
            'answer': answer,
            'retrieval_pass': retrieval_pass,
            'answer_pass': answer_pass,
        }
        results.append(result)

        r_symbol = 'PASS' if retrieval_pass else ('N/A' if retrieval_pass is None else 'FAIL')
        a_symbol = 'PASS' if answer_pass else 'FAIL'
        print(f"[{i}/{len(cases)}] retrieval={r_symbol:4} answer={a_symbol:4} | {question}")

    summary = compute_summary(results)
    print_summary(summary)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved full results to {RESULTS_PATH}")

    return results


def compute_summary(results):
    retrieval_checked = [r for r in results if r['retrieval_pass'] is not None]
    retrieval_hits = [r for r in retrieval_checked if r['retrieval_pass']]
    answer_hits = [r for r in results if r['answer_pass']]

    retrieval_pct = 100 * len(retrieval_hits) / len(retrieval_checked) if retrieval_checked else None
    answer_pct = 100 * len(answer_hits) / len(results) if results else 0

    by_type = defaultdict(list)
    for r in results:
        by_type[r['expected_doc_type']].append(r)

    breakdown = []
    for doc_type, items in by_type.items():
        answer_ok = sum(1 for i in items if i['answer_pass'])
        breakdown.append({
            'doc_type': doc_type,
            'answer_pass_count': answer_ok,
            'total': len(items),
        })

    return {
        'retrieval_pass_count': len(retrieval_hits),
        'retrieval_checked_count': len(retrieval_checked),
        'retrieval_pct': retrieval_pct,
        'answer_pass_count': len(answer_hits),
        'answer_total_count': len(results),
        'answer_pct': answer_pct,
        'breakdown': breakdown,
    }


def print_summary(summary):
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    if summary['retrieval_pct'] is not None:
        print(f"Retrieval accuracy: {summary['retrieval_pass_count']}/{summary['retrieval_checked_count']} "
              f"({summary['retrieval_pct']:.0f}%)")
    print(f"Answer accuracy:    {summary['answer_pass_count']}/{summary['answer_total_count']} "
          f"({summary['answer_pct']:.0f}%)")

    print("\nBreakdown by doc_type:")
    for item in summary['breakdown']:
        print(f"  {str(item['doc_type']):12} answer {item['answer_pass_count']}/{item['total']}")


if __name__ == '__main__':
    run_eval()
