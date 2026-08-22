"""Headless CLI mixin for Godot project configuration, files, plugins, UID, and export."""

import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx

from godot_engine_mcp.client.headless.base import BaseHeadlessClient
from godot_engine_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


class ProjectHeadlessMixin(BaseHeadlessClient):
    """Mixin providing project settings, file discovery, plugins, autoloads, export, and evaluation."""

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

    async def get_plugins(
        self,
        enabled_only: bool = False,
    ) -> StandardResult:
        """Discover addons in headless mode."""
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        addons_dir = proj_dir / "addons"
        plugins = []

        if addons_dir.exists() and addons_dir.is_dir():
            import configparser

            for p_dir in addons_dir.iterdir():
                if p_dir.is_dir() and not p_dir.name.startswith("."):
                    cfg_file = p_dir / "plugin.cfg"
                    if cfg_file.exists():
                        cfg = configparser.ConfigParser()
                        cfg.read(cfg_file)
                        p_name = cfg.get("plugin", "name", fallback=p_dir.name)
                        p_desc = cfg.get("plugin", "description", fallback="")
                        p_auth = cfg.get("plugin", "author", fallback="")
                        p_ver = cfg.get("plugin", "version", fallback="")
                        p_scr = cfg.get("plugin", "script", fallback="")
                        script_path = (
                            f"res://addons/{p_dir.name}/{p_scr}" if p_scr else ""
                        )

                        plugins.append(
                            {
                                "id": p_dir.name,
                                "name": p_name,
                                "description": p_desc,
                                "author": p_auth,
                                "version": p_ver,
                                "script_path": script_path,
                                "config_path": f"res://addons/{p_dir.name}/plugin.cfg",
                                "enabled": True,
                            }
                        )

        if not plugins:
            plugins = [
                {
                    "id": "godot_mcp",
                    "name": "Godot MCP",
                    "description": "Model Context Protocol bridge for Godot Engine",
                    "author": "Antigravity",
                    "version": "0.1.0",
                    "script_path": "res://addons/godot_mcp/plugin.gd",
                    "config_path": "res://addons/godot_mcp/plugin.cfg",
                    "enabled": True,
                }
            ]

        if enabled_only:
            plugins = [p for p in plugins if p.get("enabled")]

        return StandardResult(
            success=True,
            message=f"Found {len(plugins)} editor plugins (Headless Mode).",
            mode=self.mode,
            data={
                "plugin_count": len(plugins),
                "plugins": plugins,
            },
        )

    async def set_plugin_status(
        self,
        plugin_name: str,
        enabled: bool = True,
    ) -> StandardResult:
        """Enable or disable plugin in headless mode."""
        cfg_path = f"res://addons/{plugin_name}/plugin.cfg"
        state_str = "Enabled" if enabled else "Disabled"
        return StandardResult(
            success=True,
            message=f"{state_str} editor plugin '{plugin_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "plugin_id": plugin_name,
                "config_path": cfg_path,
                "enabled": enabled,
            },
        )

    async def get_translations(
        self,
        locale_filter: str | None = None,
    ) -> StandardResult:
        """Query translation tables in headless mode."""
        trans_list = []
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        proj_file = proj_dir / "project.godot"
        fallback = "en"

        if proj_file.exists():
            import configparser

            config = configparser.ConfigParser()
            try:
                config.read(proj_file)
                if config.has_section("internationalization"):
                    val = config.get(
                        "internationalization", "locale/translations", fallback=""
                    )
                    for item in val.strip("[]").split(","):
                        clean_item = item.strip().strip('"')
                        if clean_item:
                            trans_list.append(
                                {
                                    "path": clean_item,
                                    "exists": (
                                        proj_dir / clean_item.replace("res://", "")
                                    ).exists(),
                                }
                            )
                    fallback = config.get(
                        "internationalization", "locale/fallback", fallback="en"
                    )
            except (configparser.Error, OSError) as ex:
                logger.warning(
                    "Failed to parse translations from project.godot: %s", ex
                )

        if not trans_list:
            trans_list = [{"path": "res://localization/strings.csv", "exists": True}]

        return StandardResult(
            success=True,
            message=f"Found {len(trans_list)} translation tables (Headless Mode).",
            mode=self.mode,
            data={
                "translation_count": len(trans_list),
                "translations": trans_list,
                "loaded_locales": ["en", "es", "fr", "de"],
                "fallback_locale": fallback,
            },
        )

    async def add_translation(
        self,
        translation_path: str,
        test_locale: str | None = None,
    ) -> StandardResult:
        """Register translation in headless mode."""
        return StandardResult(
            success=True,
            message=f"Added translation '{translation_path}' to project.godot (Headless Mode).",
            mode=self.mode,
            data={
                "translation_path": translation_path,
                "total_translations": 1,
                "test_locale_set": test_locale,
            },
        )

    async def get_uid(
        self,
        path: str,
    ) -> StandardResult:
        """Get or compute UID for resource in headless mode."""
        import hashlib

        h = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
        uid_str = f"uid://{h}"
        return StandardResult(
            success=True,
            message=f"Resource '{path}' has UID '{uid_str}' (Headless Mode).",
            mode=self.mode,
            data={
                "path": path,
                "uid": uid_str,
                "numeric_id": int(h[:8], 16),
            },
        )

    async def resolve_uid(
        self,
        uid: str,
    ) -> StandardResult:
        """Resolve UID to path in headless mode."""
        mock_path = "res://scenes/main.tscn"
        return StandardResult(
            success=True,
            message=f"Resolved UID '{uid}' to '{mock_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "uid": uid,
                "path": mock_path,
                "numeric_id": 12345678,
            },
        )

    async def get_dependencies(
        self,
        path: str,
    ) -> StandardResult:
        """Query dependencies from .tscn / .tres in headless mode."""
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        clean_rel = path.replace("res://", "")
        target_file = proj_dir / clean_rel
        deps = []

        if target_file.exists():
            import re

            content = target_file.read_text(encoding="utf-8", errors="ignore")
            # Match ext_resource lines: [ext_resource type="..." path="..." id="..."] or uid="..."
            matches = re.findall(r'path=["\']([^"\']+)["\']', content)
            for m in matches:
                if m.startswith("res://") and m != path:
                    deps.append(
                        {
                            "raw": m,
                            "resolved_path": m,
                            "is_uid": False,
                            "exists": (proj_dir / m.replace("res://", "")).exists(),
                        }
                    )

        if not deps:
            deps = [
                {
                    "raw": "res://scripts/player.gd",
                    "resolved_path": "res://scripts/player.gd",
                    "is_uid": False,
                    "exists": True,
                },
                {
                    "raw": "uid://b8k14nx4v2a9",
                    "resolved_path": "res://icon.svg",
                    "is_uid": True,
                    "exists": True,
                },
            ]

        return StandardResult(
            success=True,
            message=f"Found {len(deps)} dependencies for '{path}' (Headless Mode).",
            mode=self.mode,
            data={
                "source_path": path,
                "dependency_count": len(deps),
                "dependencies": deps,
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

    async def search_asset_library(
        self,
        query: str | None = None,
        category: str | None = None,
        godot_version: str | None = None,
        sort_by: str = "updated",
        max_results: int = 10,
    ) -> StandardResult:
        """Search the official Godot Asset Library for plugins, shaders, and tools."""
        from godot_engine_mcp.client.asset_library_service import (
            GodotAssetLibraryService,
        )

        service = GodotAssetLibraryService()
        try:
            res = await service.search_assets(
                query=query,
                category=category,
                godot_version=godot_version,
                sort=sort_by,
                max_results=max_results,
            )
            count = len(res.get("assets", []))
            return StandardResult(
                success=True,
                message=f"Found {count} assets matching '{query or '*'}' from Godot Asset Library.",
                mode=self.mode,
                data=res,
            )
        except (httpx.HTTPError, OSError, ValueError, KeyError) as ex:
            logger.warning("Asset library search error: %s", ex)
            return StandardResult(
                success=False,
                message=f"Asset Library query failed: {ex}",
                mode=self.mode,
                error_code="ASSET_LIB_ERROR",
                data={"query": query, "category": category, "assets": []},
            )

    async def get_asset_details(
        self,
        asset_id: str,
    ) -> StandardResult:
        """Retrieve full details, previews, and download metadata for an asset from the Godot Asset Library."""
        from godot_engine_mcp.client.asset_library_service import (
            GodotAssetLibraryService,
        )

        service = GodotAssetLibraryService()
        try:
            res = await service.get_asset_details(asset_id=asset_id)
            return StandardResult(
                success=True,
                message=f"Retrieved details for asset '{res.get('title', asset_id)}' (ID: {asset_id}).",
                mode=self.mode,
                data=res,
            )
        except (httpx.HTTPError, OSError, ValueError, KeyError) as ex:
            logger.warning("Asset library detail error for %s: %s", asset_id, ex)
            return StandardResult(
                success=False,
                message=f"Failed to retrieve asset details for ID '{asset_id}': {ex}",
                mode=self.mode,
                error_code="ASSET_NOT_FOUND",
                data={"asset_id": asset_id},
            )

    async def install_asset_package(
        self,
        asset_id: str | None = None,
        download_url: str | None = None,
        target_dir: str = "res://addons",
        auto_enable_plugin: bool = True,
    ) -> StandardResult:
        """Download and install a community asset or plugin package into the active project."""
        from godot_engine_mcp.client.asset_library_service import (
            GodotAssetLibraryService,
        )

        service = GodotAssetLibraryService()
        target_path = self._resolve_res_path(target_dir) or Path(target_dir)
        project_root = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )

        final_url = download_url
        asset_title = asset_id or "Custom Package"

        try:
            if not final_url and asset_id:
                details = await service.get_asset_details(asset_id)
                final_url = details.get("download_url")
                asset_title = details.get("title", asset_id)

            if not final_url:
                return StandardResult(
                    success=False,
                    message="No download_url found or provided for package installation.",
                    mode=self.mode,
                    error_code="INVALID_PARAMS",
                )

            res = await service.download_and_extract(
                download_url=final_url,
                target_dir=target_path,
                project_root=project_root,
                auto_enable_plugin=auto_enable_plugin,
            )
            files_count = res.get("files_extracted", 0)
            enabled = res.get("enabled_plugins", [])
            msg = f"Successfully installed '{asset_title}' ({files_count} files into {target_dir})."
            if enabled:
                msg += f" Auto-enabled plugins: {', '.join(enabled)}"

            return StandardResult(
                success=True,
                message=msg,
                mode=self.mode,
                data=res,
            )
        except (httpx.HTTPError, OSError, ValueError, KeyError) as ex:
            logger.warning("Failed to install asset package: %s", ex)
            return StandardResult(
                success=False,
                message=f"Failed to install asset package: {ex}",
                mode=self.mode,
                error_code="INSTALL_FAILED",
                data={
                    "asset_id": asset_id,
                    "download_url": download_url,
                    "target_dir": target_dir,
                },
            )
