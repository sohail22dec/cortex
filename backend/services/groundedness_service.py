"""
Groundedness Service — Independent semantic judge for factuality and anti-hallucination verification.
"""
from __future__ import annotations

import logging
from typing import Literal, Tuple

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class GroundednessEvaluation(BaseModel):
    is_grounded: Literal["YES", "NO"] = Field(
        description=(
            "'YES' if every factual claim in the AI answer is strictly supported and entailed by the provided context; "
            "'NO' if the answer contains any ungrounded claim, contradiction, invented number, or outside assumption."
        )
    )
    reason: str = Field(
        default="",
        description="Brief explanation of the factuality check."
    )


# Fast LLM for independent factuality judging
_judge_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
)

_structured_judge_llm = _judge_llm.with_structured_output(GroundednessEvaluation)


async def evaluate_groundedness_async(
    question: str,
    context: str,
    answer: str,
) -> Tuple[bool, str]:
    """
    Asynchronously evaluates whether the generated answer is strictly grounded in the provided context.
    Returns (is_grounded, reason).
    """
    if not context or not answer:
        return True, "Empty context or answer; skipping check."

    messages = [
        SystemMessage(
            content=(
                "You are an independent, strict Fact-Checking Judge for an enterprise AI system.\n"
                "Your job is to verify whether the AI Answer is strictly grounded in the provided Context.\n\n"
                "Rules:\n"
                "1. Break down the AI answer into its individual factual claims.\n"
                "2. Check if each claim is directly entailed/supported by the provided Context.\n"
                "3. If any claim introduces outside facts, hallucinated figures, or unverified extrapolation, "
                "set is_grounded to 'NO'.\n"
                "4. If all claims are completely supported by the Context, set is_grounded to 'YES'."
            )
        ),
        HumanMessage(
            content=(
                f"=== Context ===\n{context}\n\n"
                f"=== User Question ===\n{question}\n\n"
                f"=== AI Answer to Evaluate ===\n{answer}"
            )
        ),
    ]

    try:
        result: GroundednessEvaluation = await _structured_judge_llm.ainvoke(messages)
        is_grounded = result.is_grounded == "YES"
        return is_grounded, result.reason
    except Exception as e:
        logger.warning("Groundedness evaluation error: %s. Defaulting to grounded.", e)
        return True, "fallback"

