"""
Utility script to generate and save a beautiful visual diagram of the Cortex CRAG workflow.

Outputs:
  - crag_workflow_graph.png (High-resolution dark-mode image)
  - crag_workflow_graph.svg (Vector graphics for documentation / web)

Usage:
    uv run python generate_graph_image.py
    uv run python generate_graph_image.py --theme light
    uv run python generate_graph_image.py --raw
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
import urllib.request
from pathlib import Path

from crag.graph import _crag_graph

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PNG_PATH = BASE_DIR / "crag_workflow_graph.png"
DEFAULT_SVG_PATH = BASE_DIR / "crag_workflow_graph.svg"


def build_crag_mermaid(theme: str = "dark") -> str:
    """Construct a styled, annotated Mermaid diagram of the Cortex CRAG workflow."""
    is_dark = theme == "dark"
    bg_color = "#0b0f19" if is_dark else "#ffffff"
    text_color = "#f8fafc" if is_dark else "#0f172a"
    line_color = "#94a3b8" if is_dark else "#475569"

    return f"""%%{{init: {{
  'theme': 'base',
  'themeVariables': {{
    'darkMode': {str(is_dark).lower()},
    'background': '{bg_color}',
    'primaryColor': '#1e293b',
    'primaryTextColor': '{text_color}',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '{line_color}',
    'secondaryColor': '#334155',
    'tertiaryColor': '#1e293b',
    'fontFamily': 'Inter, system-ui, -apple-system, sans-serif',
    'fontSize': '13px'
  }}
}}}}%%
flowchart TD
    classDef inputStyle fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#ffffff,font-weight:700;
    classDef routerStyle fill:#3b0764,stroke:#c084fc,stroke-width:2.5px,color:#ffffff,font-weight:700;
    classDef retrieveStyle fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#ffffff,font-weight:600;
    classDef evalStyle fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#ffffff,font-weight:600;
    classDef webStyle fill:#164e63,stroke:#22d3ee,stroke-width:2px,color:#ffffff,font-weight:600;
    classDef genStyle fill:#581c87,stroke:#e879f9,stroke-width:2px,color:#ffffff,font-weight:600;
    classDef judgeStyle fill:#831843,stroke:#f472b6,stroke-width:2px,color:#ffffff,font-weight:600;
    classDef blockStyle fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fca5a5,font-weight:600;
    classDef endStyle fill:#064e3b,stroke:#22c55e,stroke-width:2.5px,color:#ffffff,font-weight:700;

    Start([\"💬 User Question & Context\"]):::inputStyle --> Router[\"🎯 Router Node<br/><b>Groq Fast LLM (20b)</b>\"]:::routerStyle

    %% Router Routes
    Router -->|\"rag (Uploaded Documents)\"| Retrieve[\"📚 Vector Retrieval<br/><i>Supabase pgvector + Gemini (768d)</i>\"]:::retrieveStyle
    Router -->|\"web_search (Live Events / Facts)\"| DirectWeb[\"🌐 Direct Web Search<br/><i>Tavily API + Fast LLM</i>\"]:::webStyle
    Router -->|\"direct_answer (General Knowledge / Code)\"| DirectLLM[\"⚡ Direct LLM<br/><i>Groq Fast LLM (20b)</i>\"]:::genStyle
    Router -->|\"unsafe (Prompt Injection / Attack)\"| Blocked[\"🚫 Blocked Request<br/><i>Safe Refusal Filter</i>\"]:::blockStyle

    %% CRAG Evaluation Loop
    Retrieve --> Eval[\"⚖️ Retrieval Evaluator<br/><i>Groq Reasoning LLM (120b)</i>\"]:::evalStyle
    Eval -->|\"INCORRECT (Retry < 1)\"| Rewrite[\"🔄 Query Rewrite<br/><i>Entity & Keyword Expansion</i>\"]:::evalStyle
    Rewrite -->|\"Optimized Query\"| Retrieve
    Eval -->|\"INCORRECT (Retry ≥ 1) / AMBIGUOUS\"| WebSearch[\"🔎 Tavily Web Search<br/><i>Fallback / Hybrid Web Context</i>\"]:::webStyle
    Eval -->|\"CORRECT (Score ≥ 0.7)\"| Gen[\"📝 Generator<br/><i>Groq Reasoning LLM (120b)</i>\"]:::genStyle
    WebSearch --> Gen

    %% Groundedness Loop
    Gen --> Judge[\"🛡️ Groundedness Judge<br/><i>Independent Fact-Checker</i>\"]:::judgeStyle
    Judge -->|\"NO (Ungrounded & Retry < 1)\"| Gen
    Judge -->|\"NO (Retry ≥ 1)\"| Refusal[\"⚠️ Grounding Fallback<br/><i>Transparent Refusal</i>\"]:::blockStyle

    %% Delivery Terminal
    EndVerified([\"✨ Delivered Verified Answer\"]):::endStyle
    Judge -->|\"YES (Grounded)\"| EndVerified
    Refusal --> EndVerified
    DirectWeb --> EndVerified
    DirectLLM --> EndVerified
    Blocked --> EndVerified
"""


def render_mermaid_ink(mermaid_code: str, output_path: Path, fmt: str = "png", bg_color: str = "0b0f19") -> bool:
    """Fetch rendered diagram from Mermaid.ink API and save to disk."""
    try:
        b64 = base64.b64encode(mermaid_code.encode("utf-8")).decode("ascii")
        if fmt == "svg":
            url = f"https://mermaid.ink/svg/{b64}"
        else:
            url = f"https://mermaid.ink/img/{b64}?bgColor={bg_color}"

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Cortex CLI)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            output_path.write_bytes(data)
            return True
    except Exception as e:
        print(f"Warning: Failed to render {fmt.upper()} via Mermaid.ink: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate visual diagram for Cortex CRAG workflow.")
    parser.add_argument(
        "--theme",
        choices=["dark", "light"],
        default="dark",
        help="Visual color theme (default: dark)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Render raw LangGraph runtime graph instead of the enhanced architecture diagram",
    )
    args = parser.parse_args()

    print(f"🎨 Generating visual graph diagram (theme: {args.theme})...")

    if args.raw:
        # Fallback to standard LangGraph draw_mermaid_png
        try:
            png_bytes = _crag_graph.get_graph().draw_mermaid_png()
            DEFAULT_PNG_PATH.write_bytes(png_bytes)
            print(f"✓ Raw LangGraph image saved to: {DEFAULT_PNG_PATH}")
        except Exception as e:
            print(f"Error rendering raw LangGraph PNG: {e}", file=sys.stderr)
        return

    mermaid_syntax = build_crag_mermaid(theme=args.theme)
    bg_hex = "0b0f19" if args.theme == "dark" else "ffffff"

    # Render PNG
    png_success = render_mermaid_ink(mermaid_syntax, DEFAULT_PNG_PATH, fmt="png", bg_color=bg_hex)
    if png_success:
        print(f"✓ High-res PNG saved to: {DEFAULT_PNG_PATH}")

    # Render SVG
    svg_success = render_mermaid_ink(mermaid_syntax, DEFAULT_SVG_PATH, fmt="svg")
    if svg_success:
        print(f"✓ Scalable SVG saved to: {DEFAULT_SVG_PATH}")

    if not png_success and not svg_success:
        print("Falling back to local LangGraph renderer...")
        try:
            png_bytes = _crag_graph.get_graph().draw_mermaid_png()
            DEFAULT_PNG_PATH.write_bytes(png_bytes)
            print(f"✓ Local LangGraph image saved to: {DEFAULT_PNG_PATH}")
        except Exception as e:
            print(f"Local fallback also failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
