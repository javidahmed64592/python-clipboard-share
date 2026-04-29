"""FastAPI server module for clipboard sharing."""

import logging
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from python_clipboard_share.models import (
    AddEntryRequest,
    AddEntryResponse,
    ClipboardHistoryArchive,
    ClipboardHistoryEntry,
    ClipboardServerConfig,
    DeleteEntryRequest,
    DeleteEntryResponse,
    GetHistoryResponse,
    ModifyEntryRequest,
    ModifyEntryResponse,
)

logger = logging.getLogger(__name__)


class ClipboardServer(TemplateServer):
    """Clipboard FastAPI server."""

    def __init__(self, config: ClipboardServerConfig | None = None) -> None:
        """Initialize the ClipboardServer.

        :param ClipboardServerConfig | None config: Optional pre-loaded configuration
        """
        self.config: ClipboardServerConfig
        super().__init__(
            package_name="python-clipboard-share",
            config=config,
        )

        logger.info("Initializing ClipboardServer with history file: %s", self.archive_file)
        self.archive_file.parent.mkdir(parents=True, exist_ok=True)
        self._clipboard_history = ClipboardHistoryArchive.load_from_file(file_path=self.archive_file)

    @property
    def archive_file(self) -> Path:
        """Get the full path to the clipboard history archive file."""
        return self.config.archive_config.archive_directory / self.config.archive_config.archive_filename

    def validate_config(self, config_data: dict[str, Any]) -> ClipboardServerConfig:
        """Validate configuration data against the ClipboardServerConfig model.

        :param dict config_data: The configuration data to validate
        :return ClipboardServerConfig: The validated configuration model
        """
        return ClipboardServerConfig.model_validate(config_data)  # type: ignore[no-any-return]

    def setup_routes(self) -> None:
        """Add custom API routes."""
        self.add_authenticated_route(
            endpoint="/clipboard/history",
            handler_function=self.get_history,
            response_model=GetHistoryResponse,
            methods=["GET"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/clipboard/add",
            handler_function=self.add_entry,
            response_model=AddEntryResponse,
            methods=["POST"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/clipboard/delete",
            handler_function=self.delete_entry,
            response_model=DeleteEntryResponse,
            methods=["POST"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/clipboard/modify",
            handler_function=self.modify_entry,
            response_model=ModifyEntryResponse,
            methods=["POST"],
            limited=True,
        )

    def _save_history(self) -> None:
        """Save the current clipboard history to the archive file."""
        self._clipboard_history.save_to_file(self.archive_file)

    async def get_history(self, request: Request) -> GetHistoryResponse:
        """Get clipboard history.

        :param Request request: The incoming HTTP request
        :return GetHistoryResponse: Clipboard history response
        """
        logger.info("Retrieving clipboard history, total entries: %d", len(self._clipboard_history.entries))
        return GetHistoryResponse(
            message="Clipboard history retrieved successfully",
            history=self._clipboard_history,
        )

    async def add_entry(self, request: Request, body: AddEntryRequest) -> AddEntryResponse:
        """Add a new entry to the clipboard history.

        :param Request request: The incoming HTTP request
        :param AddEntryRequest body: The request body containing entry details
        :return AddEntryResponse: Response containing the ID of the added entry
        """
        new_entry = ClipboardHistoryEntry.new_entry(
            title=body.title,
            content=body.content,
        )
        self._clipboard_history.add_entry(new_entry)
        self._save_history()
        logger.info("Added new clipboard entry with ID: %s", new_entry.id)
        return AddEntryResponse(
            message="Clipboard entry added successfully",
            id=new_entry.id,
        )

    async def delete_entry(self, request: Request, body: DeleteEntryRequest) -> DeleteEntryResponse:
        """Delete an entry from the clipboard history.

        :param Request request: The incoming HTTP request
        :param DeleteEntryRequest body: The request body containing the ID of the entry to delete
        :return DeleteEntryResponse: Response containing the ID of the deleted entry
        :raise HTTPException: If the entry is not found
        """
        success = self._clipboard_history.delete_entry(entry_id=body.id)
        if not success:
            logger.warning("Failed to delete clipboard entry with ID: %s - entry not found", body.id)
            raise HTTPException(status_code=ResponseCode.NOT_FOUND, detail="Clipboard entry not found")

        self._save_history()
        logger.info("Deleted clipboard entry with ID: %s", body.id)
        return DeleteEntryResponse(
            message="Clipboard entry deleted successfully",
            id=body.id,
        )

    async def modify_entry(self, request: Request, body: ModifyEntryRequest) -> ModifyEntryResponse:
        """Modify an existing entry in the clipboard history.

        :param Request request: The incoming HTTP request
        :param ModifyEntryRequest body: The request body containing the ID and new details of the entry to modify
        :return ModifyEntryResponse: Response containing the ID of the modified entry
        :raise HTTPException: If the entry is not found
        """
        success = self._clipboard_history.modify_entry(
            entry_id=body.id,
            title=body.title,
            content=body.content,
        )
        if not success:
            logger.warning("Failed to modify clipboard entry with ID: %s - entry not found", body.id)
            raise HTTPException(status_code=ResponseCode.NOT_FOUND, detail="Clipboard entry not found")

        self._save_history()
        logger.info("Modified clipboard entry with ID: %s", body.id)
        return ModifyEntryResponse(
            message="Clipboard entry modified successfully",
            id=body.id,
        )
