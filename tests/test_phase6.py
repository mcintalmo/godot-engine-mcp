"""Unit and headless tests for Godot Phase 6 tools (InputMap, WorldEnvironment, Editor Selection & Focus)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.editor_focus import (
    FocusNodeInput,
    SetEditorSelectionInput,
)
from godot_mcp.models.environment import (
    BackgroundMode,
    ConfigureEnvironmentInput,
    SkyType,
    TonemapMode,
)
from godot_mcp.models.input_map import (
    ConfigureInputActionInput,
    GetInputActionsInput,
    InputEventConfig,
    InputEventType,
)
from godot_mcp.tools.editor_tools import (
    handle_focus_node,
    handle_set_editor_selection,
)
from godot_mcp.tools.environment_tools import handle_configure_environment
from godot_mcp.tools.input_tools import (
    handle_configure_input_action,
    handle_get_input_actions,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase6_tools_mock() -> None:
    """Test Phase 6 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Get Input Actions
    get_in_res = await handle_get_input_actions(client, GetInputActionsInput())
    assert "Input Actions" in get_in_res
    assert "jump" in get_in_res
    assert "fire" in get_in_res

    # 2. Configure Input Action
    cfg_in_res = await handle_configure_input_action(
        client,
        ConfigureInputActionInput(
            action_name="dash",
            deadzone=0.4,
            events=[InputEventConfig(type=InputEventType.KEY, keycode="Shift")],
        ),
    )
    assert "dash" in cfg_in_res

    # 3. Configure Environment
    env_res = await handle_configure_environment(
        client,
        ConfigureEnvironmentInput(
            background_mode=BackgroundMode.SKY,
            sky_type=SkyType.PROCEDURAL,
            tonemap_mode=TonemapMode.ACES,
            glow_enabled=True,
            ssao_enabled=True,
            volumetric_fog_enabled=True,
        ),
    )
    assert "Environment" in env_res
    assert "glow_enabled" in env_res

    # 4. Set Editor Selection
    sel_res = await handle_set_editor_selection(
        client,
        SetEditorSelectionInput(node_paths=["Player", "Enemy"]),
    )
    assert "Selected Nodes" in sel_res
    assert "Player" in sel_res

    # 5. Focus Node
    focus_res = await handle_focus_node(
        client,
        FocusNodeInput(node_path="World/Camera3D", main_screen="3D"),
    )
    assert "Focused Node" in focus_res
    assert "Camera3D" in focus_res


@pytest.mark.asyncio
async def test_phase6_headless_client() -> None:
    """Test Phase 6 tools with HeadlessCLIClient."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # 1. Query input actions headlessly
    get_res = await handle_get_input_actions(client, GetInputActionsInput())
    assert "ui_accept" in get_res

    # 2. Configure environment headlessly
    env_res = await handle_configure_environment(
        client,
        ConfigureEnvironmentInput(
            tonemap_mode=TonemapMode.ACES,
            glow_enabled=True,
            save_path="res://default_env.tres",
        ),
    )
    assert "Environment" in env_res
    assert "glow_enabled" in env_res

    # 3. Selection in headless mode
    sel_res = await handle_set_editor_selection(
        client,
        SetEditorSelectionInput(node_paths=["Root/Mesh"]),
    )
    assert "Selected 1 nodes" in sel_res or "Root/Mesh" in sel_res
