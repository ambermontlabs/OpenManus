"""
app/agent/sandbox_agent.py — LM Studio / local execution agent
===============================================================
`SandboxManus` has been updated to bypass Daytona entirely.

When `api_type = "lmstudio"` (or any non-Daytona configuration) is
detected, the agent uses the same local toolset as the standard `Manus`
agent:

  • PythonExecute  — run Python code locally
  • BrowserUseTool — control a local Chromium instance
  • StrReplaceEditor — read / edit local files
  • AskHuman        — prompt the user for input
  • Terminate       — signal task completion

The Daytona sandbox tools (SandboxShellTool, SandboxFilesTool, etc.) are
still imported so that existing code that references them does not break,
but they are NOT added to the agent's tool collection unless Daytona
credentials are explicitly configured.

This mirrors the OpenHands approach: the LLM backend (LM Studio) is
decoupled from the execution environment (local host).
"""

from typing import Dict, List, Optional

from pydantic import Field, model_validator

from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.daytona.sandbox import LocalSandbox, create_sandbox, delete_sandbox
from app.daytona.tool_base import SandboxToolsBase
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor

# Sandbox-specific tools are imported for compatibility but only used when
# Daytona credentials are present.
from app.tool.sandbox.sb_browser_tool import SandboxBrowserTool
from app.tool.sandbox.sb_files_tool import SandboxFilesTool
from app.tool.sandbox.sb_shell_tool import SandboxShellTool
from app.tool.sandbox.sb_vision_tool import SandboxVisionTool


def _daytona_configured() -> bool:
    """Return True only when a real Daytona API key has been provided."""
    try:
        settings = config.daytona
        return bool(
            settings
            and getattr(settings, "daytona_api_key", None)
            and settings.daytona_api_key.strip()
        )
    except Exception:
        return False


class SandboxManus(ToolCallAgent):
    """
    A versatile general-purpose agent that works with LM Studio (local) or
    Daytona (cloud) as the execution backend.

    When Daytona credentials are absent the agent automatically falls back
    to the local toolset, which requires no external services beyond a
    running LM Studio instance.
    """

    name: str = "SandboxManus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools. "
        "Runs locally with LM Studio when Daytona is not configured."
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # MCP clients for remote tool access
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # Default toolset — local tools only; Daytona tools added later if needed
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])
    browser_context_helper: Optional[BrowserContextHelper] = None

    # Track connected MCP servers
    connected_servers: Dict[str, str] = Field(default_factory=dict)
    _initialized: bool = False

    # Sandbox reference — only populated when Daytona is active
    sandbox: Optional[LocalSandbox] = Field(default=None, exclude=True)
    sandbox_link: Optional[Dict[str, Dict[str, str]]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def initialize_helper(self) -> "SandboxManus":
        """Initialize basic components synchronously."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "SandboxManus":
        """Factory method to create and properly initialize a SandboxManus instance."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        if _daytona_configured():
            await instance.initialize_sandbox_tools()
        else:
            logger.info(
                "[SandboxManus] Daytona not configured — running in local / "
                "LM Studio mode with local tools."
            )
        instance._initialized = True
        return instance

    # ------------------------------------------------------------------
    # Daytona sandbox initialisation (only called when credentials exist)
    # ------------------------------------------------------------------

    async def initialize_sandbox_tools(
        self,
        password: str = None,
    ) -> None:
        """
        Create a Daytona sandbox and register sandbox-specific tools.

        This method is only invoked when `_daytona_configured()` returns
        True.  In the LM Studio path it is never called.
        """
        if password is None:
            try:
                password = config.daytona.VNC_password
            except Exception:
                password = "123456"
        try:
            sandbox = create_sandbox(password=password)
            self.sandbox = sandbox

            vnc_link = sandbox.get_preview_link(6080)
            website_link = sandbox.get_preview_link(8080)
            vnc_url = vnc_link.url if hasattr(vnc_link, "url") else str(vnc_link)
            website_url = (
                website_link.url if hasattr(website_link, "url") else str(website_link)
            )

            actual_sandbox_id = sandbox.id if hasattr(sandbox, "id") else "local"
            if not self.sandbox_link:
                self.sandbox_link = {}
            self.sandbox_link[actual_sandbox_id] = {
                "vnc": vnc_url,
                "website": website_url,
            }
            logger.info(f"Sandbox VNC URL: {vnc_url}")
            logger.info(f"Sandbox Website URL: {website_url}")
            SandboxToolsBase._urls_printed = True

            sb_tools = [
                SandboxBrowserTool(sandbox),
                SandboxFilesTool(sandbox),
                SandboxShellTool(sandbox),
                SandboxVisionTool(sandbox),
            ]
            self.available_tools.add_tools(*sb_tools)

        except Exception as exc:
            logger.error(f"Error initializing sandbox tools: {exc}")
            raise

    # ------------------------------------------------------------------
    # MCP server management
    # ------------------------------------------------------------------

    async def initialize_mcp_servers(self) -> None:
        """Initialize connections to configured MCP servers."""
        for server_id, server_config in config.mcp_config.servers.items():
            try:
                if server_config.type == "sse":
                    if server_config.url:
                        await self.connect_mcp_server(server_config.url, server_id)
                        logger.info(
                            f"Connected to MCP server {server_id} at {server_config.url}"
                        )
                elif server_config.type == "stdio":
                    if server_config.command:
                        await self.connect_mcp_server(
                            server_config.command,
                            server_id,
                            use_stdio=True,
                            stdio_args=server_config.args,
                        )
                        logger.info(
                            f"Connected to MCP server {server_id} via {server_config.command}"
                        )
            except Exception as exc:
                logger.error(f"Failed to connect to MCP server {server_id}: {exc}")

    async def connect_mcp_server(
        self,
        server_url: str,
        server_id: str = "",
        use_stdio: bool = False,
        stdio_args: List[str] = None,
    ) -> None:
        """Connect to an MCP server and add its tools."""
        if use_stdio:
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
            self.connected_servers[server_id or server_url] = server_url
        else:
            await self.mcp_clients.connect_sse(server_url, server_id)
            self.connected_servers[server_id or server_url] = server_url

        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """Disconnect from an MCP server and remove its tools."""
        await self.mcp_clients.disconnect(server_id)
        if server_id:
            self.connected_servers.pop(server_id, None)
        else:
            self.connected_servers.clear()

        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        self.available_tools = ToolCollection(*base_tools)
        self.available_tools.add_tools(*self.mcp_clients.tools)

    # ------------------------------------------------------------------
    # Sandbox lifecycle
    # ------------------------------------------------------------------

    async def delete_sandbox(self, sandbox_id: str) -> None:
        """Delete a sandbox by ID (no-op in local mode)."""
        try:
            await delete_sandbox(sandbox_id)
            logger.info(f"Sandbox {sandbox_id} deleted / released")
            if self.sandbox_link and sandbox_id in self.sandbox_link:
                del self.sandbox_link[sandbox_id]
        except Exception as exc:
            logger.error(f"Error deleting sandbox {sandbox_id}: {exc}")
            raise

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def cleanup(self):
        """Clean up agent resources."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
        if self._initialized:
            await self.disconnect_mcp_server()
            if self.sandbox is not None:
                await self.delete_sandbox(
                    self.sandbox.id if hasattr(self.sandbox, "id") else "unknown"
                )
            self._initialized = False

    # ------------------------------------------------------------------
    # Think loop
    # ------------------------------------------------------------------

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        if not self._initialized:
            await self.initialize_mcp_servers()
            self._initialized = True

        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name in (BrowserUseTool().name, SandboxBrowserTool().name)
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )

        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result
