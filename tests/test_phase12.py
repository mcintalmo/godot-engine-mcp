"""Unit and headless tests for Godot Phase 12 tools (Editor Undo/Redo & Multi-Node Selection Management)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.editor_history import RedoInput, UndoInput
from godot_engine_mcp.models.editor_selection import (
    GetSelectedNodesInput,
    SetSelectedNodesInput,
)
from godot_engine_mcp.tools.editor_history_tools import (
    handle_redo,
    handle_undo,
)
from godot_engine_mcp.tools.editor_selection_tools import (
    handle_get_selected_nodes,
    handle_set_selected_nodes,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase12_tools_mock() -> None:
    """Test Phase 12 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Undo action
    undo_res = await handle_undo(client, UndoInput())
    assert "Action History" in undo_res
    assert "Move Node" in undo_res

    # 2. Redo action
    redo_res = await handle_redo(client, RedoInput())
    assert "Action History" in redo_res
    assert "Can Undo" in redo_res

    # 3. Get selected nodes
    sel_res = await handle_get_selected_nodes(
        client, GetSelectedNodesInput(include_properties=True)
    )
    assert "Editor Selection" in sel_res
    assert "Player" in sel_res
    assert "Camera3D" in sel_res

    # 4. Set selected nodes
    set_sel_res = await handle_set_selected_nodes(
        client,
        SetSelectedNodesInput(
            node_paths=["Main/Player", "Main/Player/Camera3D"],
            clear_previous=True,
            inspect_primary=True,
        ),
    )
    assert "Editor Selection" in set_sel_res
    assert "Main/Player" in set_sel_res
    assert "Inspected in Editor" in set_sel_res


@pytest.mark.asyncio
async def test_phase12_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 12 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Undo action headlessly
    undo_res = await handle_undo(client, UndoInput())
    assert "Action History" in undo_res

    # 2. Redo action headlessly
    redo_res = await handle_redo(client, RedoInput())
    assert "Action History" in redo_res

    # 3. Get selected nodes headlessly
    sel_res = await handle_get_selected_nodes(client, GetSelectedNodesInput())
    assert "Editor Selection" in sel_res

    # 4. Set selected nodes headlessly
    set_sel_res = await handle_set_selected_nodes(
        client,
        SetSelectedNodesInput(node_paths=["Player/Sprite2D"]),
    )
    assert "Editor Selection" in set_sel_res
    assert "Sprite2D" in set_sel_res
