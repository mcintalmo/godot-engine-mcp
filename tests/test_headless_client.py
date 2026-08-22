"""Unit tests for HeadlessCLIClient operations."""

from pathlib import Path

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig


@pytest.mark.asyncio
async def test_get_project_settings(mock_config: GodotConfig) -> None:
    """Test reading settings from project.godot."""
    client = HeadlessCLIClient(mock_config)
    res = await client.get_project_settings()

    assert res.success is True
    assert "settings" in res.data
    settings = res.data["settings"]
    assert settings.get("application/config/name") == "Test Godot Project"
    assert settings.get("display/window/size/viewport_width") == "1280"


@pytest.mark.asyncio
async def test_set_project_setting(mock_config: GodotConfig) -> None:
    """Test updating a setting in project.godot."""
    client = HeadlessCLIClient(mock_config)
    res = await client.set_project_setting("application/config/name", "New Game Title")

    assert res.success is True

    # Re-read to confirm file was written
    read_res = await client.get_project_settings(section="application")
    assert read_res.data["settings"].get("application/config/name") == "New Game Title"


@pytest.mark.asyncio
async def test_list_project_files(mock_config: GodotConfig) -> None:
    """Test listing files in Godot project directory."""
    client = HeadlessCLIClient(mock_config)
    res = await client.list_project_files(directory="res://")

    assert res.success is True
    files = res.data["files"]
    paths = [f["path"] for f in files]

    assert "res://scenes/main.tscn" in paths
    assert "res://scripts/player.gd" in paths


@pytest.mark.asyncio
async def test_create_script(mock_config: GodotConfig) -> None:
    """Test creating a new GDScript file."""
    client = HeadlessCLIClient(mock_config)
    script_content = "extends CharacterBody2D\n\nfunc _physics_process(delta: float) -> void:\n\tpass\n"

    res = await client.create_script(
        path="res://scripts/enemy.gd",
        content=script_content,
        inherits="CharacterBody2D",
    )

    assert res.success is True
    assert mock_config.project_path is not None
    created_file = Path(mock_config.project_path) / "scripts" / "enemy.gd"
    assert created_file.exists()
    assert created_file.read_text(encoding="utf-8") == script_content
