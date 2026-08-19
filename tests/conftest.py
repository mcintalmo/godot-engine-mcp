"""Pytest fixtures for Godot MCP test suite."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from godot_mcp.config import GodotConfig


@pytest.fixture
def temp_project_dir() -> Generator[Path]:
    """Provide a temporary directory structured as a Godot project."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        proj_path = Path(tmp_dir)
        # Create a sample project.godot
        project_godot = proj_path / "project.godot"
        project_godot.write_text(
            """config_version=5

[application]
config/name="Test Godot Project"
run/main_scene="res://main.tscn"

[display]
window/size/viewport_width=1280
window/size/viewport_height=720
""",
            encoding="utf-8",
        )

        # Create dummy scene and script files
        scenes_dir = proj_path / "scenes"
        scenes_dir.mkdir()
        (scenes_dir / "main.tscn").write_text(
            '[gd_scene format=3 uid="uid://test1234"]\n', encoding="utf-8"
        )

        scripts_dir = proj_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "player.gd").write_text(
            "extends Node2D\n\nfunc _ready() -> void:\n\tpass\n", encoding="utf-8"
        )

        yield proj_path


@pytest.fixture
def mock_config(temp_project_dir: Path) -> GodotConfig:
    """Provide a GodotConfig pointing to the temp project dir."""
    return GodotConfig(
        executable_path=None,
        project_path=str(temp_project_dir),
        bridge_host="127.0.0.1",
        bridge_port=3118,
        request_timeout=5.0,
        auto_fallback_headless=True,
    )
