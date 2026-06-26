"""
app/daytona/tool_base.py — Local execution stub (Daytona bypassed)
==================================================================
This module previously imported the Daytona SDK and provided
`SandboxToolsBase`, a Pydantic base class that wired tools to a remote
Daytona sandbox.

It has been rewritten to use the local `LocalSandbox` shim so that all
existing sandbox tool subclasses (SandboxShellTool, SandboxFilesTool,
SandboxBrowserTool, SandboxVisionTool) continue to import and instantiate
without the Daytona SDK being present.

The LM Studio integration path does NOT use these sandbox tools at all —
it uses the standard `Manus` agent with local tools.  This stub exists
purely to keep the import graph intact and avoid ImportError when
`sandbox_agent.py` or the sandbox tool modules are imported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field

from app.daytona.sandbox import LocalSandbox, SandboxState, create_sandbox
from app.tool.base import BaseTool
from app.utils.files_utils import clean_path
from app.utils.logger import logger

# Re-export Sandbox so `from app.daytona.tool_base import Sandbox` works
Sandbox = LocalSandbox


# ---------------------------------------------------------------------------
# ThreadMessage — kept for API compatibility with vision / browser tools
# ---------------------------------------------------------------------------


@dataclass
class ThreadMessage:
    """Represents a message to be added to a thread."""

    type: str
    content: Dict[str, Any]
    is_llm_message: bool = False
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = field(
        default_factory=lambda: datetime.now().timestamp()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content": self.content,
            "is_llm_message": self.is_llm_message,
            "metadata": self.metadata or {},
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# SandboxToolsBase — local execution replacement
# ---------------------------------------------------------------------------


class SandboxToolsBase(BaseTool):
    """
    Base class for sandbox tools.

    In the LM Studio / local execution path this class manages a
    `LocalSandbox` instance instead of a remote Daytona sandbox.
    All Daytona SDK calls have been removed; the public API surface
    (``_ensure_sandbox``, ``sandbox``, ``sandbox_id``, ``clean_path``)
    is preserved so subclasses compile without modification.
    """

    # Class variable to track if sandbox URLs have been printed
    _urls_printed: ClassVar[bool] = False

    project_id: Optional[str] = None
    _sandbox: Optional[LocalSandbox] = None
    _sandbox_id: Optional[str] = None
    _sandbox_pass: Optional[str] = None
    workspace_path: str = Field(default="/workspace", exclude=True)
    _sessions: dict = {}

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    async def _ensure_sandbox(self) -> LocalSandbox:
        """Ensure we have a valid local sandbox instance."""
        if self._sandbox is None:
            try:
                self._sandbox = create_sandbox(password="local")
                if not SandboxToolsBase._urls_printed:
                    logger.info(
                        "[LocalSandbox] Running in local mode — "
                        "no VNC/website preview URLs available."
                    )
                    SandboxToolsBase._urls_printed = True
            except Exception as exc:
                logger.error(f"[LocalSandbox] Error creating sandbox: {exc}")
                raise
        else:
            # Local sandbox is always running; nothing to restart
            if self._sandbox.state in (SandboxState.ARCHIVED, SandboxState.STOPPED):
                logger.info("[LocalSandbox] Sandbox marked stopped — resetting state")
                self._sandbox.state = SandboxState.RUNNING
        return self._sandbox

    @property
    def sandbox(self) -> LocalSandbox:
        """Get the sandbox instance, ensuring it exists."""
        if self._sandbox is None:
            raise RuntimeError(
                "Sandbox not initialized. Call _ensure_sandbox() first."
            )
        return self._sandbox

    @property
    def sandbox_id(self) -> str:
        """Get the sandbox ID."""
        if self._sandbox is None:
            raise RuntimeError(
                "Sandbox ID not initialized. Call _ensure_sandbox() first."
            )
        return self._sandbox.id

    def clean_path(self, path: str) -> str:
        """Clean and normalize a path to be relative to /workspace."""
        cleaned = clean_path(path, self.workspace_path)
        logger.debug(f"[LocalSandbox] clean_path: {path} -> {cleaned}")
        return cleaned
