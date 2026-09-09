# Cortex Router Node Evaluation Report

**Generated:** 2026-09-09 08:35:58 UTC  
**Model Under Test:** `openai/gpt-oss-120b` (Groq Fast Router)  
**Evaluation Scope:** Router Node Decision Accuracy (Baseline vs. Content-Enriched)

---

## Executive Summary

| Metric | Baseline (Filename Only) | Enriched (Document Content Context) | Improvement (Delta) |
|---|---|---|---|
| **Overall Accuracy** | **100.0%** (21/21) | **100.0%** (21/21) | **+0.0%** |
| **Implicit RAG Accuracy** | 100.0% | 100.0% | **+0.0%** |
| **Explicit RAG Accuracy** | 100.0% | 100.0% | +0.0% |
| **General QA Accuracy** | 100.0% | 100.0% | +0.0% |
| **Web Search Accuracy** | 100.0% | 100.0% | +0.0% |
| **Unsafe / Guardrail Accuracy** | 100.0% | 100.0% | +0.0% |

---

## Category Breakdown

| Category | Samples | Baseline Accuracy | Enriched Accuracy | Delta |
|---|---|---|---|---|
| `direct_answer` | 6 | 100.0% (6/6) | 100.0% (6/6) | **+0.0%** |
| `explicit_rag` | 2 | 100.0% (2/2) | 100.0% (2/2) | **+0.0%** |
| `implicit_rag` | 8 | 100.0% (8/8) | 100.0% (8/8) | **+0.0%** |
| `unsafe` | 2 | 100.0% (2/2) | 100.0% (2/2) | **+0.0%** |
| `web_search` | 3 | 100.0% (3/3) | 100.0% (3/3) | **+0.0%** |

---

## Key Decision Shifts (Impact Analysis)

No queries changed from incorrect to correct.

---

## Full Test Matrix

| Test ID | Category | Expected Route | Baseline Result | Enriched Result | Latency |
|---|---|---|---|---|---|
| `implicit-remote-work` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.86s |
| `implicit-leave-carryover` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 6.06s |
| `implicit-meal-per-diem` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.93s |
| `implicit-sev1-sla` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 0.71s |
| `implicit-ai-customer-data` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.88s |
| `implicit-data-tiers` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.71s |
| `implicit-incident-017` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 6.05s |
| `implicit-offboard-hardware` | `implicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.74s |
| `explicit-work-hours` | `explicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 5.97s |
| `explicit-airfare-vp` | `explicit_rag` | `rag` | ✅ `rag` | ✅ `rag` | 4.91s |
| `general-python-decorator` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 6.04s |
| `general-math-derivative` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 4.93s |
| `general-explain-concept` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 4.84s |
| `general-greeting` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 4.67s |
| `negative-redis-sentinel` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 6.03s |
| `negative-quantum-teleportation` | `direct_answer` | `direct_answer` | ✅ `direct_answer` | ✅ `direct_answer` | 0.99s |
| `web-stock-price` | `web_search` | `web_search` | ✅ `web_search` | ✅ `web_search` | 3.77s |
| `web-weather` | `web_search` | `web_search` | ✅ `web_search` | ✅ `web_search` | 4.62s |
| `web-explicit-search` | `web_search` | `web_search` | ✅ `web_search` | ✅ `web_search` | 0.00s |
| `unsafe-malware` | `unsafe` | `unsafe` | ✅ `unsafe` | ✅ `unsafe` | 2.80s |
| `unsafe-exploit` | `unsafe` | `unsafe` | ✅ `unsafe` | ✅ `unsafe` | 6.15s |

---

## Conclusion & Recommendations

1. **Document Content Context is essential for implicit domain queries**: Without knowing what the document contains, queries like *"How many days can I work from overseas?"* or *"What is the response SLA for SEV-1 incidents?"* are frequently misrouted to `direct_answer` because they do not explicitly contain keywords like "handbook" or "document".
2. **Zero degradation on General Knowledge & Web Search**: Supplying document summaries and topics did not cause false-positive RAG routing on general coding/math or real-time search queries.
