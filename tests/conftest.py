"""Pytest fixtures for the application's unit tests."""

from pathlib import Path

import pytest

from python_clipboard_share.models import (
    ClipboardArchiveConfig,
    ClipboardHistoryArchive,
    ClipboardHistoryEntry,
    ClipboardServerConfig,
)


# General fixtures
@pytest.fixture
def mock_tmp_archive_path(tmp_path: Path) -> Path:
    """Provide a temporary archive file path."""
    return tmp_path / "archive.json"


# Clipboard Server Configuration Models
@pytest.fixture
def mock_clipboard_archive_config(mock_tmp_archive_path: Path) -> ClipboardArchiveConfig:
    """Provide a mock ClipboardArchiveConfig instance."""
    return ClipboardArchiveConfig(
        archive_directory=mock_tmp_archive_path.parent,
        archive_filename=mock_tmp_archive_path.name,
        max_clipboard_history=10,
    )


@pytest.fixture
def mock_clipboard_server_config(mock_clipboard_archive_config: ClipboardArchiveConfig) -> ClipboardServerConfig:
    """Provide a mock ClipboardServerConfig instance."""
    return ClipboardServerConfig(archive_config=mock_clipboard_archive_config)


# Archive Models
@pytest.fixture
def mock_clipboard_history_entry() -> ClipboardHistoryEntry:
    """Provide a mock ClipboardHistoryEntry instance."""
    return ClipboardHistoryEntry(
        id="test-id",
        title="Test Entry",
        content="This is a test clipboard entry.",
    )


@pytest.fixture
def mock_clipboard_history_archive(mock_clipboard_history_entry: ClipboardHistoryEntry) -> ClipboardHistoryArchive:
    """Provide a mock ClipboardHistoryArchive instance."""
    return ClipboardHistoryArchive(
        entries=[mock_clipboard_history_entry],
    )
