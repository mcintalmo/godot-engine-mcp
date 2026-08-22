"""Unit and headless tests for Godot Phase 10 tools (Resource UIDs, Dependencies & Plugin Management)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.plugin_mgr import (
    GetPluginsInput,
    SetPluginStatusInput,
)
from godot_engine_mcp.models.uid_dep import (
    GetDependenciesInput,
    GetUIDInput,
    ResolveUIDInput,
)
from godot_engine_mcp.tools.plugin_tools import (
    handle_get_plugins,
    handle_set_plugin_status,
)
from godot_engine_mcp.tools.uid_tools import (
    handle_get_dependencies,
    handle_get_uid,
    handle_resolve_uid,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase10_tools_mock() -> None:
    """Test Phase 10 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Get UID
    uid_res = await handle_get_uid(
        client,
        GetUIDInput(path="res://scenes/player.tscn"),
    )
    assert "Resource UID" in uid_res
    assert "uid://mock_uid_123" in uid_res

    # 2. Resolve UID
    res_uid_res = await handle_resolve_uid(
        client,
        ResolveUIDInput(uid="uid://mock_uid_123"),
    )
    assert "Resource UID" in res_uid_res
    assert "res://scenes/main.tscn" in res_uid_res

    # 3. Get Dependencies
    dep_res = await handle_get_dependencies(
        client,
        GetDependenciesInput(path="res://scenes/main.tscn"),
    )
    assert "Dependencies for `res://scenes/main.tscn`" in dep_res
    assert "player.gd" in dep_res

    # 4. Get Plugins
    plug_res = await handle_get_plugins(
        client,
        GetPluginsInput(enabled_only=False),
    )
    assert "Editor Plugins" in plug_res
    assert "godot_mcp" in plug_res

    # 5. Set Plugin Status
    set_plug_res = await handle_set_plugin_status(
        client,
        SetPluginStatusInput(
            plugin_name="godot_mcp",
            enabled=True,
        ),
    )
    assert "Plugin Enabled" in set_plug_res
    assert "godot_mcp" in set_plug_res


@pytest.mark.asyncio
async def test_phase10_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 10 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Get UID headlessly
    uid_res = await handle_get_uid(
        client,
        GetUIDInput(path="res://scripts/enemy.gd"),
    )
    assert "Resource UID" in uid_res

    # 2. Resolve UID headlessly
    res_uid_res = await handle_resolve_uid(
        client,
        ResolveUIDInput(uid="uid://test_uid"),
    )
    assert "Resource UID" in res_uid_res

    # 3. Get Dependencies headlessly
    dep_res = await handle_get_dependencies(
        client,
        GetDependenciesInput(path="res://scenes/level.tscn"),
    )
    assert "Dependencies for `res://scenes/level.tscn`" in dep_res

    # 4. Get Plugins headlessly
    plug_res = await handle_get_plugins(
        client,
        GetPluginsInput(),
    )
    assert "Editor Plugins" in plug_res

    # 5. Set Plugin Status headlessly
    set_plug_res = await handle_set_plugin_status(
        client,
        SetPluginStatusInput(
            plugin_name="terrain_3d",
            enabled=False,
        ),
    )
    assert "Plugin Disabled" in set_plug_res
