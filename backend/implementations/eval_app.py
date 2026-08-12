import gradio as gr
import pandas as pd

from eval_runner import run_eval, compute_summary


def results_to_dataframe(results):
    rows = []
    for r in results:
        rows.append({
            'Question': r['question'],
            'Doc Type': r['expected_doc_type'] or 'N/A',
            'Retrieval': (
                'N/A' if r['retrieval_pass'] is None
                else ('PASS' if r['retrieval_pass'] else 'FAIL')
            ),
            'Answer': 'PASS' if r['answer_pass'] else 'FAIL',
            'Response': r['answer'],
        })
    return pd.DataFrame(rows)


def breakdown_to_markdown(summary):
    lines = ['| Doc Type | Answer Accuracy |', '|---|---|']
    for item in summary['breakdown']:
        doc_type = item['doc_type'] or 'N/A (unanswerable)'
        lines.append(f"| {doc_type} | {item['answer_pass_count']}/{item['total']} |")
    return '\n'.join(lines)


def run_and_display():
    results = run_eval()
    summary = compute_summary(results)

    retrieval_text = (
        f"{summary['retrieval_pass_count']}/{summary['retrieval_checked_count']} "
        f"({summary['retrieval_pct']:.0f}%)"
        if summary['retrieval_pct'] is not None else 'N/A'
    )
    answer_text = f"{summary['answer_pass_count']}/{summary['answer_total_count']} ({summary['answer_pct']:.0f}%)"

    return (
        retrieval_text,
        answer_text,
        breakdown_to_markdown(summary),
        results_to_dataframe(results),
    )


with gr.Blocks(title='RAG Eval Report') as demo:
    gr.Markdown('# NovaTech RAG Eval Report')
    gr.Markdown('Runs all 30 test questions through the RAG pipeline and scores retrieval + answer correctness.')

    run_button = gr.Button('Run Eval', variant='primary')

    with gr.Row():
        retrieval_metric = gr.Textbox(label='Retrieval Accuracy', interactive=False)
        answer_metric = gr.Textbox(label='Answer Accuracy', interactive=False)

    breakdown_md = gr.Markdown(label='Breakdown by Category')
    results_table = gr.Dataframe(label='Full Results', wrap=True)

    run_button.click(
        fn=run_and_display,
        inputs=[],
        outputs=[retrieval_metric, answer_metric, breakdown_md, results_table],
    )


if __name__ == '__main__':
    demo.launch()
