"""
Utility script to generate and save a visual PNG diagram of the compiled LangGraph CRAG workflow.
Usage:
    python generate_graph_image.py
"""
import os
from crag.graph import _crag_graph

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "crag_workflow_graph.png")

def main():
    print("Generating visual graph diagram from compiled LangGraph...")
    try:
        png_bytes = _crag_graph.get_graph().draw_mermaid_png()
        with open(OUTPUT_PATH, "wb") as f:
            f.write(png_bytes)
        print(f"Graph image successfully saved to: {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error rendering PNG: {e}")

if __name__ == "__main__":
    main()
