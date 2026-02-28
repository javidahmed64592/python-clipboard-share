"""Unit tests for the python_template_server.models module."""

from python_clipboard_share.models import (
    AddEntryRequest,
    AddEntryResponse,
    ClipboardArchiveConfig,
    ClipboardHistoryArchive,
    ClipboardHistoryEntry,
    ClipboardServerConfig,
    DeleteEntryRequest,
    DeleteEntryResponse,
    GetHistoryResponse,
    ModifyEntryRequest,
    ModifyEntryResponse,
)


# Clipboard Server Configuration Models
class TestClipboardServerConfig:
    """Unit tests for the ClipboardServerConfig class."""

    def test_model_dump(
        self, mock_clipboard_server_config: ClipboardServerConfig, mock_clipboard_archive_config: ClipboardArchiveConfig
    ) -> None:
        """Test the model_dump method."""
        assert mock_clipboard_server_config.archive_config.model_dump() == mock_clipboard_archive_config.model_dump()


# Archive Models
class TestClipboardHistoryEntry:
    """Unit tests for the ClipboardHistoryEntry class."""

    def test_model_dump(self, mock_clipboard_history_entry: ClipboardHistoryEntry) -> None:
        """Test the model_dump method."""
        expected_dict = {
            "id": mock_clipboard_history_entry.id,
            "title": mock_clipboard_history_entry.title,
            "content": mock_clipboard_history_entry.content,
        }
        assert mock_clipboard_history_entry.model_dump() == expected_dict

    def test_new_entry(self) -> None:
        """Test the new_entry class method."""
        title = "New Entry"
        content = "This is a new clipboard entry."
        entry = ClipboardHistoryEntry.new_entry(title=title, content=content)

        assert isinstance(entry.id, str)
        assert entry.title == title
        assert entry.content == content


class TestClipboardHistoryArchive:
    """Unit tests for the ClipboardHistoryArchive class."""

    def test_model_dump(self, mock_clipboard_history_archive: ClipboardHistoryArchive) -> None:
        """Test the model_dump method."""
        expected_dict = {
            "entries": [entry.model_dump() for entry in mock_clipboard_history_archive.entries],
        }
        assert mock_clipboard_history_archive.model_dump() == expected_dict

    def test_add_entry(self, mock_clipboard_history_archive: ClipboardHistoryArchive) -> None:
        """Test adding an entry to the archive."""
        initial_count = len(mock_clipboard_history_archive.entries)
        new_entry = ClipboardHistoryEntry.new_entry(title="Test Add", content="Testing add_entry method.")
        mock_clipboard_history_archive.entries.append(new_entry)

        assert len(mock_clipboard_history_archive.entries) == initial_count + 1
        assert mock_clipboard_history_archive.entries[-1] == new_entry

    def test_delete_entry(self, mock_clipboard_history_archive: ClipboardHistoryArchive) -> None:
        """Test deleting an entry from the archive."""
        entry_to_delete = mock_clipboard_history_archive.entries[0]
        result = mock_clipboard_history_archive.delete_entry(entry_id=entry_to_delete.id)

        assert result is True
        assert entry_to_delete not in mock_clipboard_history_archive.entries

    def test_modify_entry(self, mock_clipboard_history_archive: ClipboardHistoryArchive) -> None:
        """Test modifying an entry in the archive."""
        entry_to_modify = mock_clipboard_history_archive.entries[0]
        new_title = "Modified Title"
        new_content = "Modified content for testing."
        result = mock_clipboard_history_archive.modify_entry(
            entry_id=entry_to_modify.id,
            title=new_title,
            content=new_content,
        )

        assert result is True
        assert entry_to_modify.title == new_title
        assert entry_to_modify.content == new_content


# API Response Models
class TestGetHistoryResponse:
    """Unit tests for the GetHistoryResponse class."""

    def test_model_dump(self, mock_clipboard_history_archive: ClipboardHistoryArchive) -> None:
        """Test the model_dump method."""
        timestamp = GetHistoryResponse.current_timestamp()
        config_dict: dict = {
            "message": "Clipboard history retrieved successfully",
            "timestamp": timestamp,
            "history": mock_clipboard_history_archive.model_dump(),
        }
        response = GetHistoryResponse(**config_dict)
        assert response.model_dump() == config_dict


class TestAddEntryResponse:
    """Unit tests for the AddEntryResponse class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        timestamp = AddEntryResponse.current_timestamp()
        config_dict: dict = {
            "message": "Clipboard entry added successfully",
            "timestamp": timestamp,
            "id": "test-id-123",
        }
        response = AddEntryResponse(**config_dict)
        assert response.model_dump() == config_dict


class TestDeleteEntryResponse:
    """Unit tests for the DeleteEntryResponse class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        timestamp = DeleteEntryResponse.current_timestamp()
        config_dict: dict = {
            "message": "Clipboard entry deleted successfully",
            "timestamp": timestamp,
            "id": "test-id-456",
        }
        response = DeleteEntryResponse(**config_dict)
        assert response.model_dump() == config_dict


class TestModifyEntryResponse:
    """Unit tests for the ModifyEntryResponse class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        timestamp = ModifyEntryResponse.current_timestamp()
        config_dict: dict = {
            "message": "Clipboard entry modified successfully",
            "timestamp": timestamp,
            "id": "test-id-789",
        }
        response = ModifyEntryResponse(**config_dict)
        assert response.model_dump() == config_dict


# API Request Models
class TestAddEntryRequest:
    """Unit tests for the AddEntryRequest class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        config_dict: dict = {
            "title": "My Snippet",
            "content": "print('hello')",
        }
        request = AddEntryRequest(**config_dict)
        assert request.model_dump() == config_dict


class TestDeleteEntryRequest:
    """Unit tests for the DeleteEntryRequest class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        config_dict: dict = {"id": "entry-id-001"}
        request = DeleteEntryRequest(**config_dict)
        assert request.model_dump() == config_dict


class TestModifyEntryRequest:
    """Unit tests for the ModifyEntryRequest class."""

    def test_model_dump(self) -> None:
        """Test the model_dump method."""
        config_dict: dict = {
            "id": "entry-id-002",
            "title": "Updated Title",
            "content": "Updated content.",
        }
        request = ModifyEntryRequest(**config_dict)
        assert request.model_dump() == config_dict
