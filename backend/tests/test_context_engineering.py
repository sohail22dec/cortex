from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.documents import Document

from rag.document_processor import extract_structural_topics
from rag import vector_store as vs
from services.router_service import (
    RouteDecision,
    _build_system_prompt,
    _format_documents,
    classify_async,
)


class TestContextEngineering(unittest.TestCase):
    def test_schema_reasoning_first(self):
        """Ensure reason field is defined before route for autoregressive scratchpad benefit."""
        fields = list(RouteDecision.model_fields.keys())
        self.assertEqual(fields[0], "reason")
        self.assertEqual(fields[1], "route")

    def test_dynamic_token_pruning_no_docs(self):
        """When has_documents is False, RAG instructions should be omitted to minimize prompt tokens."""
        prompt = _build_system_prompt(has_documents=False, documents=[])
        self.assertIn("DISABLED", prompt)
        self.assertNotIn("Active Uploaded Documents:", prompt)

    def test_dynamic_prompt_with_document_topics(self):
        """When documents with topics are provided, they should be formatted into the prompt."""
        docs = [
            {"filename": "handbook.pdf", "topics": "Travel reimbursement, meals, taxi expenses, PTO"},
            {"filename": "architecture.pdf", "topics": "Redis caching, API gateway"},
        ]
        prompt = _build_system_prompt(has_documents=True, documents=docs)
        self.assertIn('"handbook.pdf" (Topics: Travel reimbursement, meals, taxi expenses, PTO)', prompt)
        self.assertIn('"architecture.pdf" (Topics: Redis caching, API gateway)', prompt)
        self.assertIn("Today's date is:", prompt)

    def test_extract_structural_topics_markdown(self):
        """Test zero-token heading extraction on markdown text."""
        md_text = (
            "# Employee Benefits Handbook\n\n"
            "Introductory text.\n\n"
            "## 1. Expense Reimbursement\n\n"
            "Details about taxis and travel.\n\n"
            "## 2. Health & Dental Insurance\n\n"
            "Details about coverage.\n\n"
            "### Dental Deductible\n\n"
            "Coverage details."
        )
        docs = [Document(page_content=md_text)]
        topics = extract_structural_topics(tmp_path="dummy.md", suffix=".md", docs=docs)
        self.assertIn("Employee Benefits Handbook", topics)
        self.assertIn("1. Expense Reimbursement", topics)
        self.assertIn("2. Health & Dental Insurance", topics)

    def test_extract_structural_topics_fallback(self):
        """Test fallback topic extraction when no markdown headers are present."""
        plain_text = (
            "Corporate Travel Policy\n"
            "Guidelines for all employee flights and hotels.\n\n"
            "Meal Allowances\n"
            "Breakfast: $15, Lunch: $25, Dinner: $40.\n\n"
            "Car Rentals\n"
            "Economy car bookings only."
        )
        docs = [Document(page_content=plain_text)]
        topics = extract_structural_topics(tmp_path="dummy.txt", suffix=".txt", docs=docs)
        self.assertTrue(len(topics) > 0)
        self.assertIn("Corporate Travel Policy", topics)

    @patch("rag.vector_store._get_client")
    def test_save_document_meta_upsert(self, mock_get_client):
        """Test saving document metadata to the Supabase documents table."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_get_client.return_value = mock_client

        vs.save_document_meta(
            session_id="session-123",
            filename="policy.pdf",
            topics="Travel, PTO",
            user_id="user-456",
        )

        mock_client.table.assert_called_with("documents")
        mock_table.upsert.assert_called_once()
        call_args, call_kwargs = mock_table.upsert.call_args
        self.assertEqual(call_args[0]["session_id"], "session-123")
        self.assertEqual(call_args[0]["filename"], "policy.pdf")
        self.assertEqual(call_args[0]["topics"], "Travel, PTO")
        self.assertEqual(call_args[0]["user_id"], "user-456")
        self.assertEqual(call_kwargs.get("on_conflict"), "session_id,filename")

    @patch("rag.vector_store._get_client")
    def test_get_document_profiles_success(self, mock_get_client):
        """Test retrieving document profiles from documents table."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_execute = MagicMock()

        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_execute
        mock_execute.data = [
            {"filename": "handbook.pdf", "topics": "Travel, PTO"},
            {"filename": "spec.pdf", "topics": "API, Redis"},
        ]
        mock_get_client.return_value = mock_client

        profiles = vs.get_document_profiles("session-123")
        self.assertEqual(len(profiles), 2)
        self.assertEqual(profiles[0]["filename"], "handbook.pdf")
        self.assertEqual(profiles[0]["topics"], "Travel, PTO")

    @patch("rag.vector_store._get_client")
    @patch("rag.vector_store.list_document_names")
    def test_get_document_profiles_fallback(self, mock_list_names, mock_get_client):
        """Test fallback to list_document_names when documents table errors."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Table not found")
        mock_get_client.return_value = mock_client
        mock_list_names.return_value = ["manual.pdf"]

        profiles = vs.get_document_profiles("session-123")
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["filename"], "manual.pdf")
        self.assertEqual(profiles[0]["topics"], "")


if __name__ == "__main__":
    unittest.main()
