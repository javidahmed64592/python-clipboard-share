"""Unit tests for the python_clipboard_share.server module."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Security
from fastapi.routing import APIRoute
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient
from python_template_server.models import ResponseCode

from python_clipboard_share.models import (
    AddEntryRequest,
    ClipboardHistoryArchive,
    ClipboardHistoryEntry,
    ClipboardServerConfig,
    DeleteEntryRequest,
    ModifyEntryRequest,
)
from python_clipboard_share.server import ClipboardServer


@pytest.fixture(autouse=True)
def mock_package_metadata() -> Generator[MagicMock]:
    """Mock importlib.metadata.metadata to return a mock PackageMetadata."""
    with patch("python_template_server.template_server.metadata") as mock_metadata:
        mock_pkg_metadata = MagicMock(spec=PackageMetadata)
        metadata_dict = {
            "Name": "python-clipboard-share",
            "Version": "0.1.0",
            "Summary": "A lightweight FastAPI application to share text across devices.",
        }
        mock_pkg_metadata.__getitem__.side_effect = lambda key: metadata_dict[key]
        mock_metadata.return_value = mock_pkg_metadata
        yield mock_metadata


@pytest.fixture
def mock_server(
    mock_clipboard_server_config: ClipboardServerConfig, mock_clipboard_history_archive: ClipboardHistoryArchive
) -> Generator[ClipboardServer]:
    """Provide a ClipboardServer instance for testing."""

    async def fake_verify_api_key(
        api_key: str | None = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
    ) -> None:
        """Fake verify API key that accepts the security header and always succeeds in tests."""
        return

    with (
        patch.object(ClipboardServer, "_verify_api_key", new=fake_verify_api_key),
        patch("python_clipboard_share.server.ClipboardServerConfig.save_to_file"),
        patch(
            "python_clipboard_share.server.ClipboardHistoryArchive.load_from_file",
            return_value=mock_clipboard_history_archive,
        ),
    ):
        server = ClipboardServer(config=mock_clipboard_server_config)
        yield server


@pytest.fixture
def mock_client(mock_server: ClipboardServer) -> TestClient:
    """Provide a TestClient for the mock server."""
    return TestClient(mock_server.app)


class TestClipboardServer:
    """Unit tests for the ClipboardServer class."""

    def test_init(self, mock_server: ClipboardServer) -> None:
        """Test ClipboardServer initialization."""
        assert isinstance(mock_server.config, ClipboardServerConfig)
        assert isinstance(mock_server._clipboard_history, ClipboardHistoryArchive)

    def test_archive_file_property(self, mock_server: ClipboardServer) -> None:
        """Test the archive_file property returns the correct path."""
        expected_path = mock_server.archive_file.parent
        assert expected_path.exists()
        assert expected_path.is_dir()

    def test_validate_config(
        self, mock_server: ClipboardServer, mock_clipboard_server_config: ClipboardServerConfig
    ) -> None:
        """Test configuration validation."""
        config_dict = mock_clipboard_server_config.model_dump()
        validated_config = mock_server.validate_config(config_dict)
        assert validated_config == mock_clipboard_server_config

    def test_validate_config_invalid_returns_default(self, mock_server: ClipboardServer) -> None:
        """Test invalid configuration returns default configuration."""
        invalid_config = {"invalid": None}
        validated_config = mock_server.validate_config(invalid_config)
        assert isinstance(validated_config, ClipboardServerConfig)


class TestClipboardServerRoutes:
    """Integration tests for the ClipboardServer routes."""

    def test_setup_routes(self, mock_server: ClipboardServer) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_server.app.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/health",
            "/login",
            "/clipboard/history",
            "/clipboard/add",
            "/clipboard/delete",
            "/clipboard/modify",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes


class TestGetClipboardHistoryEndpoint:
    """Integration tests for the /clipboard/history endpoint."""

    def test_get_history(self, mock_server: ClipboardServer) -> None:
        """Test the /clipboard/history endpoint method."""
        request = MagicMock()
        response = asyncio.run(mock_server.get_history(request))

        assert response.message == "Clipboard history retrieved successfully"
        assert response.history == mock_server._clipboard_history

    def test_get_clipboard_history_endpoint(self, mock_client: TestClient) -> None:
        """Test /clipboard/history endpoint returns 200."""
        response = mock_client.get("/clipboard/history")
        assert response.status_code == ResponseCode.OK


class TestAddClipboardEntryEndpoint:
    """Integration tests for the /clipboard/add endpoint."""

    @pytest.fixture
    def mock_add_entry_request(self) -> AddEntryRequest:
        """Provide a mock AddEntryRequest instance."""
        return AddEntryRequest(title="Test Entry", content="This is a test clipboard entry.")

    def test_add_entry(self, mock_server: ClipboardServer, mock_add_entry_request: AddEntryRequest) -> None:
        """Test the /clipboard/add endpoint method."""
        request = MagicMock()
        response = asyncio.run(mock_server.add_entry(request, mock_add_entry_request))
        assert response.message == "Clipboard entry added successfully"
        assert isinstance(response.id, str)

    def test_add_clipboard_entry_endpoint(
        self, mock_client: TestClient, mock_add_entry_request: AddEntryRequest
    ) -> None:
        """Test /clipboard/add endpoint returns 200."""
        response = mock_client.post("/clipboard/add", json=mock_add_entry_request.model_dump())
        assert response.status_code == ResponseCode.OK


class TestDeleteClipboardEntryEndpoint:
    """Integration tests for the /clipboard/delete endpoint."""

    @pytest.fixture
    def mock_delete_entry_request(self, mock_clipboard_history_entry: ClipboardHistoryEntry) -> DeleteEntryRequest:
        """Provide a mock DeleteEntryRequest instance."""
        return DeleteEntryRequest(id=mock_clipboard_history_entry.id)

    def test_delete_entry(self, mock_server: ClipboardServer, mock_delete_entry_request: DeleteEntryRequest) -> None:
        """Test the /clipboard/delete endpoint method."""
        request = MagicMock()
        response = asyncio.run(mock_server.delete_entry(request, mock_delete_entry_request))
        assert response.message == "Clipboard entry deleted successfully"
        assert response.id == mock_delete_entry_request.id

    def test_delete_entry_not_found(
        self, mock_server: ClipboardServer, mock_delete_entry_request: DeleteEntryRequest
    ) -> None:
        """Test the /clipboard/delete endpoint method when the entry is not found."""
        request = MagicMock()
        mock_delete_entry_request.id = "non-existent-id"
        with pytest.raises(HTTPException, match=r"Clipboard entry not found"):
            asyncio.run(mock_server.delete_entry(request, mock_delete_entry_request))

    def test_delete_clipboard_entry_endpoint(
        self, mock_client: TestClient, mock_delete_entry_request: DeleteEntryRequest
    ) -> None:
        """Test /clipboard/delete endpoint returns 200."""
        response = mock_client.post("/clipboard/delete", json=mock_delete_entry_request.model_dump())
        assert response.status_code == ResponseCode.OK


class TestModifyClipboardEntryEndpoint:
    """Integration tests for the /clipboard/modify endpoint."""

    @pytest.fixture
    def mock_modify_entry_request(self, mock_clipboard_history_entry: ClipboardHistoryEntry) -> ModifyEntryRequest:
        """Provide a mock ModifyEntryRequest instance."""
        return ModifyEntryRequest(
            id=mock_clipboard_history_entry.id,
            title="Modified Title",
            content="Modified content for the clipboard entry.",
        )

    def test_modify_entry(self, mock_server: ClipboardServer, mock_modify_entry_request: ModifyEntryRequest) -> None:
        """Test the /clipboard/modify endpoint method."""
        request = MagicMock()
        response = asyncio.run(mock_server.modify_entry(request, mock_modify_entry_request))
        assert response.message == "Clipboard entry modified successfully"
        assert response.id == mock_modify_entry_request.id

    def test_modify_entry_not_found(
        self, mock_server: ClipboardServer, mock_modify_entry_request: ModifyEntryRequest
    ) -> None:
        """Test the /clipboard/modify endpoint method when the entry is not found."""
        request = MagicMock()
        mock_modify_entry_request.id = "non-existent-id"
        with pytest.raises(HTTPException, match=r"Clipboard entry not found"):
            asyncio.run(mock_server.modify_entry(request, mock_modify_entry_request))

    def test_modify_clipboard_entry_endpoint(
        self, mock_client: TestClient, mock_modify_entry_request: ModifyEntryRequest
    ) -> None:
        """Test /clipboard/modify endpoint returns 200."""
        response = mock_client.post("/clipboard/modify", json=mock_modify_entry_request.model_dump())
        assert response.status_code == ResponseCode.OK
