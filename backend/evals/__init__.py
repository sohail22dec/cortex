"""
Cortex Evaluation Framework — Automated benchmarks for RAG quality, groundedness, and guardrails.
"""
from __future__ import annotations

from evals.dataset import (
    DEFAULT_BENCHMARK_DATASET,
    EvalSample,
    load_dataset,
    save_dataset,
)
from evals.evaluator import (
    evaluate_answer_relevance_score,
    evaluate_faithfulness_score,
    evaluate_guardrail_safety,
    evaluate_sample_async,
)
from evals.report import generate_markdown_report, print_cli_summary
from evals.runner import run_evaluation_benchmark, run_single_pipeline_test

__all__ = [
    "DEFAULT_BENCHMARK_DATASET",
    "EvalSample",
    "load_dataset",
    "save_dataset",
    "evaluate_answer_relevance_score",
    "evaluate_faithfulness_score",
    "evaluate_guardrail_safety",
    "evaluate_sample_async",
    "generate_markdown_report",
    "print_cli_summary",
    "run_evaluation_benchmark",
    "run_single_pipeline_test",
]
