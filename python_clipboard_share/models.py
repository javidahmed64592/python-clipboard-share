"""Pydantic models for the server."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, TemplateServerConfig


# Clipboard Server Configuration Models
class ClipboardServerConfig(TemplateServerConfig):
    """Clipboard server configuration."""

    archive_directory: Path = Field(..., description="Directory to store clipboard history archives")
    archive_filename: str = Field(..., description="Filename for clipboard history archive")
    max_clipboard_history: int = Field(..., description="Maximum number of clipboard history entries to keep")


# Archive Models
class ClipboardHistoryEntry(BaseModel):
    """Model representing a single clipboard history entry."""

    id: str = Field(..., description="Unique identifier for the clipboard entry")
    title: str = Field(..., description="Title of the clipboard entry")
    content: str = Field(..., description="Content of the clipboard entry")

    @classmethod
    def new_entry(cls, title: str, content: str) -> ClipboardHistoryEntry:
        """Create a new clipboard history entry with a generated ID."""
        return cls(
            id=cls.generate_id(),
            title=title,
            content=content,
        )

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a clipboard entry."""
        return str(uuid.uuid4())


class ClipboardHistoryArchive(BaseModel):
    """Model representing a clipboard history archive."""

    entries: list[ClipboardHistoryEntry] = Field(..., description="List of clipboard history entries")

    @classmethod
    def load_from_file(cls, file_path: Path) -> ClipboardHistoryArchive:
        """Load clipboard history archive from a JSON file."""
        if not file_path.exists():
            return cls(entries=[])
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def save_to_file(self, file_path: Path) -> None:
        """Save clipboard history archive to a JSON file."""
        tmp_file_path = file_path.with_suffix(".tmp")

        try:
            with tmp_file_path.open("w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, ensure_ascii=False, indent=4)

            tmp_file_path.replace(file_path)
        except Exception:
            if tmp_file_path.exists():
                tmp_file_path.unlink()
            raise

    def add_entry(self, entry: ClipboardHistoryEntry) -> None:
        """Add a new entry to the clipboard history archive."""
        self.entries.append(entry)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry from the clipboard history archive by ID.

        :param str entry_id: The unique identifier of the entry to delete
        :return bool: True if the entry was found and deleted, False otherwise
        """
        for i, entry in enumerate(self.entries):
            if entry.id == entry_id:
                del self.entries[i]
                return True
        return False

    def modify_entry(self, entry_id: str, title: str, content: str) -> bool:
        """Modify an existing entry in the clipboard history archive by ID.

        :param str entry_id: The unique identifier of the entry to modify
        :param str title: The new title for the clipboard entry
        :param str content: The new content for the clipboard entry
        :return bool: True if the entry was found and modified, False otherwise
        """
        for entry in self.entries:
            if entry.id == entry_id:
                entry.title = title
                entry.content = content
                return True
        return False


# API Response Models
class GetHistoryResponse(BaseResponse):
    """Response model for retrieving clipboard history."""

    history: ClipboardHistoryArchive = Field(..., description="Clipboard history archive")


class AddEntryResponse(BaseResponse):
    """Response model for adding a clipboard entry."""

    id: str = Field(..., description="Unique identifier of the added clipboard entry")


class DeleteEntryResponse(BaseResponse):
    """Response model for deleting a clipboard entry."""

    id: str = Field(..., description="Unique identifier of the deleted clipboard entry")


class ModifyEntryResponse(BaseResponse):
    """Response model for modifying a clipboard entry."""

    id: str = Field(..., description="Unique identifier of the modified clipboard entry")


# API Request Models
class AddEntryRequest(BaseModel):
    """Model for adding a clipboard entry."""

    title: str = Field(..., description="Title of the clipboard entry")
    content: str = Field(..., description="Content of the clipboard entry")


class DeleteEntryRequest(BaseModel):
    """Model for deleting a clipboard entry."""

    id: str = Field(..., description="Unique identifier of the clipboard entry to delete")


class ModifyEntryRequest(BaseModel):
    """Model for modifying a clipboard entry."""

    id: str = Field(..., description="Unique identifier of the clipboard entry to modify")
    title: str = Field(..., description="New title of the clipboard entry")
    content: str = Field(..., description="New content of the clipboard entry")
