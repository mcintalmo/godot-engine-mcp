"""Unit and headless tests for Godot Phase 15 tools (Editor Layouts, Multi-Window Dock State & Workspace Inspector)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.editor_layout import (
    GetEditorLayoutInput,
    SetEditorLayoutInput,
)
from godot_mcp.tools.editor_layout_tools import (
    handle_get_editor_layout,
    handle_set_editor_layout,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase15_tools_mock() -> None:
    """Test Phase 15 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Get editor layout
    layout_res = await handle_get_editor_layout(
        client,
        GetEditorLayoutInput(include_open_scenes=True),
    )
    assert "Godot Editor Workspace Layout" in layout_res
    assert "1.25x" in layout_res
    assert "res://scenes/main.tscn" in layout_res

    # 2. Set editor layout
    set_layout_res = await handle_set_editor_layout(
        client,
        SetEditorLayoutInput(
            main_screen="3D",
            distraction_free_mode=True,
            active_scene_path="res://scenes/level.tscn",
        ),
    )
    assert "Updated Editor Workspace Layout" in set_layout_res
    assert "Main Screen: 3D" in set_layout_res
    assert "Distraction-Free: True" in set_layout_res
    assert "Opened Scene: res://scenes/level.tscn" in set_layout_res


@pytest.mark.asyncio
async def test_phase15_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 15 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Get editor layout headlessly
    layout_res = await handle_get_editor_layout(client, GetEditorLayoutInput())
    assert "Godot Editor Workspace Layout" in layout_res
    assert "UI Scale" in layout_res

    # 2. Set editor layout headlessly
    set_layout_res = await handle_set_editor_layout(
        client,
        SetEditorLayoutInput(main_screen="2D"),
    )
    assert "Updated Editor Workspace Layout" in set_layout_res
    assert "Main Screen: 2D" in set_layout_res
