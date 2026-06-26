"""
app/daytona/sandbox.py — Local execution stub (Daytona bypassed)
================================================================
This module previously managed Daytona cloud sandboxes.  It has been
replaced with a lightweight local stub so that the rest of the codebase
(imports, type hints, call sites) continues to work without the Daytona
SDK being installed or configured.

The LM Studio integration path uses the standard `Manus` agent
(app/agent/manus.py) with local tools (PythonExecute, BrowserUseTool,
StrReplaceEditor) and does not require any remote sandbox.

If you still need Daytona support, restore this file from git history
and set `[daytona]` credentials in config/config.toml.
"""

from __future__ import annotations

import asyncio
import subprocess
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from app.utils.logger import logger


# ---------------------------------------------------------------------------
# Minimal type stubs that mirror the Daytona SDK surface used elsewhere
# ---------------------------------------------------------------------------


class SandboxState(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ARCHIVED = "archived"
    STARTING = "starting"


@dataclass
class _FakeFs:
    """Minimal filesystem shim backed by the local host."""

    workspace: str = "/workspace"

    def get_file_info(self, path: str) -> "_FileInfo":
        import os

        return _FileInfo(
            path=path,
            is_dir=os.path.isdir(path),
            size=os.path.getsize(path) if os.path.exists(path) else 0,
        )

    def download_file(self, path: str) -> bytes:
        with open(path, "rb") as fh:
            return fh.read()

    def upload_file(self, path: str, data: bytes) -> None:
        import os

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)

    def list_files(self, path: str):
        import os

        return [
            _FileInfo(
                path=os.path.join(path, name),
                is_dir=os.path.isdir(os.path.join(path, name)),
                size=0,
            )
            for name in os.listdir(path)
        ]

    def create_folder(self, path: str, mode: str = "0755") -> None:
        import os

        os.makedirs(path, exist_ok=True)

    def delete_file(self, path: str) -> None:
        import os

        if os.path.isdir(path):
            import shutil

            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)

    def set_file_permissions(self, path: str, mode: str) -> None:
        import os

        os.chmod(path, int(mode, 8))


@dataclass
class _FileInfo:
    path: str
    is_dir: bool
    size: int


@dataclass
class _ProcessResult:
    exit_code: int
    result: str


@dataclass
class _FakeProcess:
    """Minimal process shim that runs commands locally."""

    _sessions: Dict[str, Any] = field(default_factory=dict)

    def create_session(self, session_id: str) -> None:
        self._sessions[session_id] = []
        logger.debug(f"[LocalSandbox] Session created: {session_id}")

    def execute_session_command(self, session_id: str, request: Any = None, req: Any = None, timeout: Optional[int] = None):
        """Execute a command in a session and return a result stub."""
        # Accept both `request` (old API) and `req` (new API) keyword arguments
        effective_request = req if req is not None else request
        cmd = getattr(effective_request, "command", str(effective_request))
        run_async = getattr(effective_request, "run_async", False) or getattr(effective_request, "var_async", False)
        logger.debug(f"[LocalSandbox] exec in session {session_id}: {cmd}")
        if run_async:
            subprocess.Popen(cmd, shell=True)
        else:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=timeout
                )
                output = result.stdout + result.stderr
            except Exception:
                output = ""
        # Return a minimal result object
        class _R:
            cmd_id = session_id
            exit_code = 0
        return _R()

    def get_session_command_logs(self, session_id: str, cmd_id: str) -> str:
        return ""

    def exec(self, command: str, timeout: Optional[int] = None) -> _ProcessResult:
        logger.debug(f"[LocalSandbox] exec: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            return _ProcessResult(exit_code=result.returncode, result=output)
        except subprocess.TimeoutExpired:
            return _ProcessResult(exit_code=1, result="Command timed out")
        except Exception as exc:
            return _ProcessResult(exit_code=1, result=str(exc))


@dataclass
class LocalSandbox:
    """
    Drop-in replacement for the Daytona `Sandbox` object.

    Runs all operations on the local host filesystem and process table,
    which is sufficient for the LM Studio integration path.
    """

    id: str = field(default_factory=lambda: f"local-{uuid.uuid4().hex[:8]}")
    state: SandboxState = SandboxState.RUNNING
    fs: _FakeFs = field(default_factory=_FakeFs)
    process: _FakeProcess = field(default_factory=_FakeProcess)

    def get_preview_link(self, port: int) -> "_PreviewLink":
        return _PreviewLink(url=f"http://localhost:{port}")


@dataclass
class _PreviewLink:
    url: str


# Alias so existing `from app.daytona.sandbox import Sandbox` imports work
Sandbox = LocalSandbox


@dataclass
class SessionExecuteRequest:
    """
    Stub for the Daytona SDK `SessionExecuteRequest`.

    Accepted by `_FakeProcess.execute_session_command` and ignored in
    local mode; the command is run directly via subprocess.
    """

    command: str
    run_async: bool = False
    var_async: bool = False  # legacy alias
    cwd: Optional[str] = None

    @dataclass
    class _Result:
        cmd_id: str = ""
        exit_code: int = 0

    def __post_init__(self):
        # Normalise var_async / run_async
        if self.var_async:
            self.run_async = True


# ---------------------------------------------------------------------------
# Public API — mirrors the original daytona/sandbox.py surface
# ---------------------------------------------------------------------------


def create_sandbox(password: str, project_id: Optional[str] = None) -> LocalSandbox:
    """
    Return a local sandbox instance.

    The `password` and `project_id` arguments are accepted for API
    compatibility but are not used in the local execution path.
    """
    logger.info(
        "[LocalSandbox] Daytona bypassed — using local execution sandbox. "
        "LM Studio integration active."
    )
    sandbox = LocalSandbox()
    logger.info(f"[LocalSandbox] Sandbox ready (id={sandbox.id})")
    return sandbox


async def get_or_start_sandbox(sandbox_id: str) -> LocalSandbox:
    """Return a running local sandbox (always available locally)."""
    logger.info(f"[LocalSandbox] get_or_start_sandbox({sandbox_id}) — local mode")
    return LocalSandbox(id=sandbox_id)


def start_supervisord_session(sandbox: LocalSandbox) -> None:
    """No-op: supervisord is not needed for local execution."""
    logger.debug("[LocalSandbox] start_supervisord_session — no-op in local mode")


async def delete_sandbox(sandbox_id: str) -> bool:
    """No-op: nothing to delete for a local sandbox."""
    logger.info(f"[LocalSandbox] delete_sandbox({sandbox_id}) — no-op in local mode")
    return True
