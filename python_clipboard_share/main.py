"""FastAPI Clipboard server using uvicorn."""

from python_clipboard_share.server import ClipboardServer


def run() -> None:
    """Serve the FastAPI application using uvicorn.

    :raise SystemExit: If configuration fails to load or SSL certificate files are missing
    """
    server = ClipboardServer()
    server.run()
