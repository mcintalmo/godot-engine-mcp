"""Unit and integration tests for Godot Asset Library tools and package service."""

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from godot_mcp.client.asset_library_service import GodotAssetLibraryService
from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.asset_library import (
    AssetSort,
    GetAssetDetailsInput,
    InstallAssetPackageInput,
    SearchAssetLibraryInput,
)
from godot_mcp.models.common import ResponseFormat
from godot_mcp.tools.asset_library_tools import (
    handle_get_asset_details,
    handle_install_asset_package,
    handle_search_asset_library,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_asset_library_tools_mock() -> None:
    """Test asset library tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Search Asset Library (Markdown)
    search_res = await handle_search_asset_library(
        client,
        SearchAssetLibraryInput(
            query="phantom camera",
            sort_by=AssetSort.UPDATED,
            response_format=ResponseFormat.MARKDOWN,
        ),
    )
    assert "Matching Assets" in search_res
    assert "Phantom Camera" in search_res
    assert "1234" in search_res

    # 2. Search Asset Library (JSON)
    search_json = await handle_search_asset_library(
        client,
        SearchAssetLibraryInput(
            query="phantom camera",
            response_format=ResponseFormat.JSON,
        ),
    )
    data = json.loads(search_json)
    assert data["success"] is True
    assert len(data["data"]["assets"]) == 1

    # 3. Get Asset Details
    detail_res = await handle_get_asset_details(
        client,
        GetAssetDetailsInput(
            asset_id="1234",
            response_format=ResponseFormat.MARKDOWN,
        ),
    )
    assert "Phantom Camera" in detail_res
    assert "https://example.com/phantom_camera.zip" in detail_res

    # 4. Install Asset Package
    install_res = await handle_install_asset_package(
        client,
        InstallAssetPackageInput(
            asset_id="1234",
            target_dir="res://addons/phantom_camera",
            auto_enable_plugin=True,
        ),
    )
    assert "Successfully installed" in install_res
    assert "phantom_camera" in install_res


@pytest.mark.asyncio
async def test_asset_library_service_download_and_extract(tmp_path: Path) -> None:
    """Test downloading and extracting an in-memory zip archive with plugin registration."""
    service = GodotAssetLibraryService()

    # Create dummy project.godot
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    project_godot = project_dir / "project.godot"
    project_godot.write_text('[application]\nconfig/name="TestApp"\n', encoding="utf-8")

    # Create dummy in-memory zip archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr(
            "dummy_plugin/plugin.cfg",
            '[plugin]\nname="Dummy"\ndescription="Dummy Plugin"\nauthor="Test"\nversion="1.0"\nscript="plugin.gd"\n',
        )
        zf.writestr("dummy_plugin/plugin.gd", "extends EditorPlugin\n")
        zf.writestr("dummy_plugin/data.txt", "hello world")
    zip_bytes = zip_buffer.getvalue()

    # Mock httpx GET to return the zip bytes
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.content = zip_bytes
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        target_dir = project_dir / "addons"
        res = await service.download_and_extract(
            download_url="https://example.com/dummy.zip",
            target_dir=target_dir,
            project_root=project_dir,
            auto_enable_plugin=True,
        )

        assert res["files_extracted"] == 3
        assert (target_dir / "dummy_plugin" / "plugin.cfg").is_file()
        assert (target_dir / "dummy_plugin" / "data.txt").is_file()
        assert len(res["enabled_plugins"]) == 1
        assert "res://addons/dummy_plugin/plugin.cfg" in res["enabled_plugins"]

        # Verify project.godot was updated with [editor_plugins]
        content = project_godot.read_text(encoding="utf-8")
        assert "[editor_plugins]" in content
        assert "res://addons/dummy_plugin/plugin.cfg" in content


@pytest.mark.asyncio
async def test_asset_library_service_search_and_details() -> None:
    """Test REST search and details formatting with mocked API responses."""
    service = GodotAssetLibraryService()

    fake_search_payload = {
        "result": [
            {
                "asset_id": "42",
                "title": "GUT - Godot Unit Test",
                "author": "bitwes",
                "author_id": "100",
                "version": "9.3.0",
                "godot_version": "4.3",
                "category": "Scripts",
                "cost": "MIT",
                "download_url": "https://example.com/gut.zip",
                "description": "Unit testing framework for Godot Engine.",
            }
        ],
        "total_items": 1,
        "page": 0,
        "pages": 1,
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.json = lambda: fake_search_payload
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        search_data = await service.search_assets(query="GUT")
        assert search_data["total_items"] == 1
        assert len(search_data["assets"]) == 1
        assert search_data["assets"][0]["title"] == "GUT - Godot Unit Test"

    fake_detail_payload = {
        "asset_id": "42",
        "title": "GUT - Godot Unit Test",
        "author": "bitwes",
        "version_string": "9.3.0",
        "godot_version": "4.3",
        "category": "Scripts",
        "cost": "MIT",
        "download_url": "https://example.com/gut.zip",
        "browse_url": "https://godotengine.org/asset-library/asset/42",
        "description": "Full unit test suite runner.",
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.json = lambda: fake_detail_payload
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        details = await service.get_asset_details("42")
        assert details["title"] == "GUT - Godot Unit Test"
        assert details["download_url"] == "https://example.com/gut.zip"


@pytest.mark.asyncio
async def test_headless_client_asset_library() -> None:
    """Test HeadlessCLIClient asset library methods."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # Search with mocked network
    with patch(
        "godot_mcp.client.asset_library_service.GodotAssetLibraryService.search_assets"
    ) as mock_search:
        mock_search.return_value = {
            "query": "jolt",
            "category": "all",
            "godot_version": "4.x",
            "total_items": 1,
            "assets": [
                {
                    "asset_id": "99",
                    "title": "Godot Jolt",
                    "author": "mihe",
                    "version": "0.13.0",
                    "godot_version": "4.3",
                    "category": "3D Tools",
                    "cost": "MIT",
                    "download_url": "https://example.com/godot_jolt.zip",
                }
            ],
        }
        res = await client.search_asset_library("jolt")
        assert res.success is True
        assert "Found 1 assets" in res.message
        assert len(res.data["assets"]) == 1
