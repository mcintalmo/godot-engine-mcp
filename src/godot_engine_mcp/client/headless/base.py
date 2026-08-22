"""Base headless client with core process execution and path resolution."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.client.lsp_client import GodotLSPClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.common import EngineMode

logger = logging.getLogger(__name__)


class BaseHeadlessClient(GodotClient):
    """Base class for headless Godot client providing environment and process management."""

    def __init__(self, config: GodotConfig | None = None) -> None:
        self.config = config or GodotConfig.load()
        self.lsp = GodotLSPClient(self.config)

    @property
    def mode(self) -> EngineMode:
        return EngineMode.HEADLESS_CLI

    async def is_available(self) -> bool:
        """Check if Godot executable is available."""
        return bool(
            self.config.executable_path and os.path.exists(self.config.executable_path)
        )

    def _resolve_res_path(self, res_path: str) -> Path | None:
        """Translate 'res://path/to/file' into absolute filesystem Path."""
        project_root = self.config.project_path or self.config.discover_project_root()
        if not project_root:
            return None
        if res_path.startswith("res://"):
            rel = res_path[len("res://") :].lstrip("/\\")
            return Path(project_root) / rel
        return Path(res_path)

    async def _run_godot_command(
        self, args: list[str], timeout: float | None = None
    ) -> tuple[int, str, str]:
        """Execute Godot process asynchronously and return (returncode, stdout, stderr)."""
        if not self.config.executable_path:
            return 1, "", "Godot executable path not configured"

        cmd = [self.config.executable_path, "--headless"] + args
        eff_timeout = timeout or self.config.request_timeout

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=eff_timeout
            )
            return (
                proc.returncode or 0,
                stdout_b.decode(errors="replace"),
                stderr_b.decode(errors="replace"),
            )
        except TimeoutError:
            return -1, "", f"Godot command timed out after {eff_timeout}s"
        except (OSError, subprocess.SubprocessError) as e:
            return 1, "", str(e)
