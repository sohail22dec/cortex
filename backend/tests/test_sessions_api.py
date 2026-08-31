from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from services.conversation_service import delete_conversation
from rag import vector_store as vs


class TestSessionsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.chat.delete_conversation")
    @patch("api.chat.vs.delete_session_documents")
    def test_delete_session_endpoint_success(self, mock_delete_docs, mock_delete_conv):
        response = self.client.delete("/api/sessions/test-session-123")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("test-session-123", data["message"])
        mock_delete_conv.assert_called_once_with("test-session-123")
        mock_delete_docs.assert_called_once_with("test-session-123")

    @patch("services.conversation_service._get_client")
    def test_delete_conversation_service(self, mock_get_client):
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_eq = MagicMock()

        mock_get_client.return_value.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq

        delete_conversation("test-session-abc")

        mock_get_client.return_value.table.assert_called_once_with("conversations")
        mock_table.delete.assert_called_once()
        mock_delete.eq.assert_called_once_with("session_id", "test-session-abc")
        mock_eq.execute.assert_called_once()

    @patch("rag.vector_store._get_client")
    def test_delete_session_documents(self, mock_get_client):
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_eq = MagicMock()

        mock_get_client.return_value.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq

        vs.delete_session_documents("test-session-xyz")

        mock_get_client.return_value.table.assert_called_once_with("document_chunks")
        mock_table.delete.assert_called_once()
        mock_delete.eq.assert_called_once_with("session_id", "test-session-xyz")
        mock_eq.execute.assert_called_once()
