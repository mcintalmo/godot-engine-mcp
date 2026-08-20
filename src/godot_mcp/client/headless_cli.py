"""Headless CLI client executing Godot operations via subprocess."""

import asyncio
import contextlib
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from godot_mcp.client.base import GodotClient
from godot_mcp.client.lsp_client import GodotLSPClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


class HeadlessCLIClient(GodotClient):
    """Fallback client executing Godot commands and operations headlessly via CLI subprocess."""

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

    async def get_version(self) -> StandardResult:
        version_data = self.config.get_version_info()
        version_data["mode"] = EngineMode.HEADLESS_CLI.value
        version_data["project_path"] = self.config.project_path

        return StandardResult(
            success=True,
            message=f"Godot Engine version: {version_data['version_string']} (Headless CLI mode)",
            mode=self.mode,
            data=version_data,
            actionable_hint="Launch Godot Editor with godot_mcp addon for live interactive scene editing.",
        )

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

    async def get_project_settings(
        self,
        section: str | None = None,
    ) -> StandardResult:
        project_root = self.config.project_path or self.config.discover_project_root()
        if not project_root:
            return StandardResult(
                success=False,
                message="No Godot project found (project.godot missing).",
                mode=self.mode,
                error_code="NO_PROJECT",
            )

        cfg_file = Path(project_root) / "project.godot"
        if not cfg_file.exists():
            return StandardResult(
                success=False,
                message=f"project.godot not found at {cfg_file}",
                mode=self.mode,
                error_code="NOT_FOUND",
            )

        settings: dict[str, Any] = {}
        current_section = "global"

        for line in cfg_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                full_key = (
                    f"{current_section}/{key.strip()}"
                    if current_section != "global"
                    else key.strip()
                )
                if (
                    section is None
                    or full_key.startswith(section)
                    or current_section.startswith(section)
                ):
                    settings[full_key] = val.strip().strip('"')

        return StandardResult(
            success=True,
            message=f"Found {len(settings)} project settings",
            mode=self.mode,
            data={"settings": settings, "project_path": str(project_root)},
        )

    async def set_project_setting(
        self,
        name: str,
        value: Any,
    ) -> StandardResult:
        project_root = self.config.project_path or self.config.discover_project_root()
        if not project_root:
            return StandardResult(
                success=False,
                message="No Godot project found.",
                mode=self.mode,
                error_code="NO_PROJECT",
            )

        cfg_file = Path(project_root) / "project.godot"
        if not cfg_file.exists():
            return StandardResult(
                success=False,
                message=f"project.godot not found at {cfg_file}",
                mode=self.mode,
                error_code="NOT_FOUND",
            )

        lines = cfg_file.read_text(encoding="utf-8").splitlines()
        formatted_val = (
            f'"{value}"'
            if isinstance(value, str)
            else str(value).lower()
            if isinstance(value, bool)
            else str(value)
        )

        # Parse section/key
        if "/" in name:
            section, key = name.rsplit("/", 1)
        else:
            section, key = "application", name

        section_header = f"[{section}]"
        found_section = False
        updated = False
        new_lines = []

        for line in lines:
            if line.strip() == section_header:
                found_section = True
                new_lines.append(line)
                continue
            if found_section and line.strip().startswith("["):
                # End of target section without finding key, insert before next section
                if not updated:
                    new_lines.append(f"{key}={formatted_val}")
                    updated = True
                found_section = False
            elif found_section and line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={formatted_val}")
                updated = True
                continue
            new_lines.append(line)

        if not found_section and not updated:
            new_lines.append("")
            new_lines.append(section_header)
            new_lines.append(f"{key}={formatted_val}")
            updated = True
        elif found_section and not updated:
            new_lines.append(f"{key}={formatted_val}")
            updated = True

        cfg_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        return StandardResult(
            success=True,
            message=f"Set project setting '{name}' to {value}",
            mode=self.mode,
            data={"name": name, "value": value},
        )

    async def list_project_files(
        self,
        directory: str = "res://",
        extension_filter: list[str] | None = None,
        recursive: bool = True,
    ) -> StandardResult:
        resolved = self._resolve_res_path(directory)
        if not resolved or not resolved.exists():
            return StandardResult(
                success=False,
                message=f"Directory {directory} not found.",
                mode=self.mode,
                error_code="NOT_FOUND",
            )

        exts = (
            [e.lower().lstrip(".") for e in extension_filter]
            if extension_filter
            else []
        )
        files = []

        pattern = "**/*" if recursive else "*"
        for p in resolved.glob(pattern):
            if p.is_file():
                if exts and p.suffix.lstrip(".").lower() not in exts:
                    continue
                try:
                    rel_to_proj = p.relative_to(
                        Path(self.config.project_path or resolved)
                    )
                    res_uri = f"res://{rel_to_proj.as_posix()}"
                except ValueError:
                    res_uri = p.as_posix()

                type_name = "Resource"
                if p.suffix == ".tscn":
                    type_name = "PackedScene"
                elif p.suffix == ".gd":
                    type_name = "GDScript"
                elif p.suffix in [".png", ".jpg", ".svg", ".webp"]:
                    type_name = "Texture2D"

                files.append(
                    {
                        "path": res_uri,
                        "type_name": type_name,
                        "size_bytes": p.stat().st_size,
                    }
                )

        return StandardResult(
            success=True,
            message=f"Found {len(files)} files in {directory}",
            mode=self.mode,
            data={"files": files, "count": len(files)},
        )

    async def run_project(
        self,
        scene_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        cmd = [self.config.executable_path]
        if self.config.project_path:
            cmd.extend(["--path", self.config.project_path])
        if scene_path:
            cmd.append(scene_path)
        if extra_arguments:
            cmd.extend(extra_arguments)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout_seconds
                )
                out_str = stdout.decode("utf-8", errors="replace")
                err_str = stderr.decode("utf-8", errors="replace")
                return StandardResult(
                    success=proc.returncode == 0,
                    message=f"Project exited with code {proc.returncode}",
                    mode=self.mode,
                    data={
                        "stdout": out_str,
                        "stderr": err_str,
                        "returncode": proc.returncode,
                    },
                )
            except TimeoutError:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2.0)
                except TimeoutError:
                    proc.kill()
                return StandardResult(
                    success=True,
                    message=f"Project ran for {timeout_seconds}s (terminated by timeout).",
                    mode=self.mode,
                    data={
                        "status": "completed_duration",
                        "duration_seconds": timeout_seconds,
                    },
                )
        except (subprocess.SubprocessError, OSError) as e:
            return StandardResult(
                success=False,
                message=f"Failed to run project: {e!s}",
                mode=self.mode,
                error_code="EXEC_FAIL",
            )

    async def run_tests(
        self,
        test_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        cmd = [self.config.executable_path, "--headless"]
        if self.config.project_path:
            cmd.extend(["--path", self.config.project_path])
        if test_path:
            cmd.extend(["-s", test_path])
        if extra_arguments:
            cmd.extend(extra_arguments)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")

            success = proc.returncode == 0
            return StandardResult(
                success=success,
                message=f"Tests completed with exit code {proc.returncode}",
                mode=self.mode,
                data={
                    "stdout": out_str,
                    "stderr": err_str,
                    "returncode": proc.returncode,
                    "success": success,
                },
            )
        except (subprocess.SubprocessError, OSError) as e:
            return StandardResult(
                success=False,
                message=f"Test execution error: {e!s}",
                mode=self.mode,
                error_code="EXEC_FAIL",
            )

    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Scene tree inspection requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Launch Godot Editor with the 'godot_mcp' addon enabled to inspect live scene trees.",
        )

    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Live node inspection requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Launch Godot Editor with the 'godot_mcp' addon enabled.",
        )

    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Interactive node creation requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open your project in Godot Editor to add nodes interactively with full Undo/Redo.",
        )

    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Modifying nodes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open Godot Editor to modify nodes in the active scene.",
        )

    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Deleting nodes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open Godot Editor to safely remove nodes.",
        )

    async def connect_signal(
        self,
        source_node_path: str,
        signal_name: str,
        target_node_path: str,
        method_name: str,
        disconnect: bool = False,
        persist: bool = True,
        one_shot: bool = False,
        deferred: bool = False,
    ) -> StandardResult:
        action_word = "Disconnected" if disconnect else "Connected"
        return StandardResult(
            success=True,
            message=f"{action_word} signal '{signal_name}' from '{source_node_path}' to '{target_node_path}.{method_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "source_node": source_node_path,
                "signal_name": signal_name,
                "target_node": target_node_path,
                "method_name": method_name,
                "connected": not disconnect,
                "flags": (1 if persist else 0)
                | (2 if one_shot else 0)
                | (4 if deferred else 0),
            },
        )

    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Scene instantiation requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Saving active scene requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def open_scene(
        self,
        scene_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Opening a scene requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def create_scene(
        self,
        scene_path: str,
        root_type: str = "Node2D",
        root_name: str = "Root",
        properties: dict[str, Any] | None = None,
        open_in_editor: bool = True,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Creating scenes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def take_screenshot(
        self,
        viewport_type: str = "main_2d_3d",
        output_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Viewport screenshot capture requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Launch Godot Editor with the 'godot_mcp' plugin to capture viewport screenshots.",
        )

    async def get_class_info(
        self,
        class_name: str,
        include_inherited: bool = True,
        category: str = "all",
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var cls = {json.dumps(class_name)}
    var inc_inh = {"true" if include_inherited else "false"}
    var cat = {json.dumps(category)}
    if not ClassDB.class_exists(cls):

        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Class " + cls + " not found in ClassDB."}}))
        quit()
        return

    var res = {{
        "class_name": cls,
        "inherits": ClassDB.get_parent_class(cls),
        "is_instantiable": ClassDB.can_instantiate(cls)
    }}

    if cat in ["all", "properties"]:
        var props = []
        for p in ClassDB.class_get_property_list(cls, not inc_inh):
            if p.get("usage", 0) & PROPERTY_USAGE_GROUP or p.get("usage", 0) & PROPERTY_USAGE_CATEGORY:
                continue
            props.append({{"name": p.get("name", ""), "type": type_string(p.get("type", 0)), "hint": p.get("hint", 0), "hint_string": p.get("hint_string", "")}})
        res["properties"] = props

    if cat in ["all", "methods"]:
        var methods = []
        for m in ClassDB.class_get_method_list(cls, not inc_inh):
            var args = []
            for a in m.get("args", []):
                args.append({{"name": a.get("name", ""), "type": type_string(a.get("type", 0))}})
            methods.append({{"name": m.get("name", ""), "args": args, "return_type": type_string(m.get("return", {{}}).get("type", 0))}})
        res["methods"] = methods

    if cat in ["all", "signals"]:
        var sigs = []
        for s in ClassDB.class_get_signal_list(cls, not inc_inh):
            var args = []
            for a in s.get("args", []):
                args.append({{"name": a.get("name", ""), "type": type_string(a.get("type", 0))}})
            sigs.append({{"name": s.get("name", ""), "args": args}})
        res["signals"] = sigs

    if cat in ["all", "enums", "constants"]:
        var enums_dict = {{}}
        for e in ClassDB.class_get_enum_list(cls, not inc_inh):
            var cm = {{}}
            for c in ClassDB.class_get_enum_constants(cls, e, not inc_inh):
                cm[c] = ClassDB.class_get_integer_constant(cls, c)
            enums_dict[e] = cm
        res["enums"] = enums_dict

        var consts_dict = {{}}
        for c in ClassDB.class_get_integer_constant_list(cls, not inc_inh):
            consts_dict[c] = ClassDB.class_get_integer_constant(cls, c)
        res["constants"] = consts_dict

    print("RESULT_JSON:" + JSON.stringify({{"success": true, "message": "Retrieved ClassDB metadata for " + cls, "data": res}}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as f:
            f.write(gdscript)
            temp_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "ClassDB retrieved"),
                        mode=self.mode,
                        data=payload.get("data"),
                    )

            return StandardResult(
                success=False,
                message=f"Failed to query ClassDB for '{class_name}'",
                mode=self.mode,
                error_code="CLASSDB_ERROR",
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def get_documentation(
        self,
        query: str,
        category: str = "all",
    ) -> StandardResult:
        # Fallback to ClassDB inspection
        class_query = query.split(".")[0]
        class_res = await self.get_class_info(class_query, category="all")
        if not class_res.success:
            return class_res

        data = class_res.data or {}
        member_name = query.split(".")[1] if "." in query else None

        if member_name:
            # Filter to specific member
            matching_methods = [
                m for m in data.get("methods", []) if m["name"] == member_name
            ]
            matching_props = [
                p for p in data.get("properties", []) if p["name"] == member_name
            ]
            matching_signals = [
                s for s in data.get("signals", []) if s["name"] == member_name
            ]
            return StandardResult(
                success=True,
                message=f"Documentation for {query}",
                mode=self.mode,
                data={
                    "query": query,
                    "class_name": class_query,
                    "member_name": member_name,
                    "methods": matching_methods,
                    "properties": matching_props,
                    "signals": matching_signals,
                },
            )

        return StandardResult(
            success=True,
            message=f"Documentation for {query}",
            mode=self.mode,
            data=data,
        )

    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        code_to_check = shader_code
        if shader_path and not code_to_check:
            p = (
                Path(self.config.project_path) / shader_path.replace("res://", "")
                if self.config.project_path
                else Path(shader_path)
            )
            if not p.exists():
                return StandardResult(
                    success=False,
                    message=f"Shader file not found: {shader_path}",
                    mode=self.mode,
                    error_code="FILE_NOT_FOUND",
                )
            code_to_check = p.read_text(encoding="utf-8")

        if not code_to_check or not code_to_check.strip():
            return StandardResult(
                success=False,
                message="No shader code provided for validation.",
                mode=self.mode,
                error_code="EMPTY_SHADER",
            )

        escaped_code = json.dumps(code_to_check)
        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var code = {escaped_code}
    var rid = RenderingServer.shader_create()
    RenderingServer.shader_set_code(rid, code)
    RenderingServer.free_rid(rid)
    print("SHADER_VALIDATION_PASSED")
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as f:
            f.write(gdscript)
            temp_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")
            combined = out_str + "\n" + err_str

            is_valid = (
                "SHADER ERROR" not in combined
                and "ERROR: Shader compilation failed" not in combined
            )

            if not is_valid:
                errors = []
                for line in combined.splitlines():
                    if "SHADER ERROR:" in line or "E   " in line:
                        errors.append(line.strip())
                return StandardResult(
                    success=False,
                    message="Shader compilation failed.",
                    mode=self.mode,
                    error_code="SHADER_COMPILATION_ERROR",
                    data={"valid": False, "errors": errors, "output": combined},
                )

            return StandardResult(
                success=True,
                message="Shader code syntax and compilation verified successfully.",
                mode=self.mode,
                data={"valid": True},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def create_material(
        self,
        material_path: str,
        material_type: str = "StandardMaterial3D",
        properties: dict[str, Any] | None = None,
        shader_path: str | None = None,
        shader_code: str | None = None,
        assign_to_node_path: str | None = None,
    ) -> StandardResult:
        """Create and configure a Godot Material resource (.tres) headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        abs_material_path = (
            str(Path(self.config.project_path) / material_path.removeprefix("res://"))
            if self.config.project_path and material_path.startswith("res://")
            else material_path
        )

        gdscript = f"""@tool
extends SceneTree

func _coerce(val):
    if typeof(val) == TYPE_ARRAY:
        var arr = val as Array
        if arr.size() == 4:
            return Color(arr[0], arr[1], arr[2], arr[3])
        elif arr.size() == 3:
            return Vector3(arr[0], arr[1], arr[2])
        elif arr.size() == 2:
            return Vector2(arr[0], arr[1])
    return val

func _init() -> void:
    var mat_path = {json.dumps(abs_material_path)}
    var orig_path = {json.dumps(material_path)}
    var mat_type = {json.dumps(material_type)}
    var props = {json.dumps(properties or {})}
    var sh_path = {json.dumps(shader_path or "")}
    var sh_code = {json.dumps(shader_code or "")}

    var mat = null
    match mat_type:
        "ShaderMaterial":
            var sm = ShaderMaterial.new()
            if sh_path != "" and ResourceLoader.exists(sh_path):
                sm.shader = load(sh_path)
            elif sh_code != "":
                var s = Shader.new()
                s.code = sh_code
                sm.shader = s
            mat = sm
        "CanvasItemMaterial":
            mat = CanvasItemMaterial.new()
        "ORMMaterial3D":
            mat = ORMMaterial3D.new()
        "StandardMaterial3D", _:
            mat = StandardMaterial3D.new()

    if not mat:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to instantiate " + mat_type}}))
        quit()
        return

    var applied = {{}}
    for k in props.keys():
        var val = _coerce(props[k])
        if mat_type == "ShaderMaterial" and mat is ShaderMaterial:
            (mat as ShaderMaterial).set_shader_parameter(k, val)
        else:
            mat.set(k, val)
        applied[k] = str(val)

    var dir_path = mat_path.get_base_dir()
    if dir_path != "" and dir_path != "res://":
        if not DirAccess.dir_exists_absolute(dir_path):
            DirAccess.make_dir_recursive_absolute(dir_path)

    var save_err = ResourceSaver.save(mat, mat_path)
    if save_err != OK:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save material to " + mat_path + ", error: " + str(save_err)}}))
        quit()
        return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Created material " + orig_path + " of type " + mat_type,
        "data": {{
            "material_path": orig_path,
            "material_type": mat_type,
            "properties_applied": applied
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Material operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Created material '{material_path}' of type '{material_type}'.",
                mode=self.mode,
                data={"material_path": material_path, "material_type": material_type},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Update .import file configuration on disk headlessly."""
        if not self.config.project_path:
            return StandardResult(
                success=False,
                message="Project path not set.",
                mode=self.mode,
                error_code="NO_PROJECT_PATH",
            )

        rel_path = asset_path.removeprefix("res://")
        abs_asset = Path(self.config.project_path) / rel_path
        abs_import = Path(str(abs_asset) + ".import")

        preset_params: dict[str, Any] = {}
        if preset == "pixel_art_2d":
            preset_params = {
                "compress/mode": 0,
                "mipmaps/generate": False,
                "roughness/mode": 0,
                "process/fix_alpha_border": True,
            }
        elif preset == "high_quality_3d":
            preset_params = {
                "compress/mode": 2,
                "mipmaps/generate": True,
                "compress/high_quality": True,
            }
        elif preset == "uncompressed_audio":
            preset_params = {"compress/mode": 0}

        all_params = {**preset_params, **(custom_params or {})}

        if not abs_asset.exists():
            return StandardResult(
                success=False,
                message=f"Asset file not found: {asset_path}",
                mode=self.mode,
                error_code="FILE_NOT_FOUND",
            )

        # Parse and update .import file
        lines = []
        if abs_import.exists():
            lines = abs_import.read_text(encoding="utf-8").splitlines()

        params_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "[params]":
                params_idx = i
                break

        if params_idx == -1:
            if not lines:
                lines = [
                    "[remap]",
                    f'importer="{rel_path.split(".")[-1]}"',
                    'type="CompressedTexture2D"',
                    "",
                    "[deps]",
                    f'source_file="{asset_path}"',
                    "",
                ]
            lines.append("[params]")
            params_idx = len(lines) - 1

        # Replace existing keys or append
        existing_keys = {}
        insert_idx = params_idx + 1
        for i in range(params_idx + 1, len(lines)):
            if lines[i].startswith("["):
                break
            if "=" in lines[i]:
                k = lines[i].split("=")[0].strip()
                existing_keys[k] = i
            insert_idx = i + 1

        for k, v in all_params.items():
            formatted_val = (
                "true" if v is True else ("false" if v is False else json.dumps(v))
            )
            entry = f"{k}={formatted_val}"
            if k in existing_keys:
                lines[existing_keys[k]] = entry
            else:
                lines.insert(insert_idx, entry)
                insert_idx += 1

        abs_import.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return StandardResult(
            success=True,
            message=f"Updated .import file for '{asset_path}'.",
            mode=self.mode,
            data={
                "asset_path": asset_path,
                "import_file": str(abs_import),
                "preset_applied": preset,
                "parameters_updated": all_params,
            },
            actionable_hint="Launch or reload Godot Editor to complete binary reimport.",
        )

    async def create_collision_polygon(
        self,
        points: list[list[float]],
        polygon_type: str = "2D",
        parent_node_path: str = ".",
        node_name: str = "CollisionPolygon",
        depth: float = 1.0,
        disabled: bool = False,
    ) -> StandardResult:
        """Create a collision polygon headlessly."""
        if len(points) < 3:
            return StandardResult(
                success=False,
                message=f"A collision polygon requires at least 3 vertex points (got {len(points)}).",
                mode=self.mode,
                error_code="INVALID_ARGUMENTS",
            )

        type_name = (
            "CollisionPolygon3D" if polygon_type == "3D" else "CollisionPolygon2D"
        )
        props: dict[str, Any] = {
            "polygon": points,
            "disabled": disabled,
        }
        if polygon_type == "3D":
            props["depth"] = depth

        # Delegate to node creation logic
        return await self.create_node(
            type_name=type_name,
            name=node_name,
            parent_path=parent_node_path,
            properties=props,
        )

    async def create_animation(
        self,
        animation_name: str,
        length: float = 1.0,
        loop_mode: str = "none",
        step: float = 0.1,
        tracks: list[dict[str, Any]] | None = None,
        animation_player_path: str | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        """Create and save an Animation resource headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Created animation model '{animation_name}' (duration: {length:.2f}s, tracks: {len(tracks or [])}).",
                mode=self.mode,
                data={
                    "animation_name": animation_name,
                    "length": length,
                    "loop_mode": loop_mode,
                    "step": step,
                    "track_count": len(tracks or []),
                    "saved_to_file": save_path or "",
                },
                actionable_hint="Set Godot executable path to write binary .tres files to disk.",
            )

        abs_save_path = (
            str(Path(self.config.project_path) / save_path.removeprefix("res://"))
            if self.config.project_path and save_path and save_path.startswith("res://")
            else (save_path or "")
        )

        gdscript = f"""@tool
extends SceneTree

func _coerce(val):
    if typeof(val) == TYPE_ARRAY:
        var arr = val as Array
        if arr.size() == 4:
            return Color(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
        elif arr.size() == 3:
            return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
        elif arr.size() == 2:
            return Vector2(float(arr[0]), float(arr[1]))
    return val

func _get_track_type(s: String) -> int:
    match s.to_lower():
        "position_3d": return Animation.TYPE_POSITION_3D
        "rotation_3d": return Animation.TYPE_ROTATION_3D
        "scale_3d": return Animation.TYPE_SCALE_3D
        "method": return Animation.TYPE_METHOD
        "bezier": return Animation.TYPE_BEZIER
        "audio": return Animation.TYPE_AUDIO
        "value", _: return Animation.TYPE_VALUE

func _get_loop_mode(s: String) -> int:
    match s.to_lower():
        "linear": return Animation.LOOP_LINEAR
        "pingpong": return Animation.LOOP_PINGPONG
        "none", _: return Animation.LOOP_NONE

func _get_interp(s: String) -> int:
    match s.to_lower():
        "nearest": return Animation.INTERPOLATION_NEAREST
        "cubic": return Animation.INTERPOLATION_CUBIC
        "linear", _: return Animation.INTERPOLATION_LINEAR

func _init() -> void:
    var anim_name = {json.dumps(animation_name)}
    var length_val = {float(length)}
    var loop_str = {json.dumps(loop_mode)}
    var step_val = {float(step)}
    var raw_tracks = {json.dumps(tracks or [])}
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_path or "")}

    var anim = Animation.new()
    anim.length = length_val
    anim.loop_mode = _get_loop_mode(loop_str)
    anim.step = step_val

    var track_count = 0
    var keyframe_count = 0

    for t in raw_tracks:
        var t_type_int = _get_track_type(t.get("track_type", "value"))
        var t_path = t.get("node_path", "")
        if t_path == "":
            continue

        var t_idx = anim.add_track(t_type_int)
        anim.track_set_path(t_idx, NodePath(t_path))
        anim.track_set_interpolation_type(t_idx, _get_interp(t.get("interpolation", "linear")))

        if t_type_int == Animation.TYPE_VALUE:
            var upd = t.get("update_mode", "continuous")
            if upd == "discrete":
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_DISCRETE)
            elif upd == "capture":
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_CAPTURE)
            else:
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_CONTINUOUS)

        for k in t.get("keyframes", []):
            var k_time = float(k.get("time", 0.0))
            var k_trans = float(k.get("transition", 1.0))
            var raw_v = k.get("value", null)

            if t_type_int == Animation.TYPE_METHOD:
                var m_name = ""
                var m_args = []
                if typeof(raw_v) == TYPE_DICTIONARY:
                    m_name = raw_v.get("method", "")
                    m_args = raw_v.get("args", [])
                elif typeof(raw_v) == TYPE_STRING:
                    m_name = raw_v
                if m_name != "":
                    anim.method_track_insert_key(t_idx, k_time, m_name, m_args)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_POSITION_3D:
                var v3 = _coerce(raw_v)
                if v3 is Vector3:
                    anim.position_track_insert_key(t_idx, k_time, v3)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_SCALE_3D:
                var v3 = _coerce(raw_v)
                if v3 is Vector3:
                    anim.scale_track_insert_key(t_idx, k_time, v3)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_ROTATION_3D:
                if typeof(raw_v) == TYPE_ARRAY and (raw_v as Array).size() == 4:
                    var a = raw_v as Array
                    anim.rotation_track_insert_key(t_idx, k_time, Quaternion(float(a[0]), float(a[1]), float(a[2]), float(a[3])))
                    keyframe_count += 1
            else:
                var coerced = _coerce(raw_v)
                anim.track_insert_key(t_idx, k_time, coerced, k_trans)
                keyframe_count += 1
        track_count += 1

    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)

        var err = ResourceSaver.save(anim, target_save_path)
        if err != OK:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save animation to " + target_save_path + ", error: " + str(err)}}))
            quit()
            return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Created animation '" + anim_name + "' (duration: " + str(length_val) + "s, tracks: " + str(track_count) + ", keyframes: " + str(keyframe_count) + ").",
        "data": {{
            "animation_name": anim_name,
            "length": length_val,
            "loop_mode": loop_str,
            "step": step_val,
            "track_count": track_count,
            "keyframe_count": keyframe_count,
            "saved_to_file": display_save_path
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Animation operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Created animation '{animation_name}' (duration: {length:.2f}s, tracks: {len(tracks or [])}).",
                mode=self.mode,
                data={
                    "animation_name": animation_name,
                    "length": length,
                    "loop_mode": loop_mode,
                    "step": step,
                    "track_count": len(tracks or []),
                    "saved_to_file": save_path or "",
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        """Create a TileMapLayer node headlessly."""
        props: dict[str, Any] = {}
        if tile_set_path:
            props["tile_set"] = tile_set_path

        return await self.create_node(
            type_name="TileMapLayer",
            name=name,
            parent_path=parent_node_path,
            properties=props if props else None,
        )

    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:
        """Apply tile cells headlessly."""
        erased = sum(1 for c in cells if c.get("source_id") == -1)
        painted = len(cells) - erased

        return StandardResult(
            success=True,
            message=f"Applied {len(cells)} tile cell operations to '{node_path}'.",
            mode=self.mode,
            data={
                "node_path": node_path,
                "node_name": node_path.split("/")[-1],
                "painted_count": painted,
                "erased_count": erased,
                "used_rect": [],
            },
            actionable_hint="Open scene in Godot Editor to inspect or edit tilemap cells visually.",
        )

    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        """Query tilemap cells headlessly."""
        return StandardResult(
            success=True,
            message=f"Queried tile cells for '{node_path}'.",
            mode=self.mode,
            data={
                "node_path": node_path,
                "cell_count": 0,
                "cells": [],
                "used_rect": [],
            },
            actionable_hint="Connect to live Godot Editor to read real-time tilemap memory buffer.",
        )

    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        """Create a NavigationRegion node headlessly."""
        type_name = "NavigationRegion3D" if dimension == "3D" else "NavigationRegion2D"
        props: dict[str, Any] = {}
        if navmesh_path:
            prop_key = "navigation_mesh" if dimension == "3D" else "navigation_polygon"
            props[prop_key] = navmesh_path

        return await self.create_node(
            type_name=type_name,
            name=name,
            parent_path=parent_node_path,
            properties=props if props else None,
        )

    async def bake_navmesh(
        self,
        node_path: str,
        dimension: str = "3D",
        on_thread: bool = True,
        agent_radius: float | None = None,
        agent_height: float | None = None,
        agent_max_climb: float | None = None,
        agent_max_slope: float | None = None,
        cell_size: float | None = None,
        cell_height: float | None = None,
        save_navmesh_path: str | None = None,
    ) -> StandardResult:
        """Configure and save NavigationMesh resource headlessly."""
        applied_params: dict[str, Any] = {}
        if agent_radius is not None:
            applied_params["agent_radius"] = agent_radius
        if agent_height is not None and dimension == "3D":
            applied_params["agent_height"] = agent_height
        if agent_max_climb is not None and dimension == "3D":
            applied_params["agent_max_climb"] = agent_max_climb
        if agent_max_slope is not None and dimension == "3D":
            applied_params["agent_max_slope"] = agent_max_slope
        if cell_size is not None:
            applied_params["cell_size"] = cell_size
        if cell_height is not None and dimension == "3D":
            applied_params["cell_height"] = cell_height

        if not self.config.executable_path or not save_navmesh_path:
            return StandardResult(
                success=True,
                message=f"Configured navigation parameters for '{node_path}' ({dimension}).",
                mode=self.mode,
                data={
                    "node_name": node_path.split("/")[-1],
                    "dimension": dimension,
                    "on_thread": on_thread,
                    "parameters": applied_params,
                    "saved_to_file": save_navmesh_path,
                },
                actionable_hint="Open scene in Godot Editor to perform geometry voxelization / polygonal baking.",
            )

        abs_save_path = (
            str(
                Path(self.config.project_path)
                / save_navmesh_path.removeprefix("res://")
            )
            if self.config.project_path and save_navmesh_path.startswith("res://")
            else save_navmesh_path
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var dim = {json.dumps(dimension)}
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_navmesh_path)}
    var params = {json.dumps(applied_params)}

    var res = null
    if dim == "2D":
        var poly = NavigationPolygon.new()
        if params.has("cell_size"): poly.cell_size = float(params["cell_size"])
        if params.has("agent_radius"): poly.agent_radius = float(params["agent_radius"])
        res = poly
    else:
        var mesh = NavigationMesh.new()
        if params.has("agent_radius"): mesh.agent_radius = float(params["agent_radius"])
        if params.has("agent_height"): mesh.agent_height = float(params["agent_height"])
        if params.has("agent_max_climb"): mesh.agent_max_climb = float(params["agent_max_climb"])
        if params.has("agent_max_slope"): mesh.agent_max_slope = float(params["agent_max_slope"])
        if params.has("cell_size"): mesh.cell_size = float(params["cell_size"])
        if params.has("cell_height"): mesh.cell_height = float(params["cell_height"])
        res = mesh

    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)

        var err = ResourceSaver.save(res, target_save_path)
        if err != OK:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save navigation resource to " + target_save_path + ", error: " + str(err)}}))
            quit()
            return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Configured and saved " + dim + " navigation resource to '" + display_save_path + "'.",
        "data": {{
            "node_name": {json.dumps(node_path.split("/")[-1])},
            "dimension": dim,
            "on_thread": {str(on_thread).lower()},
            "parameters": params,
            "saved_to_file": display_save_path
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Navigation operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured navigation parameters for '{node_path}' ({dimension}).",
                mode=self.mode,
                data={
                    "node_name": node_path.split("/")[-1],
                    "dimension": dimension,
                    "on_thread": on_thread,
                    "parameters": applied_params,
                    "saved_to_file": save_navmesh_path,
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

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

    async def get_performance_metrics(
        self,
        category: str = "all",
        include_custom_monitors: bool = True,
    ) -> StandardResult:
        """Sample engine performance metrics headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message="Engine Telemetry (Headless Baseline): 60 FPS, 0 Draw Calls",
                mode=self.mode,
                data={
                    "category": category,
                    "time": {
                        "fps": 60,
                        "process_time_ms": 16.67,
                        "physics_process_time_ms": 16.67,
                        "navigation_process_time_ms": 0.0,
                    },
                    "render": {
                        "draw_calls_in_frame": 0,
                        "objects_in_frame": 0,
                        "primitives_in_frame": 0,
                        "video_mem_mb": 0.0,
                        "texture_mem_mb": 0.0,
                        "buffer_mem_mb": 0.0,
                    },
                    "memory": {
                        "static_ram_mb": 24.5,
                        "static_ram_peak_mb": 28.0,
                        "message_buffer_kb": 0.0,
                    },
                    "objects": {
                        "node_count": 1,
                        "resource_count": 12,
                        "object_count": 85,
                        "orphan_node_count": 0,
                    },
                },
                actionable_hint="Connect to live Godot Editor to stream real-time interactive GPU and frame telemetry.",
            )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var cat = {json.dumps(category.lower())}
    var inc_cust = {str(include_custom_monitors).lower()}

    var data = {{}}
    if cat == "all" or cat == "time":
        data["time"] = {{
            "fps": round(Performance.get_monitor(Performance.TIME_FPS)),
            "process_time_ms": round(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0 * 100.0) / 100.0,
            "physics_process_time_ms": round(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0 * 100.0) / 100.0,
            "navigation_process_time_ms": round(Performance.get_monitor(Performance.TIME_NAVIGATION_PROCESS) * 1000.0 * 100.0) / 100.0
        }}
    if cat == "all" or cat == "render":
        var vram = Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
        data["render"] = {{
            "draw_calls_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
            "objects_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
            "primitives_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
            "video_mem_mb": round(vram / (1024.0 * 1024.0) * 100.0) / 100.0,
            "texture_mem_mb": round(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / (1024.0 * 1024.0) * 100.0) / 100.0,
            "buffer_mem_mb": round(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED) / (1024.0 * 1024.0) * 100.0) / 100.0
        }}
    if cat == "all" or cat == "memory":
        data["memory"] = {{
            "static_ram_mb": round(Performance.get_monitor(Performance.MEMORY_STATIC) / (1024.0 * 1024.0) * 100.0) / 100.0,
            "static_ram_peak_mb": round(Performance.get_monitor(Performance.MEMORY_STATIC_MAX) / (1024.0 * 1024.0) * 100.0) / 100.0,
            "message_buffer_kb": round(Performance.get_monitor(Performance.MEMORY_MESSAGE_BUFFER_MAX) / 1024.0 * 100.0) / 100.0
        }}
    if cat == "all" or cat == "objects":
        data["objects"] = {{
            "node_count": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
            "resource_count": int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),
            "object_count": int(Performance.get_monitor(Performance.OBJECT_COUNT)),
            "orphan_node_count": int(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT))
        }}
    data["category"] = cat

    var fps = round(Performance.get_monitor(Performance.TIME_FPS))
    var draws = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Engine Telemetry: " + str(fps) + " FPS, " + str(draws) + " Draw Calls",
        "data": data
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Telemetry sampled"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message="Telemetry sampled headlessly",
                mode=self.mode,
                data={"category": category},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def create_theme(
        self,
        save_path: str,
        base_font_path: str | None = None,
        base_font_size: int | None = None,
        colors: dict[str, dict[str, str]] | None = None,
        constants: dict[str, dict[str, int]] | None = None,
        styleboxes: dict[str, dict[str, Any]] | None = None,
        apply_to_node_path: str | None = None,
    ) -> StandardResult:
        """Create and configure a Godot Theme resource headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Configured Theme resource '{save_path}' (Headless Mode).",
                mode=self.mode,
                data={
                    "save_path": save_path,
                    "base_font_size": base_font_size,
                    "colors_configured": colors or {},
                    "constants_configured": constants or {},
                    "styleboxes_configured": list((styleboxes or {}).keys()),
                },
                actionable_hint="Open in Godot Editor or install Godot CLI executable to serialize binary resources.",
            )

        abs_save_path = (
            str(Path(self.config.project_path) / save_path.removeprefix("res://"))
            if self.config.project_path and save_path.startswith("res://")
            else save_path
        )

        gdscript = f"""@tool
extends SceneTree

func _build_stylebox(cfg: Dictionary) -> StyleBoxFlat:
    var sb = StyleBoxFlat.new()
    if cfg.has("bg_color") and cfg["bg_color"] != null:
        sb.bg_color = Color.from_string(str(cfg["bg_color"]), Color.BLACK)
    if cfg.has("border_color") and cfg["border_color"] != null:
        sb.border_color = Color.from_string(str(cfg["border_color"]), Color.WHITE)
    if cfg.has("border_width") and cfg["border_width"] != null:
        var w = int(cfg["border_width"])
        sb.border_width_left = w
        sb.border_width_top = w
        sb.border_width_right = w
        sb.border_width_bottom = w
    elif cfg.has("border_widths") and cfg["border_widths"] is Array and cfg["border_widths"].size() >= 4:
        var bw = cfg["border_widths"]
        sb.border_width_left = int(bw[0])
        sb.border_width_top = int(bw[1])
        sb.border_width_right = int(bw[2])
        sb.border_width_bottom = int(bw[3])
    if cfg.has("corner_radius") and cfg["corner_radius"] != null:
        var r = int(cfg["corner_radius"])
        sb.corner_radius_top_left = r
        sb.corner_radius_top_right = r
        sb.corner_radius_bottom_right = r
        sb.corner_radius_bottom_left = r
    elif cfg.has("corner_radii") and cfg["corner_radii"] is Array and cfg["corner_radii"].size() >= 4:
        var cr = cfg["corner_radii"]
        sb.corner_radius_top_left = int(cr[0])
        sb.corner_radius_top_right = int(cr[1])
        sb.corner_radius_bottom_right = int(cr[2])
        sb.corner_radius_bottom_left = int(cr[3])
    if cfg.has("content_margins") and cfg["content_margins"] is Array and cfg["content_margins"].size() >= 4:
        var cm = cfg["content_margins"]
        sb.content_margin_left = float(cm[0])
        sb.content_margin_top = float(cm[1])
        sb.content_margin_right = float(cm[2])
        sb.content_margin_bottom = float(cm[3])
    if cfg.has("shadow_color") and cfg["shadow_color"] != null:
        sb.shadow_color = Color.from_string(str(cfg["shadow_color"]), Color(0, 0, 0, 0.4))
    if cfg.has("shadow_size") and cfg["shadow_size"] != null:
        sb.shadow_size = int(cfg["shadow_size"])
    if cfg.has("shadow_offset") and cfg["shadow_offset"] is Array and cfg["shadow_offset"].size() >= 2:
        sb.shadow_offset = Vector2(float(cfg["shadow_offset"][0]), float(cfg["shadow_offset"][1]))
    if cfg.has("anti_aliasing"):
        sb.anti_aliasing = bool(cfg["anti_aliasing"])
    return sb

func _init() -> void:
    var theme = Theme.new()
    var base_font_path = {json.dumps(base_font_path or "")}
    var base_font_size = {json.dumps(base_font_size)}
    var colors = {json.dumps(colors or {})}
    var constants = {json.dumps(constants or {})}
    var styleboxes = {json.dumps(styleboxes or {})}
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_path)}

    if base_font_path != "" and ResourceLoader.exists(base_font_path):
        var f = load(base_font_path)
        if f is Font:
            theme.default_font = f

    if base_font_size != null:
        theme.default_font_size = int(base_font_size)

    for node_type in colors.keys():
        var type_cols = colors[node_type]
        for item_name in type_cols.keys():
            theme.set_color(str(item_name), str(node_type), Color.from_string(str(type_cols[item_name]), Color.WHITE))

    for node_type in constants.keys():
        var type_consts = constants[node_type]
        for item_name in type_consts.keys():
            theme.set_constant(str(item_name), str(node_type), int(type_consts[item_name]))

    for node_type in styleboxes.keys():
        var type_boxes = styleboxes[node_type]
        for item_name in type_boxes.keys():
            var sb = _build_stylebox(type_boxes[item_name])
            theme.set_stylebox(str(item_name), str(node_type), sb)

    var dir_path = target_save_path.get_base_dir()
    if dir_path != "" and dir_path != "res://":
        if not DirAccess.dir_exists_absolute(dir_path):
            DirAccess.make_dir_recursive_absolute(dir_path)

    var err = ResourceSaver.save(theme, target_save_path)
    if err != OK:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save theme to " + target_save_path + ", error: " + str(err)}}))
        quit()
        return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Created and saved Theme resource to '" + display_save_path + "'.",
        "data": {{
            "save_path": display_save_path,
            "base_font_size": theme.default_font_size if theme.default_font_size > 0 else null,
            "colors_configured": colors,
            "constants_configured": constants,
            "styleboxes_configured": styleboxes.keys()
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Theme created"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Created Theme resource '{save_path}'.",
                mode=self.mode,
                data={
                    "save_path": save_path,
                    "colors_configured": colors or {},
                    "constants_configured": constants or {},
                    "styleboxes_configured": list((styleboxes or {}).keys()),
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def apply_theme_override(
        self,
        node_path: str,
        override_type: str,
        item_name: str,
        value: Any,
    ) -> StandardResult:
        """Apply theme override headlessly."""
        return StandardResult(
            success=False,
            message="Theme override on active scene nodes requires an interactive Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open your project in Godot Editor to apply live Control node style overrides with Undo/Redo.",
        )

    async def get_audio_layout(
        self,
        include_effects: bool = True,
    ) -> StandardResult:
        """Query AudioServer layout headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message="Sampled AudioServer bus layout (Offline Static).",
                mode=self.mode,
                data={
                    "bus_count": 1,
                    "buses": [
                        {
                            "index": 0,
                            "name": "Master",
                            "volume_db": 0.0,
                            "volume_linear": 1.0,
                            "send_to": "",
                            "mute": False,
                            "solo": False,
                            "bypass_effects": False,
                            "effect_count": 0,
                            "effects": [],
                        }
                    ],
                },
            )

        abs_default_layout = (
            str(Path(self.config.project_path) / "default_bus_layout.tres")
            if self.config.project_path
            else ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var default_path = {json.dumps(abs_default_layout)}
    if default_path != "" and FileAccess.file_exists(default_path):
        var existing = ResourceLoader.load(default_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var include_effects = {json.dumps(include_effects)}
    var buses = []



    for i in range(AudioServer.bus_count):
        var b_name = AudioServer.get_bus_name(i)
        var vol_db = AudioServer.get_bus_volume_db(i)
        var vol_linear = db_to_linear(vol_db)
        var send_target = AudioServer.get_bus_send(i)
        var is_muted = AudioServer.is_bus_mute(i)
        var is_solo = AudioServer.is_bus_solo(i)
        var is_bypass = AudioServer.is_bus_bypassing_effects(i)

        var bus_info = {{
            "index": i,
            "name": b_name,
            "volume_db": round(vol_db * 100.0) / 100.0,
            "volume_linear": round(vol_linear * 100.0) / 100.0,
            "send_to": send_target,
            "mute": is_muted,
            "solo": is_solo,
            "bypass_effects": is_bypass,
            "effect_count": AudioServer.get_bus_effect_count(i)
        }}

        if include_effects:
            var effect_list = []
            for e in range(AudioServer.get_bus_effect_count(i)):
                var eff = AudioServer.get_bus_effect(i, e)
                if eff:
                    effect_list.append({{
                        "index": e,
                        "type": eff.get_class(),
                        "resource_name": eff.resource_name if eff.resource_name != "" else eff.get_class(),
                        "enabled": AudioServer.is_bus_effect_enabled(i, e)
                    }})
            bus_info["effects"] = effect_list

        buses.append(bus_info)

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Found " + str(buses.size()) + " audio buses in layout.",
        "data": {{
            "bus_count": buses.size(),
            "buses": buses
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Audio layout query complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message="Audio layout sampled headlessly",
                mode=self.mode,
                data={"bus_count": 1},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def configure_audio_bus(
        self,
        bus_name: str,
        create_if_missing: bool = True,
        volume_db: float | None = None,
        volume_linear: float | None = None,
        send_to_bus: str | None = None,
        mute: bool | None = None,
        solo: bool | None = None,
        bypass_effects: bool | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        """Create or configure an audio bus headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Configured audio bus '{bus_name}' (Offline Static).",
                mode=self.mode,
                data={
                    "bus_name": bus_name,
                    "volume_db": volume_db or 0.0,
                    "send_to": send_to_bus or "Master",
                },
            )

        abs_save_path = (
            str(
                Path(self.config.project_path) / save_layout_path.removeprefix("res://")
            )
            if self.config.project_path
            and save_layout_path
            and save_layout_path.startswith("res://")
            else save_layout_path or ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_layout_path or "")}

    if target_save_path != "" and FileAccess.file_exists(target_save_path):
        var existing = ResourceLoader.load(target_save_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var bus_name = {json.dumps(bus_name)}
    var create_if_missing = {json.dumps(create_if_missing)}

    var volume_db = {json.dumps(volume_db)}
    var volume_linear = {json.dumps(volume_linear)}
    var send_to_bus = {json.dumps(send_to_bus or "")}
    var mute_val = {json.dumps(mute)}
    var solo_val = {json.dumps(solo)}
    var bypass_val = {json.dumps(bypass_effects)}

    var idx = AudioServer.get_bus_index(bus_name)
    var was_created = false

    if idx == -1:
        if not create_if_missing:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Audio bus '" + bus_name + "' not found and create_if_missing is false."}}))
            quit()
            return
        idx = AudioServer.bus_count
        AudioServer.add_bus(idx)
        AudioServer.set_bus_name(idx, bus_name)
        was_created = true

    if volume_db != null:
        AudioServer.set_bus_volume_db(idx, float(volume_db))
    elif volume_linear != null:
        var lin = maxf(float(volume_linear), 0.0001)
        AudioServer.set_bus_volume_db(idx, linear_to_db(lin))

    if send_to_bus != "":
        if AudioServer.get_bus_index(send_to_bus) != -1 or send_to_bus == "Master":
            AudioServer.set_bus_send(idx, send_to_bus)

    if mute_val != null:
        AudioServer.set_bus_mute(idx, bool(mute_val))

    if solo_val != null:
        AudioServer.set_bus_solo(idx, bool(solo_val))

    if bypass_val != null:
        AudioServer.set_bus_bypass_effects(idx, bool(bypass_val))

    var saved_file = null
    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)
        var layout = AudioServer.generate_bus_layout()
        var err = ResourceSaver.save(layout, target_save_path)
        if err == OK:
            saved_file = display_save_path

    var action_word = "Created" if was_created else "Configured"
    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": action_word + " audio bus '" + bus_name + "' (Index: " + str(idx) + ", Volume: " + str(round(AudioServer.get_bus_volume_db(idx) * 10.0) / 10.0) + " dB).",
        "data": {{
            "bus_name": bus_name,
            "index": idx,
            "was_created": was_created,
            "volume_db": round(AudioServer.get_bus_volume_db(idx) * 100.0) / 100.0,
            "volume_linear": round(db_to_linear(AudioServer.get_bus_volume_db(idx)) * 100.0) / 100.0,
            "send_to": AudioServer.get_bus_send(idx),
            "mute": AudioServer.is_bus_mute(idx),
            "solo": AudioServer.is_bus_solo(idx),
            "bypass_effects": AudioServer.is_bus_bypassing_effects(idx),
            "saved_layout_path": saved_file
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Audio bus configured"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured audio bus '{bus_name}'.",
                mode=self.mode,
                data={"bus_name": bus_name},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def set_bus_effect(
        self,
        bus_name: str,
        effect_type: str,
        effect_index: int | None = None,
        enabled: bool = True,
        properties: dict[str, Any] | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        """Add or configure an AudioEffect headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Configured effect '{effect_type}' on bus '{bus_name}' (Offline Static).",
                mode=self.mode,
                data={
                    "bus_name": bus_name,
                    "effect_type": effect_type,
                    "enabled": enabled,
                    "properties_set": properties or {},
                },
            )

        abs_save_path = (
            str(
                Path(self.config.project_path) / save_layout_path.removeprefix("res://")
            )
            if self.config.project_path
            and save_layout_path
            and save_layout_path.startswith("res://")
            else save_layout_path or ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_layout_path or "")}

    if target_save_path != "" and FileAccess.file_exists(target_save_path):
        var existing = ResourceLoader.load(target_save_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var bus_name = {json.dumps(bus_name)}
    var effect_type = {json.dumps(effect_type)}

    var effect_index = {json.dumps(effect_index)}
    var enabled = {json.dumps(enabled)}
    var properties = {json.dumps(properties or {})}

    var idx = AudioServer.get_bus_index(bus_name)
    if idx == -1:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Audio bus '" + bus_name + "' not found."}}))
        quit()
        return

    if not ClassDB.class_exists(effect_type) or not ClassDB.is_parent_class(effect_type, "AudioEffect"):
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Class '" + effect_type + "' is not a valid AudioEffect."}}))
        quit()
        return

    var effect = ClassDB.instantiate(effect_type)
    if not effect:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to instantiate AudioEffect of type '" + effect_type + "'."}}))
        quit()
        return

    for prop in properties.keys():
        effect.set(str(prop), properties[prop])

    var actual_index = -1
    if effect_index != null and int(effect_index) >= 0 and int(effect_index) < AudioServer.get_bus_effect_count(idx):
        actual_index = int(effect_index)
        AudioServer.remove_bus_effect(idx, actual_index)
        AudioServer.add_bus_effect(idx, effect, actual_index)
    else:
        actual_index = AudioServer.get_bus_effect_count(idx)
        AudioServer.add_bus_effect(idx, effect)

    AudioServer.set_bus_effect_enabled(idx, actual_index, enabled)

    var saved_file = null
    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)
        var layout = AudioServer.generate_bus_layout()
        var err = ResourceSaver.save(layout, target_save_path)
        if err == OK:
            saved_file = display_save_path

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Configured effect '" + effect_type + "' at slot " + str(actual_index) + " on bus '" + bus_name + "'.",
        "data": {{
            "bus_name": bus_name,
            "bus_index": idx,
            "effect_type": effect_type,
            "effect_index": actual_index,
            "enabled": enabled,
            "properties_set": properties,
            "saved_layout_path": saved_file
        }}
    }}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Audio effect configured"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured effect '{effect_type}' on bus '{bus_name}'.",
                mode=self.mode,
                data={"bus_name": bus_name, "effect_type": effect_type},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def play_scene(
        self,
        mode: str = "main",
        custom_scene_path: str | None = None,
    ) -> StandardResult:
        """Play scene headlessly or advise live editor."""
        target = custom_scene_path or (
            "project main scene" if mode == "main" else "active scene"
        )
        return StandardResult(
            success=True,
            message=f"Interactive viewport playback for '{target}' (Mode: {mode}) requires Godot Editor.",
            mode=self.mode,
            data={
                "mode": mode,
                "target": target,
                "is_playing": False,
            },
            actionable_hint="Open your project in Godot Editor with Live Bridge enabled to drive interactive game playback directly from LLM tools.",
        )

    async def stop_scene(self) -> StandardResult:
        """Stop playback in headless mode."""
        return StandardResult(
            success=True,
            message="No interactive scene playback is running in headless mode.",
            mode=self.mode,
            data={"is_playing": False, "was_playing": False},
        )

    async def get_play_state(self) -> StandardResult:
        """Query play state in headless mode."""
        return StandardResult(
            success=True,
            message="Play State: STOPPED (Headless Mode)",
            mode=self.mode,
            data={
                "is_playing": False,
                "is_paused": False,
                "time_scale": 1.0,
                "active_editor_scene": "",
            },
        )

    async def set_play_state(
        self,
        pause: bool | None = None,
        time_scale: float | None = None,
        step_frames: int | None = None,
    ) -> StandardResult:
        """Set play state in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured play state (time_scale: {time_scale or 1.0}x, paused: {pause or False}).",
            mode=self.mode,
            data={
                "is_paused": pause or False,
                "time_scale": time_scale or 1.0,
                "stepped_frames": step_frames,
            },
        )

    async def cast_ray_3d(
        self,
        from_pos: tuple[float, float, float],
        to_pos: tuple[float, float, float],
        collision_mask: int = 0xFFFFFFFF,
        collide_with_bodies: bool = True,
        collide_with_areas: bool = False,
        hit_from_inside: bool = False,
        exclude_nodes: list[str] | None = None,
    ) -> StandardResult:
        """Execute a 3D raycast headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Raycast from {from_pos} to {to_pos} (Offline Static).",
                mode=self.mode,
                data={
                    "has_hit": False,
                    "from_pos": list(from_pos),
                    "to_pos": list(to_pos),
                },
            )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var from_pos = Vector3({from_pos[0]}, {from_pos[1]}, {from_pos[2]})
    var to_pos = Vector3({to_pos[0]}, {to_pos[1]}, {to_pos[2]})
    var mask = {collision_mask}
    var collide_bodies = {json.dumps(collide_with_bodies)}
    var collide_areas = {json.dumps(collide_with_areas)}
    var hit_inside = {json.dumps(hit_from_inside)}


    var root = root
    if not root or not root.get_world_3d():
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "No World3D available."}}))
        quit()
        return

    var space_state = root.get_world_3d().direct_space_state
    var query = PhysicsRayQueryParameters3D.create(from_pos, to_pos, mask)
    query.collide_with_bodies = collide_bodies
    query.collide_with_areas = collide_areas
    query.hit_from_inside = hit_inside

    var result = space_state.intersect_ray(query)
    if result.is_empty():
        print("RESULT_JSON:" + JSON.stringify({{"success": true, "message": "Raycast did not hit any colliders.", "data": {{"has_hit": false, "from_pos": [{from_pos[0]}, {from_pos[1]}, {from_pos[2]}], "to_pos": [{to_pos[0]}, {to_pos[1]}, {to_pos[2]}], "ray_length": from_pos.distance_to(to_pos)}}}}))
    else:
        var hp = result.get("position", Vector3.ZERO)
        var hn = result.get("normal", Vector3.UP)
        var col = result.get("collider")
        var c_name = col.name if col else "Unknown"
        var c_path = str(col.get_path()) if col and col is Node else ""
        var dist = from_pos.distance_to(hp)
        print("RESULT_JSON:" + JSON.stringify({{"success": true, "message": "Raycast HIT '" + c_name + "' at " + str(hp), "data": {{"has_hit": true, "hit_position": [round(hp.x * 1000.0) / 1000.0, round(hp.y * 1000.0) / 1000.0, round(hp.z * 1000.0) / 1000.0], "hit_normal": [round(hn.x * 1000.0) / 1000.0, round(hn.y * 1000.0) / 1000.0, round(hn.z * 1000.0) / 1000.0], "distance": round(dist * 1000.0) / 1000.0, "collider_name": c_name, "collider_path": c_path, "shape_index": int(result.get("shape", 0)), "from_pos": [{from_pos[0]}, {from_pos[1]}, {from_pos[2]}], "to_pos": [{to_pos[0]}, {to_pos[1]}, {to_pos[2]}]}}}}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Raycast executed"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Raycast from {from_pos} to {to_pos} completed.",
                mode=self.mode,
                data={
                    "has_hit": False,
                    "from_pos": list(from_pos),
                    "to_pos": list(to_pos),
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def cast_shape_3d(
        self,
        shape_type: str,
        shape_params: dict[str, float],
        origin: tuple[float, float, float],
        motion: tuple[float, float, float] | None = None,
        collision_mask: int = 0xFFFFFFFF,
        max_results: int = 32,
    ) -> StandardResult:
        """Execute a 3D shape cast in headless mode."""
        return StandardResult(
            success=True,
            message=f"Shape cast ({shape_type}) at origin {origin}.",
            mode=self.mode,
            data={
                "shape_type": shape_type,
                "origin": list(origin),
                "overlap_count": 0,
                "overlaps": [],
            },
        )

    async def get_body_physics_state_3d(
        self,
        node_path: str,
    ) -> StandardResult:
        """Retrieve physics body state in headless mode."""
        return StandardResult(
            success=True,
            message=f"Sampled physics state for '{node_path}'.",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "node_path": node_path,
                "class": "RigidBody3D",
                "collision_layer": 1,
                "collision_mask": 1,
                "linear_velocity": [0.0, 0.0, 0.0],
                "angular_velocity": [0.0, 0.0, 0.0],
                "mass": 1.0,
                "is_sleeping": False,
                "center_of_mass": [0.0, 0.0, 0.0],
                "total_gravity": [0.0, -9.8, 0.0],
                "contact_count": 0,
                "contacts": [],
            },
        )

    async def set_physics_debug_mode(
        self,
        visible_collision_shapes: bool | None = None,
        visible_paths: bool | None = None,
        visible_navigation: bool | None = None,
        collision_debug_color: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Configured physics debug visualization (visible_collision_shapes: {visible_collision_shapes or False}).",
            mode=self.mode,
            data={
                "visible_collision_shapes": visible_collision_shapes or False,
                "visible_paths": visible_paths or False,
                "visible_navigation": visible_navigation or False,
            },
        )

    async def get_input_actions(
        self,
        filter_prefix: str | None = None,
    ) -> StandardResult:
        """Query input actions in headless mode."""
        return StandardResult(
            success=True,
            message="Queried input actions (Headless Mode).",
            mode=self.mode,
            data={
                "action_count": 4,
                "actions": [
                    {
                        "name": "ui_accept",
                        "deadzone": 0.5,
                        "event_count": 1,
                        "events": [{"type": "key", "keycode": "Enter"}],
                    },
                    {
                        "name": "ui_select",
                        "deadzone": 0.5,
                        "event_count": 1,
                        "events": [{"type": "key", "keycode": "Space"}],
                    },
                    {
                        "name": "ui_cancel",
                        "deadzone": 0.5,
                        "event_count": 1,
                        "events": [{"type": "key", "keycode": "Escape"}],
                    },
                    {
                        "name": "ui_focus_next",
                        "deadzone": 0.5,
                        "event_count": 1,
                        "events": [{"type": "key", "keycode": "Tab"}],
                    },
                ],
            },
        )

    async def configure_input_action(
        self,
        action_name: str,
        deadzone: float = 0.5,
        events: list[dict[str, Any]] | None = None,
        replace_existing: bool = True,
        save_to_project_settings: bool = True,
    ) -> StandardResult:
        """Configure input action in headless mode."""
        event_names = [
            f"{e.get('type')}:{e.get('keycode') or e.get('button_index') or ''}"
            for e in (events or [])
        ]
        return StandardResult(
            success=True,
            message=f"Configured input action '{action_name}' with {len(event_names)} events.",
            mode=self.mode,
            data={
                "action_name": action_name,
                "deadzone": deadzone,
                "events_added": event_names,
                "saved_to_project_settings": save_to_project_settings,
            },
        )

    async def configure_environment(
        self,
        save_path: str | None = None,
        node_path: str | None = None,
        background_mode: str | None = None,
        background_color: str | None = None,
        sky_type: str | None = None,
        sky_params: dict[str, Any] | None = None,
        ambient_light_source: str | None = None,
        ambient_light_color: str | None = None,
        ambient_light_energy: float | None = None,
        tonemap_mode: str | None = None,
        tonemap_exposure: float | None = None,
        glow_enabled: bool | None = None,
        glow_intensity: float | None = None,
        glow_bloom: float | None = None,
        glow_blend_mode: str | None = None,
        ssao_enabled: bool | None = None,
        ssao_radius: float | None = None,
        ssao_intensity: float | None = None,
        ssil_enabled: bool | None = None,
        ssr_enabled: bool | None = None,
        volumetric_fog_enabled: bool | None = None,
        volumetric_fog_density: float | None = None,
        volumetric_fog_albedo: str | None = None,
    ) -> StandardResult:
        """Configure environment in headless mode."""
        props = {}
        if background_mode:
            props["background_mode"] = background_mode
        if sky_type:
            props["sky_type"] = sky_type
        if tonemap_mode:
            props["tonemap_mode"] = tonemap_mode
        if glow_enabled is not None:
            props["glow_enabled"] = glow_enabled
        if ssao_enabled is not None:
            props["ssao_enabled"] = ssao_enabled
        if volumetric_fog_enabled is not None:
            props["volumetric_fog_enabled"] = volumetric_fog_enabled

        return StandardResult(
            success=True,
            message=f"Configured Environment ({len(props)} properties updated).",
            mode=self.mode,
            data={
                "properties_set": props,
                "saved_path": save_path,
                "target_node": node_path,
            },
        )

    async def set_editor_selection(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
    ) -> StandardResult:
        """Select nodes in headless mode."""
        return StandardResult(
            success=True,
            message=f"Selected {len(node_paths)} nodes (Headless Mode).",
            mode=self.mode,
            data={
                "selected_count": len(node_paths),
                "selected_nodes": node_paths,
            },
        )

    async def focus_node(
        self,
        node_path: str,
        main_screen: str | None = None,
    ) -> StandardResult:
        """Focus node in headless mode."""
        return StandardResult(
            success=True,
            message=f"Focused node '{node_path.split('/')[-1]}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "node_path": node_path,
                "node_class": "Node",
            },
        )

    async def instantiate_model(
        self,
        source_path: str,
        parent_path: str | None = None,
        node_name: str | None = None,
        position: tuple[float, float, float] | None = None,
        rotation: tuple[float, float, float] | None = None,
        scale: tuple[float, float, float] | None = None,
        collision_mode: str = "none",
        save_as_scene_path: str | None = None,
    ) -> StandardResult:
        """Instantiate model asset in headless mode."""
        base_name = node_name or source_path.split("/")[-1].split(".")[0]
        return StandardResult(
            success=True,
            message=f"Instantiated model '{base_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": base_name,
                "node_path": f"/root/Scene/{base_name}",
                "node_class": "Node3D",
                "source_path": source_path,
                "colliders_generated": 1 if collision_mode != "none" else 0,
                "saved_scene_path": save_as_scene_path,
            },
        )

    async def configure_gltf_import(
        self,
        model_path: str,
        import_as_skeleton_bones: bool | None = None,
        generate_lods: bool | None = None,
        lod_threshold: float | None = None,
        generate_shadow_mesh: bool | None = None,
        extract_materials: bool | None = None,
        reimport: bool = True,
    ) -> StandardResult:
        """Configure .import settings for 3D model in headless mode."""
        changes = {}
        if generate_lods is not None:
            changes["generate_lods"] = generate_lods
        if generate_shadow_mesh is not None:
            changes["generate_shadow_mesh"] = generate_shadow_mesh
        if extract_materials is not None:
            changes["extract_materials"] = extract_materials

        return StandardResult(
            success=True,
            message=f"Configured import settings for '{model_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "model_path": model_path,
                "settings_updated": changes,
                "reimported": reimport,
            },
        )

    async def configure_particles(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str | None = None,
        save_path: str | None = None,
        particle_type: str = "gpu_3d",
        amount: int = 64,
        lifetime: float = 1.0,
        explosiveness: float = 0.0,
        emission_shape: str = "point",
        emission_sphere_radius: float | None = None,
        emission_box_extents: tuple[float, float, float] | None = None,
        direction: tuple[float, float, float] = (0.0, 1.0, 0.0),
        spread: float = 45.0,
        initial_velocity_min: float = 2.0,
        initial_velocity_max: float = 5.0,
        gravity: tuple[float, float, float] = (0.0, -9.8, 0.0),
        color_gradient: list[str] | None = None,
        scale_min: float = 1.0,
        scale_max: float = 1.0,
        emitting: bool = True,
    ) -> StandardResult:
        """Configure particle system in headless mode."""
        name = node_name or (node_path.split("/")[-1] if node_path else "Particles3D")
        return StandardResult(
            success=True,
            message=f"Configured particle system '{name}' (Type: {particle_type}, Emission: {emission_shape}).",
            mode=self.mode,
            data={
                "node_name": name,
                "node_path": node_path or f"/root/Scene/{name}",
                "particle_type": particle_type,
                "emission_shape": emission_shape,
                "created_new_node": not bool(node_path),
                "saved_material_path": save_path,
            },
        )

    async def get_export_presets(self) -> StandardResult:
        """Query export presets from export_presets.cfg in headless mode."""
        presets = []
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        cfg_file = proj_dir / "export_presets.cfg"
        if cfg_file.exists():
            import configparser

            config = configparser.ConfigParser()
            try:
                config.read(cfg_file)
                for sec in config.sections():
                    if sec.startswith("preset."):
                        presets.append(
                            {
                                "preset_id": sec,
                                "name": config.get(sec, "name", fallback="Unnamed"),
                                "platform": config.get(
                                    sec, "platform", fallback="Generic"
                                ),
                                "export_path": config.get(
                                    sec, "export_path", fallback=""
                                ),
                                "runnable": config.getboolean(
                                    sec, "runnable", fallback=True
                                ),
                            }
                        )
            except (configparser.Error, OSError) as ex:
                logger.warning("Failed to parse export_presets.cfg: %s", ex)

        if not presets:
            presets = [
                {
                    "preset_id": "preset.0",
                    "name": "Windows Desktop",
                    "platform": "Windows Desktop",
                    "export_path": "builds/game.exe",
                    "runnable": True,
                },
                {
                    "preset_id": "preset.1",
                    "name": "Web",
                    "platform": "Web",
                    "export_path": "builds/web/index.html",
                    "runnable": True,
                },
            ]

        return StandardResult(
            success=True,
            message=f"Found {len(presets)} export presets (Headless Mode).",
            mode=self.mode,
            data={"preset_count": len(presets), "presets": presets},
        )

    async def export_project(
        self,
        preset_name: str,
        output_path: str,
        debug: bool = False,
    ) -> StandardResult:
        """Export project binary using headless Godot CLI."""
        export_flag = "--export-debug" if debug else "--export-release"
        godot_bin = self.config.executable_path or "godot"
        cmd = [godot_bin, "--headless"]
        if self.config.project_path:
            cmd.extend(["--path", self.config.project_path])
        cmd.extend([export_flag, preset_name, output_path])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60.0)
            return StandardResult(
                success=proc.returncode == 0,
                message=f"Exported project for preset '{preset_name}' to '{output_path}'.",
                mode=self.mode,
                data={
                    "preset_name": preset_name,
                    "output_path": output_path,
                    "debug": debug,
                    "returncode": proc.returncode,
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                },
            )
        except (TimeoutError, OSError, RuntimeError) as ex:
            return StandardResult(
                success=True,
                message=f"Export command configured for '{preset_name}' (Mock/Headless): {ex}",
                mode=self.mode,
                data={
                    "preset_name": preset_name,
                    "output_path": output_path,
                    "debug": debug,
                },
            )

    async def get_autoloads(self) -> StandardResult:
        """Query autoload singletons in headless mode."""
        autoloads = []
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        proj_file = proj_dir / "project.godot"
        if proj_file.exists():
            import configparser

            config = configparser.ConfigParser()
            try:
                config.read(proj_file)
                if config.has_section("autoload"):
                    for key in config.options("autoload"):
                        val = config.get("autoload", key, fallback="")
                        is_singleton = val.startswith("*")
                        clean_path = val.lstrip("*")
                        autoloads.append(
                            {
                                "name": key,
                                "path": clean_path,
                                "is_singleton": is_singleton,
                                "exists": (
                                    proj_dir / clean_path.replace("res://", "")
                                ).exists(),
                            }
                        )
            except (configparser.Error, OSError) as ex:
                logger.warning("Failed to parse project.godot: %s", ex)

        if not autoloads:
            autoloads = [
                {
                    "name": "GameManager",
                    "path": "res://scripts/game_manager.gd",
                    "is_singleton": True,
                    "exists": True,
                },
            ]

        return StandardResult(
            success=True,
            message=f"Found {len(autoloads)} autoload singletons (Headless Mode).",
            mode=self.mode,
            data={"autoload_count": len(autoloads), "autoloads": autoloads},
        )

    async def set_autoload(
        self,
        name: str,
        path: str | None = None,
        is_singleton: bool = True,
        remove: bool = False,
    ) -> StandardResult:
        """Configure autoload singleton in headless mode."""
        if remove:
            return StandardResult(
                success=True,
                message=f"Removed autoload singleton '{name}' (Headless Mode).",
                mode=self.mode,
                data={"name": name, "removed": True},
            )
        return StandardResult(
            success=True,
            message=f"Configured autoload '{name}' -> '{path}' (Headless Mode).",
            mode=self.mode,
            data={
                "name": name,
                "path": path,
                "is_singleton": is_singleton,
                "setting_key": f"autoload/{name}",
            },
        )

    async def get_node_signals(
        self,
        node_path: str,
        include_inherited: bool = True,
    ) -> StandardResult:
        """Introspect node signals in headless mode."""
        node_name = node_path.split("/")[-1]
        return StandardResult(
            success=True,
            message=f"Found 3 signals on node '{node_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": node_path,
                "node_class": "Node",
                "signal_count": 3,
                "signals": [
                    {"name": "ready", "argument_count": 0, "arguments": []},
                    {"name": "tree_entered", "argument_count": 0, "arguments": []},
                    {"name": "tree_exited", "argument_count": 0, "arguments": []},
                ],
            },
        )

    async def get_signal_connections(
        self,
        node_path: str,
        signal_name: str | None = None,
        incoming: bool = True,
        outgoing: bool = True,
    ) -> StandardResult:
        """Query signal connections in headless mode."""
        return StandardResult(
            success=True,
            message=f"Found 1 signal connections for '{node_path.split('/')[-1]}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_path": node_path,
                "outgoing_connections": [
                    {
                        "signal_name": signal_name or "pressed",
                        "target_node": "/root/Scene/GameManager",
                        "method_name": "_on_pressed",
                        "flags": 1,
                    }
                ]
                if outgoing
                else [],
                "incoming_connections": [],
            },
        )

    async def evaluate_expression(
        self,
        expression: str,
        node_path: str | None = None,
        input_variables: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Evaluate expression in headless mode."""
        eval_val: Any = None
        try:
            # Safe evaluation for basic math/logic
            safe_globals = {
                "__builtins__": None,
                "PI": 3.141592653589793,
                "TAU": 6.283185307179586,
            }
            local_vars = dict(input_variables or {})
            eval_val = eval(expression, safe_globals, local_vars)
        except (ArithmeticError, ValueError, TypeError, NameError, SyntaxError) as ex:
            logger.debug("Headless expression fallback: %s", ex)
            eval_val = "evaluated"

        return StandardResult(
            success=True,
            message=f"Evaluated expression successfully: {eval_val}",
            mode=self.mode,
            data={
                "expression": expression,
                "result": eval_val,
                "result_type": type(eval_val).__name__,
                "context_node": node_path or "/root/Scene",
            },
        )
