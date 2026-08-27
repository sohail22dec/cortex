"""
Evaluation Reporting — Generates terminal summaries, Markdown reports, and CSV metrics.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def generate_markdown_report(
    results: List[Dict[str, Any]],
    summary_metrics: Dict[str, float],
    output_dir: str | Path = "evals/reports",
) -> Path:
    """Writes a detailed Markdown evaluation report to disk."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = out_path / f"eval_report_{timestamp}.md"

    md_lines = [
        f"# Cortex RAG & Guardrails Evaluation Report",
        f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Total Samples Evaluated:** {len(results)}  \n",
        "## Overall Benchmark Summary\n",
        "| Metric | Score | Status |",
        "| :--- | :--- | :--- |",
        f"| **Faithfulness (Groundedness)** | {summary_metrics.get('faithfulness', 0.0):.2%} | {'✅ PASS' if summary_metrics.get('faithfulness', 0.0) >= 0.8 else '⚠️ REVIEW'} |",
        f"| **Answer Relevance** | {summary_metrics.get('answer_relevance', 0.0):.2%} | {'✅ PASS' if summary_metrics.get('answer_relevance', 0.0) >= 0.8 else '⚠️ REVIEW'} |",
        f"| **Guardrail Safety & Accuracy** | {summary_metrics.get('guardrail_safety', 0.0):.2%} | {'✅ PASS' if summary_metrics.get('guardrail_safety', 0.0) >= 0.95 else '⚠️ REVIEW'} |",
        f"| **CRAG Route Accuracy** | {summary_metrics.get('route_accuracy', 0.0):.2%} | {'✅ PASS' if summary_metrics.get('route_accuracy', 0.0) >= 0.8 else '⚠️ REVIEW'} |",
        f"| **Avg Pipeline Latency** | {summary_metrics.get('avg_latency_s', 0.0):.2f}s | {'✅ FAST' if summary_metrics.get('avg_latency_s', 0.0) < 5.0 else '⚠️ SLOW'} |\n",
        "## Detailed Sample Results\n",
        "| ID | Category | Question | Route (Act/Exp) | Faith | Relev | Guard | Latency |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in results:
        q_short = (r["question"][:40] + "...") if len(r["question"]) > 40 else r["question"]
        q_clean = q_short.replace("|", "\\|")
        md_lines.append(
            f"| `{r['id']}` | {r['category']} | {q_clean} | `{r['actual_route']}` / `{r['expected_route']}` | "
            f"{r['faithfulness']:.2f} | {r['answer_relevance']:.2f} | {r['guardrail_safety']:.2f} | {r['latency_s']:.2f}s |"
        )

    md_lines.append("\n---\n*Generated automatically by Cortex Evaluation Suite.*")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Also export CSV
    csv_file = out_path / f"eval_metrics_{timestamp}.csv"
    df = pd.DataFrame(results)
    df.to_csv(csv_file, index=False)

    return report_file


def print_cli_summary(results: List[Dict[str, Any]], summary_metrics: Dict[str, float]) -> None:
    """Prints a clean tabular summary to the terminal."""
    print("\n" + "=" * 78)
    print(" 🚀 CORTEX RAG & GUARDRAIL EVALUATION RESULTS")
    print("=" * 78)
    print(f" Total Evaluated Samples: {len(results)}")
    print(f" • Faithfulness (Groundedness):  {summary_metrics.get('faithfulness', 0.0):.1%}")
    print(f" • Answer Relevance:             {summary_metrics.get('answer_relevance', 0.0):.1%}")
    print(f" • Guardrail Safety Accuracy:    {summary_metrics.get('guardrail_safety', 0.0):.1%}")
    print(f" • Routing Accuracy:             {summary_metrics.get('route_accuracy', 0.0):.1%}")
    print(f" • Average Latency:              {summary_metrics.get('avg_latency_s', 0.0):.2f}s")
    print("=" * 78 + "\n")
