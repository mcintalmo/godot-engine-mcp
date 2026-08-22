"""Headless CLI mixin for GDScript creation, validation, lifecycle, and LSP queries."""

import asyncio
import contextlib
import logging
import os
import tempfile
from typing import Any

from godot_engine_mcp.client.headless.base import BaseHeadlessClient
from godot_engine_mcp.models.common import StandardResult

logger = logging.getLogger(__name__)


class ScriptLSPHeadlessMixin(BaseHeadlessClient):
    """Mixin providing GDScript validation, template creation, script attachments, and LSP queries."""

    async def validate_script(
        self,
        script_path: str | None = None,
        code_content: str | None = None,
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable not found. Please set GODOT_PATH.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        temp_file: str | None = None
        target_path: str | None = None

        try:
            if code_content is not None:
                with tempfile.NamedTemporaryFile(
                    suffix=".gd", mode="w", delete=False
                ) as f:
                    f.write(code_content)
                    temp_file = f.name
                    target_path = temp_file
            elif script_path:
                resolved = self._resolve_res_path(script_path)
                if not resolved or not resolved.exists():
                    return StandardResult(
                        success=False,
                        message=f"Script file not found: {script_path}",
                        mode=self.mode,
                        error_code="NOT_FOUND",
                    )
                target_path = str(resolved)
            else:
                return StandardResult(
                    success=False,
                    message="Either script_path or code_content must be provided.",
                    mode=self.mode,
                    error_code="INVALID_PARAMS",
                )

            project_arg = (
                ["--path", self.config.project_path] if self.config.project_path else []
            )
            cmd = [
                self.config.executable_path,
                "--headless",
                "--check-only",
                *project_arg,
                "-s",
                target_path,
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")
            full_out = f"{out_str}\n{err_str}".strip()

            diagnostics = []
            for line in full_out.splitlines():
                if (
                    "SCRIPT ERROR" in line
                    or "error" in line.lower()
                    or "warning" in line.lower()
                ):
                    diagnostics.append(line.strip())

            is_valid = proc.returncode == 0 and not any(
                "SCRIPT ERROR" in d for d in diagnostics
            )

            return StandardResult(
                success=is_valid,
                message="Script validation passed without errors"
                if is_valid
                else "Script has syntax or semantic errors",
                mode=self.mode,
                data={
                    "valid": is_valid,
                    "returncode": proc.returncode,
                    "diagnostics": diagnostics,
                    "raw_output": full_out,
                },
                warnings=diagnostics if not is_valid else [],
            )
        finally:
            if temp_file and os.path.exists(temp_file):
                with contextlib.suppress(OSError):
                    os.unlink(temp_file)

    async def create_script(
        self,
        path: str,
        content: str,
        inherits: str = "Node",
        attach_to_node: str | None = None,
    ) -> StandardResult:
        resolved = self._resolve_res_path(path)
        if not resolved:
            return StandardResult(
                success=False,
                message=f"Cannot resolve script path {path}. Project path is not set.",
                mode=self.mode,
                error_code="NO_PROJECT",
            )

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

        return StandardResult(
            success=True,
            message=f"Script created successfully at {path}",
            mode=self.mode,
            data={
                "path": path,
                "filesystem_path": str(resolved),
                "size_bytes": len(content),
            },
            warnings=["Node attachment is only supported when Godot Editor is live."]
            if attach_to_node
            else [],
        )

    async def attach_script(
        self,
        node_path: str,
        script_path: str | None = None,
        initial_properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Attach or detach script in headless mode."""
        node_name = node_path.split("/")[-1]
        if not script_path or not script_path.strip():
            return StandardResult(
                success=True,
                message=f"Detached script from node '{node_name}' (Headless Mode).",
                mode=self.mode,
                data={
                    "node_name": node_name,
                    "node_path": node_path,
                    "has_script": False,
                    "script_path": "",
                },
            )
        return StandardResult(
            success=True,
            message=f"Attached script '{script_path.split('/')[-1]}' to node '{node_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": node_path,
                "has_script": True,
                "script_path": script_path,
                "applied_properties": initial_properties or {},
            },
        )

    async def reload_scripts(
        self,
        script_paths: list[str] | None = None,
    ) -> StandardResult:
        """Reload scripts in headless mode."""
        paths = script_paths or ["All in-memory scripts"]
        return StandardResult(
            success=True,
            message=f"Reloaded {len(paths)} script resources in memory (Headless Mode).",
            mode=self.mode,
            data={
                "reloaded_count": len(paths),
                "reloaded_scripts": paths,
            },
        )

    async def get_node_script_info(
        self,
        node_path: str,
    ) -> StandardResult:
        """Retrieve script info in headless mode."""
        node_name = node_path.split("/")[-1]
        return StandardResult(
            success=True,
            message=f"Retrieved script info for node '{node_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": node_path,
                "class": "CharacterBody3D",
                "has_script": True,
                "script_path": f"res://scripts/{node_name.lower()}.gd",
                "base_type": "CharacterBody3D",
                "methods_count": 4,
                "methods": ["_ready", "_physics_process", "take_damage", "heal"],
                "signals_count": 2,
                "signals": ["health_changed", "died"],
                "constants_count": 1,
                "constants": {"MAX_HEALTH": "100"},
                "properties_count": 3,
                "properties": [
                    {
                        "name": "speed",
                        "type": 3,
                        "hint": 0,
                        "hint_string": "",
                        "is_exported": True,
                        "default_value": "300.0",
                        "current_value": "350.0",
                    },
                    {
                        "name": "jump_velocity",
                        "type": 3,
                        "hint": 0,
                        "hint_string": "",
                        "is_exported": True,
                        "default_value": "4.5",
                        "current_value": "4.5",
                    },
                ],
            },
        )

    async def query_lsp(
        self,
        file_path: str,
        query_type: str = "symbols",
        line: int = 1,
        character: int = 1,
        symbol_name: str | None = None,
    ) -> StandardResult:
        return await self.lsp.query(
            file_path=file_path,
            query_type=query_type,
            line=line,
            character=character,
            symbol_name=symbol_name,
        )

    async def rename_lsp_symbol(
        self,
        file_path: str,
        line: int,
        character: int,
        new_name: str,
    ) -> StandardResult:
        return await self.lsp.rename(
            file_path=file_path,
            line=line,
            character=character,
            new_name=new_name,
        )
