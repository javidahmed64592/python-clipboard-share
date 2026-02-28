"""Unit tests for the python_clipboard_share.main module."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from python_clipboard_share.main import run
from python_clipboard_share.models import ClipboardServerConfig


@pytest.fixture
def mock_clipboard_server_class(
    mock_clipboard_server_config: ClipboardServerConfig,
) -> Generator[MagicMock]:
    """Mock ClipboardServer class."""
    with patch("python_clipboard_share.main.ClipboardServer") as mock_server:
        mock_server.load_config.return_value = mock_clipboard_server_config
        yield mock_server


class TestRun:
    """Unit tests for the run function."""

    def test_run(self, mock_clipboard_server_class: MagicMock) -> None:
        """Test successful server run."""
        run()

        mock_clipboard_server_class.return_value.run.assert_called_once()
