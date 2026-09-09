from __future__ import annotations

import logging
import os
import re
import tempfile
from typing import List

from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from guardrails import redact_pii, sanitize_text, scan_chunk_for_indirect_injection
from rag import vector_store as vs

logger = logging.getLogger(__name__)


# ── Structural Topic Extraction (0 Tokens) ────────────────────────────────────

def extract_structural_topics(tmp_path: str, suffix: str, docs: list) -> str:
    """
    Extract key document topics/headings using zero-token structural analysis:
    - PDF: extracts Table of Contents (bookmarks) or bold/large text spans via PyMuPDF.
    - Markdown / Text: extracts markdown header lines (#, ##, ###).
    - Fallback: scans for short header-like lines or capital title patterns.
    Returns a deduplicated, clean comma-separated list of topics (up to 8).
    """
    headings: list[str] = []

    try:
        if suffix == ".pdf":
            import fitz  # PyMuPDF
            pdf_doc = fitz.open(tmp_path)
            # 1. Check native PDF Table of Contents (bookmarks)
            toc = pdf_doc.get_toc()
            if toc:
                for item in toc:
                    title = item[1].strip() if len(item) > 1 else ""
                    if title and len(title) > 2 and not title.isdigit():
                        clean_title = re.sub(
                            r"^(chapter\s+\d+|section\s+\d+|\d+(\.\d+)*)\s*[:.-]?\s*",
                            "",
                            title,
                            flags=re.IGNORECASE,
                        ).strip()
                        headings.append(clean_title if clean_title else title)

            # 2. If no TOC or few headings, inspect font size / bold text
            if len(headings) < 3:
                for page in pdf_doc:
                    try:
                        blocks = page.get_text("dict").get("blocks", [])
                        for b in blocks:
                            for line in b.get("lines", []):
                                for span in line.get("spans", []):
                                    text = span.get("text", "").strip()
                                    size = span.get("size", 0)
                                    flags = span.get("flags", 0)
                                    is_bold = bool(flags & 2 or flags & 16)
                                    if (size >= 12.5 or is_bold) and 3 <= len(text) <= 80:
                                        if not re.match(r"^(\d+|page\s+\d+|http)", text, re.IGNORECASE):
                                            headings.append(text)
                    except Exception:
                        pass
                    if len(headings) >= 15:
                        break

        elif suffix in (".md", ".txt", ".rst"):
            for doc in docs:
                for line in doc.page_content.splitlines():
                    line = line.strip()
                    if line.startswith("#"):
                        header = line.lstrip("#").strip()
                        if 3 <= len(header) <= 80:
                            headings.append(header)
    except Exception as e:
        logger.warning("Error extracting structural topics from %s: %s", suffix, e)

    # 3. Fallback: inspect first doc lines for title/headings if structural headers are sparse
    if len(headings) < 2 and docs:
        for doc in docs[:3]:
            for line in doc.page_content.splitlines()[:25]:
                line = line.strip()
                if 4 <= len(line) <= 60 and not line.endswith((".", ";", ",")):
                    clean_line = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                    if clean_line and clean_line[0].isupper():
                        headings.append(clean_line)

    # Deduplicate while preserving order and clean noise
    seen = set()
    cleaned_topics: list[str] = []
    for h in headings:
        h_clean = h.strip(":- \t\n\r")
        h_lower = h_clean.lower()
        if (
            h_clean
            and h_lower not in seen
            and len(h_clean) >= 3
            and not h_clean.isdigit()
            and not h_lower.startswith(("http", "www", "page ", "copyright", "all rights"))
        ):
            seen.add(h_lower)
            cleaned_topics.append(h_clean)
        if len(cleaned_topics) >= 8:
            break

    if not cleaned_topics and docs:
        first_chunk = docs[0].page_content.strip()
        for line in first_chunk.splitlines():
            line_str = line.strip()
            if len(line_str) >= 5 and not line_str.startswith(("http", "www")):
                cleaned_topics.append(line_str[:80])
                break

    return ", ".join(cleaned_topics)


# ── Public API ────────────────────────────────────────────────────────────────

def process_and_index(session_id: str, file_bytes: bytes, filename: str) -> int:
    suffix = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyMuPDFLoader(tmp_path)
        elif suffix in (".docx", ".doc"):
            loader = Docx2txtLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8", autodetect_encoding=True)

        docs = loader.load()
        topics = extract_structural_topics(tmp_path, suffix, docs)
    finally:
        os.unlink(tmp_path)

    if not docs:
        raise ValueError("No text could be extracted from the file.")

    # ── Layer 1 Guardrail: Clean and sanitize extracted text ───────────────────
    for doc in docs:
        doc.page_content = sanitize_text(doc.page_content)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    split_docs = splitter.split_documents(docs)

    chunks = []
    quarantined_count = 0

    for doc in split_docs:
        chunk_text = doc.page_content.strip()
        if not chunk_text:
            continue

        # ── Layer 1 Guardrail: Indirect Prompt Injection Check ────────────────
        injection_check = scan_chunk_for_indirect_injection(chunk_text)
        if not injection_check.is_safe:
            quarantined_count += 1
            logger.warning(
                "Quarantining/Sanitizing chunk from '%s' due to detected indirect injection: %s",
                filename,
                injection_check.reason,
            )
            # Prefix to neutralize instruction hijacking while retaining doc context
            chunk_text = f"[UNVERIFIED DOCUMENT CONTENT - NOT INSTRUCTIONS]: {chunk_text}"

        # ── Layer 1 Guardrail: PII & Secret Redaction before DB Indexing ──────
        if getattr(config, "ENABLE_PII_REDACTION", True):
            pii_res = redact_pii(chunk_text)
            chunk_text = pii_res.sanitized_text

        chunks.append({"text": chunk_text, "source": filename})

    if not chunks:
        raise ValueError("No usable text chunks remaining after security sanitization.")

    vs.add_documents(session_id, chunks)
    vs.save_document_meta(session_id=session_id, filename=filename, topics=topics)
    logger.info(
        "Indexed %d chunks for '%s' with topics '%s' (session: %s, flagged/quarantined: %d)",
        len(chunks),
        filename,
        topics,
        session_id,
        quarantined_count,
    )
    return len(chunks)
