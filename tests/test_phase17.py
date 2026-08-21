"""Unit and headless tests for Godot Phase 17 tools (Live Script Lifecycle, Hot-Reload & Exported Property Reflection)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.script_lifecycle import (
    AttachScriptInput,
    GetNodeScriptInfoInput,
    ReloadScriptsInput,
)
from godot_mcp.tools.script_lifecycle_tools import (
    handle_attach_script,
    handle_get_node_script_info,
    handle_reload_scripts,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase17_tools_mock() -> None:
    """Test Phase 17 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Attach script with initial properties
    attach_res = await handle_attach_script(
        client,
        AttachScriptInput(
            node_path="Player",
            script_path="res://scripts/player.gd",
            initial_properties={"speed": 400.0, "health": 100},
        ),
    )
    assert "Script Attached to Node" in attach_res
    assert "res://scripts/player.gd" in attach_res
    assert "speed" in attach_res

    # 2. Detach script
    detach_res = await handle_attach_script(
        client,
        AttachScriptInput(
            node_path="Player",
            script_path=None,
        ),
    )
    assert "Detached script" in detach_res

    # 3. Reload scripts
    reload_res = await handle_reload_scripts(
        client,
        ReloadScriptsInput(script_paths=["res://scripts/player.gd"]),
    )
    assert "Reloaded 1 Script Resources" in reload_res
    assert "res://scripts/player.gd" in reload_res

    # 4. Get node script info
    info_res = await handle_get_node_script_info(
        client,
        GetNodeScriptInfoInput(node_path="Player"),
    )
    assert "Attached Script Info" in info_res
    assert "CharacterBody3D" in info_res
    assert "take_damage" in info_res
    assert "health_changed" in info_res
    assert "speed" in info_res


@pytest.mark.asyncio
async def test_phase17_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 17 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Attach script headlessly
    attach_res = await handle_attach_script(
        client,
        AttachScriptInput(
            node_path="Enemy",
            script_path="res://scripts/enemy.gd",
        ),
    )
    assert "Script Attached to Node" in attach_res
    assert "res://scripts/enemy.gd" in attach_res

    # 2. Reload scripts headlessly
    reload_res = await handle_reload_scripts(
        client,
        ReloadScriptsInput(),
    )
    assert "Reloaded 1 Script Resources" in reload_res

    # 3. Get node script info headlessly
    info_res = await handle_get_node_script_info(
        client,
        GetNodeScriptInfoInput(node_path="Enemy"),
    )
    assert "Attached Script Info" in info_res
    assert "speed" in info_res
