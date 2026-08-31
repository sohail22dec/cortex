from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from rag import storage_service


class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("rag.storage_service._get_client")
    def test_upload_file_service(self, mock_get_client):
        mock_storage = MagicMock()
        mock_from = MagicMock()
        mock_get_client.return_value.storage = mock_storage
        mock_storage.list_buckets.return_value = [MagicMock(name="documents")]
        mock_storage.from_.return_value = mock_from

        path = storage_service.upload_file(
            session_id="sess-123",
            filename="sample.pdf",
            file_bytes=b"sample content",
            content_type="application/pdf",
        )
        self.assertEqual(path, "sess-123/sample.pdf")
        mock_storage.from_.assert_called_with("documents")
        mock_from.upload.assert_called_once()

    @patch("rag.storage_service._get_client")
    def test_get_signed_url_service(self, mock_get_client):
        mock_storage = MagicMock()
        mock_from = MagicMock()
        mock_get_client.return_value.storage = mock_storage
        mock_storage.from_.return_value = mock_from
        mock_from.create_signed_url.return_value = {"signedURL": "https://signed.url/sample.pdf"}

        url = storage_service.get_signed_url("sess-123", "sample.pdf")
        self.assertEqual(url, "https://signed.url/sample.pdf")

    @patch("api.documents.storage_service.get_signed_url")
    def test_get_document_url_endpoint(self, mock_get_url):
        mock_get_url.return_value = "https://mock.supabase.co/storage/sample.pdf"
        res = self.client.get("/api/documents/sample.pdf/url?session_id=sess-123")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["filename"], "sample.pdf")
        self.assertEqual(data["url"], "https://mock.supabase.co/storage/sample.pdf")
