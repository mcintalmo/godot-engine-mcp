"""Service for querying the official Godot Asset Library and installing packages."""

import asyncio
import io
import logging
import shutil
import zipfile
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

ASSET_LIB_BASE_URL = "https://godotengine.org/asset-library/api"


class GodotAssetLibraryService:
    """Async client interacting with the official Godot Asset Library REST API."""

    def __init__(self, base_url: str = ASSET_LIB_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    async def search_assets(
        self,
        query: str | None = None,
        category: str | None = None,
        godot_version: str | None = None,
        sort: str = "updated",
        max_results: int = 10,
        page: int = 0,
    ) -> dict[str, Any]:
        """Search the Godot Asset Library for plugins, shaders, templates, and tools."""
        params: dict[str, Any] = {
            "sort": sort,
            "max_results": max_results,
            "page": page,
        }
        if query:
            params["filter"] = query
        if category and category != "any":
            params["category"] = category
        if godot_version:
            params["godot_version"] = godot_version

        url = f"{self.base_url}/asset"
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        items: list[dict[str, Any]] = []
        raw_results = data.get("result", [])
        if isinstance(raw_results, list):
            for r in raw_results:
                items.append(
                    {
                        "asset_id": str(r.get("asset_id", "")),
                        "title": r.get("title", ""),
                        "author": r.get("author", ""),
                        "author_id": str(r.get("author_id", "")),
                        "version": r.get("version", r.get("version_string", "")),
                        "godot_version": r.get("godot_version", ""),
                        "category": r.get("category", ""),
                        "cost": r.get("cost", ""),
                        "support_level": r.get("support_level", "community"),
                        "download_url": r.get("download_url", ""),
                        "icon_url": r.get("icon_url"),
                        "description": r.get("description", ""),
                    }
                )

        return {
            "query": query or "",
            "category": category or "all",
            "godot_version": godot_version or "all",
            "total_items": data.get("total_items", len(items)),
            "page": data.get("page", 0),
            "pages": data.get("pages", 1),
            "assets": items,
        }

    async def get_asset_details(self, asset_id: str) -> dict[str, Any]:
        """Fetch detailed metadata for a specific asset by ID."""
        url = f"{self.base_url}/asset/{asset_id}"
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        return {
            "asset_id": str(data.get("asset_id", asset_id)),
            "title": data.get("title", ""),
            "author": data.get("author", ""),
            "author_id": str(data.get("author_id", "")),
            "version": data.get("version", data.get("version_string", "")),
            "godot_version": data.get("godot_version", ""),
            "category": data.get("category", ""),
            "cost": data.get("cost", ""),
            "support_level": data.get("support_level", "community"),
            "download_url": data.get("download_url", ""),
            "browse_url": data.get("browse_url", ""),
            "issues_url": data.get("issues_url", ""),
            "icon_url": data.get("icon_url"),
            "description": data.get("description", ""),
            "previews": data.get("previews", []),
        }

    def _extract_zip_sync(
        self,
        zip_bytes: bytes,
        target_dir: Path,
        project_root: Path | None,
        auto_enable_plugin: bool,
    ) -> dict[str, Any]:
        """Synchronously and safely extract zip bytes into target directory."""
        target_dir.mkdir(parents=True, exist_ok=True)
        extracted_files: list[str] = []
        discovered_plugins: list[str] = []

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            # Check for GitHub / GitLab repository release wrapper folder (e.g. repo-main/, repo-1.0.0/)
            namelist = zf.namelist()
            prefix = ""
            if namelist and all("/" in n for n in namelist if not n.endswith("/")):
                first_parts = {n.split("/")[0] for n in namelist if "/" in n}
                if len(first_parts) == 1:
                    first_part = next(iter(first_parts))
                    import re

                    if re.search(r"-(?:main|master|v?\d[\w\.]*)$", first_part):
                        prefix = f"{first_part}/"

            for member in zf.infolist():
                filename = member.filename
                if prefix and filename.startswith(prefix):
                    rel_name = filename[len(prefix) :]
                else:
                    rel_name = filename

                if not rel_name or rel_name.endswith("/"):
                    continue

                # Safety check against path traversal (Zip Slip)
                dest_path = (target_dir / rel_name).resolve()
                if not str(dest_path).startswith(str(target_dir.resolve())):
                    logger.warning("Skipping unsafe zip member: %s", filename)
                    continue

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)

                extracted_files.append(rel_name)

                # Check if this file is a Godot plugin configuration
                if dest_path.name == "plugin.cfg":
                    discovered_plugins.append(str(dest_path))

        # Auto-enable plugin in project.godot if found
        enabled_plugins: list[str] = []
        if auto_enable_plugin and project_root and discovered_plugins:
            project_godot = project_root / "project.godot"
            if project_godot.is_file():
                for pcfg in discovered_plugins:
                    pcfg_path = Path(pcfg)
                    try:
                        rel_to_proj = pcfg_path.relative_to(project_root)
                        res_plugin_path = f"res://{rel_to_proj.as_posix()}"
                        self._enable_plugin_in_project_godot(
                            project_godot, res_plugin_path
                        )
                        enabled_plugins.append(res_plugin_path)
                    except (OSError, ValueError) as e:
                        logger.warning("Failed to auto-enable plugin %s: %s", pcfg, e)

        return {
            "target_dir": str(target_dir),
            "files_extracted": len(extracted_files),
            "discovered_plugins": discovered_plugins,
            "enabled_plugins": enabled_plugins,
        }

    async def download_and_extract(
        self,
        download_url: str,
        target_dir: Path,
        project_root: Path | None = None,
        auto_enable_plugin: bool = True,
    ) -> dict[str, Any]:
        """Download a ZIP archive and safely extract it into target directory."""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(download_url)
            resp.raise_for_status()
            zip_bytes = resp.content

        res = await asyncio.to_thread(
            self._extract_zip_sync,
            zip_bytes,
            target_dir,
            project_root,
            auto_enable_plugin,
        )
        res["download_url"] = download_url
        return res

    def _enable_plugin_in_project_godot(
        self, project_godot_path: Path, plugin_res_path: str
    ) -> None:
        """Register an enabled plugin in project.godot under [editor_plugins]."""
        content = project_godot_path.read_text(encoding="utf-8")
        if "[editor_plugins]" not in content:
            content += f'\n[editor_plugins]\n\nenabled=PackedStringArray("{plugin_res_path}")\n'
            project_godot_path.write_text(content, encoding="utf-8")
            return

        if plugin_res_path in content:
            return

        lines = content.splitlines()
        new_lines: list[str] = []
        for line in lines:
            if line.startswith("enabled=PackedStringArray("):
                inside = line.split("PackedStringArray(")[1].rstrip(")")
                items = [
                    it.strip().strip('"') for it in inside.split(",") if it.strip()
                ]
                if plugin_res_path not in items:
                    items.append(plugin_res_path)
                formatted_items = ", ".join(f'"{it}"' for it in items)
                new_lines.append(f"enabled=PackedStringArray({formatted_items})")
            else:
                new_lines.append(line)

        project_godot_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
