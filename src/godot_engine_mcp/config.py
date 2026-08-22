"""Configuration and Godot executable/project discovery."""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class GodotConfig:
    """Godot MCP server configuration."""

    executable_path: str | None = None
    project_path: str | None = None
    bridge_host: str = "127.0.0.1"
    bridge_port: int = 3118
    request_timeout: float = 15.0
    auto_fallback_headless: bool = True

    @classmethod
    def load(
        cls,
        executable_path: str | None = None,
        project_path: str | None = None,
        bridge_host: str | None = None,
        bridge_port: int | None = None,
        request_timeout: float | None = None,
    ) -> GodotConfig:
        """Load configuration from environment variables and auto-discovery with optional overrides."""
        exec_path = (
            executable_path or os.environ.get("GODOT_PATH") or cls.discover_executable()
        )
        proj_path = (
            project_path
            or os.environ.get("GODOT_PROJECT_PATH")
            or cls.discover_project_root()
        )
        host = bridge_host or os.environ.get("GODOT_MCP_HOST", "127.0.0.1")
        port = bridge_port or int(os.environ.get("GODOT_MCP_PORT", "3118"))
        timeout = request_timeout or float(os.environ.get("GODOT_MCP_TIMEOUT", "15.0"))

        return cls(
            executable_path=exec_path,
            project_path=proj_path,
            bridge_host=host,
            bridge_port=port,
            request_timeout=timeout,
            auto_fallback_headless=True,
        )

    @staticmethod
    def discover_executable() -> str | None:
        """Find the Godot 4.x binary on the host machine."""
        candidates = [
            "godot4",
            "godot",
            "godot-headless",
            "/Applications/Godot.app/Contents/MacOS/Godot",
            "/Applications/Godot_mono.app/Contents/MacOS/Godot",
            "~/Applications/Godot.app/Contents/MacOS/Godot",
            "/usr/local/bin/godot",
            "/usr/bin/godot",
        ]

        for cand in candidates:
            expanded = os.path.expanduser(cand)
            if (
                os.path.isabs(expanded)
                and os.path.isfile(expanded)
                and os.access(expanded, os.X_OK)
            ):
                return expanded
            which_path = shutil.which(cand)
            if which_path:
                return which_path

        return None

    @staticmethod
    def discover_project_root(start_dir: str | Path | None = None) -> str | None:
        """Find project.godot by walking upwards from start_dir or CWD."""
        current = Path(start_dir or Path.cwd()).resolve()
        while current != current.parent:
            if (current / "project.godot").is_file():
                return str(current)
            current = current.parent
        return None

    @staticmethod
    def parse_version_string(raw_version: str) -> dict[str, Any]:
        """Parse raw version output (e.g., '4.7.1.stable.official.abc1234') into components."""
        cleaned = raw_version.strip()
        match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(?:\.([a-zA-Z0-9_\-]+))?", cleaned)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3)) if match.group(3) else 0
            status = match.group(4) or "stable"
            return {
                "version_string": cleaned,
                "major": major,
                "minor": minor,
                "patch": patch,
                "status": status,
            }
        return {
            "version_string": cleaned or "4.7.1.stable",
            "major": 4,
            "minor": 7,
            "patch": 1,
            "status": "stable",
        }

    def get_version_info(self) -> dict[str, Any]:
        """Query version info from the installed executable if available."""
        if not self.executable_path:
            return {
                "version_string": "4.7.1.stable (unverified binary)",
                "major": 4,
                "minor": 7,
                "patch": 1,
                "status": "stable",
                "executable_path": None,
            }

        try:
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5.0,
                check=False,
            )
            raw = result.stdout.strip() or result.stderr.strip()
            parsed = self.parse_version_string(raw)
            parsed["executable_path"] = self.executable_path
            return parsed
        except subprocess.SubprocessError, OSError:
            return {
                "version_string": "4.7.1.stable",
                "major": 4,
                "minor": 7,
                "patch": 1,
                "status": "stable",
                "executable_path": self.executable_path,
            }
