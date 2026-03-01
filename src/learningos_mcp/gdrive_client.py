"""
Persistent, importable Google Drive client for the learningOS MCP server.

Features
--------
- Singleton pattern → one authenticated client for the whole process lifetime.
- Async wrappers   → Google API client is synchronous; we delegate to a thread
                      so the MCP event-loop is never blocked.
- Retry with back-off for 429 / 5xx (rate-limits & transient errors).
- File-lock detection (Google Drive "capabilities.canEdit" check).
"""

from __future__ import annotations

import asyncio
import io
import logging
import time
from typing import Optional

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from learningos_mcp.auth import build_credentials
import os
import io

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------
_MAX_RETRIES = 5
_INITIAL_BACKOFF_S = 1.0
_BACKOFF_MULTIPLIER = 2.0
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503}


def _execute_with_retry(func, *args, **kwargs):
    """Execute a Google API request with exponential back-off on transient errors."""
    backoff = _INITIAL_BACKOFF_S
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            #if a Google API request is passed in, execute it
            # If it's a method (like next_chunk), call it directly
            if hasattr(func, 'execute'):
                return func.execute()
            else:
                return func(*args, **kwargs)
        except HttpError as exc:
            status = exc.resp.status if exc.resp else None
            if status in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES:
                logger.warning(
                    "Google API %s (attempt %d/%d) – retrying in %.1fs",
                    status,
                    attempt,
                    _MAX_RETRIES,
                    backoff,
                )
                time.sleep(backoff)
                backoff *= _BACKOFF_MULTIPLIER
            else:
                raise
        except Exception as exc:
            logger.error(f"Error executing function {func.__name__}: {exc}")
            raise


class GDriveManager:
    """Persistent Google Drive manager (singleton).

    Usage::

        from learningos_mcp.gdrive_client import GDriveManager

        mgr = GDriveManager.get_instance()

        # synchronous
        content = mgr.read_file(file_id)

        # async (non-blocking)
        content = await mgr.async_read_file(file_id)
    """

    _instance: Optional[GDriveManager] = None


    def __init__(self) -> None:
        creds = build_credentials()
        self._service: Resource = build("drive", "v3", credentials=creds)
        self.folder_id: str = os.getenv("GDRIVE_FOLDER_ID")
        self.file_id: str = os.getenv("GDRIVE_FILE_ID") or self._find_master_knowledge_graph()
        logger.info("GDriveManager initialised (Drive API v3)")

    @classmethod
    def get_instance(cls) -> GDriveManager:
        """Return (and lazily create) the process-wide singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def service(self) -> Resource:
        return self._service

    def read_master_knowledge_graph(self) -> str:
        """Load the contents of the master knowledge graph file into memory."""
        file_id = self.file_id
        request = self._service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)

        done = False
        while done is False:    
            status, done = _execute_with_retry(downloader.next_chunk)
            print(f"Download {int(status.progress() * 100)}%.")
        return file_buffer.getvalue().decode("utf-8")
    
    def write_master_knowledge_graph(self, content: str) -> None:
        """Write the contents to the master knowledge graph file."""
        
        file_metadata = {'name': 'master_knowledge_graph.md', 'parents': [self.folder_id]}
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/markdown",
            resumable=True,
        )
        is_editable = _execute_with_retry(
            self._check_editable(self.file_id)
        )
        if not is_editable:
            raise PermissionError("File is not editable (locked).")
        return _execute_with_retry(
            self._service.files()
            .update(
                fileId=self.file_id,
                body=file_metadata,
                media_body=media
            )
        )
    
    def _find_master_knowledge_graph(self) -> str:
        """Find the master knowledge graph file by name."""
        files = self._service.files().list(
            q=f"name='master_knowledge_graph.md' and '{self.folder_id}' in parents and trashed = false",
            fields="files(id, name, mimeType, modifiedTime)",
        ).execute()
        files = files.get("files", [])
        if not files:
            raise FileNotFoundError("Master knowledge graph file not found.")
        return files[0].get("id")

   
    def _check_editable(self, file_id: str) -> bool:
        """Raise if the file is currently locked or not editable."""
        meta = self.get_metadata(file_id)
        caps = meta.get("capabilities", {})
        if not caps.get("canEdit", False):
            logger.error(f"File '{meta.get('name', file_id)}' is not editable (locked).")
            return False
        return True

    # ------------------------------------------------------------------
    # Async wrappers (non-blocking for the MCP event-loop)
    # ------------------------------------------------------------------
    async def _async_check_editable(self, file_id: str) -> None:
        return await asyncio.to_thread(self.check_editable, file_id)

    async def async_find_master_knowledge_graph(
        self, name: str, **kwargs
    ) -> list[dict]:
        return await asyncio.to_thread(self.find_master_knowledge_graph, name, **kwargs)

    async def async_read_master_knowledge_graph(self, file_id: str) -> str:
        return await asyncio.to_thread(self.read_master_knowledge_graph, file_id)
    
    async def async_write_master_knowledge_graph(self, content: str) -> None:
        is_editable = await self._async_check_editable(self.file_id)
        if not is_editable:
            raise PermissionError("File is not editable (locked).")
        return await asyncio.to_thread(self.write_master_knowledge_graph, content)
