"""Unit and headless tests for Godot Phase 16 tools (Scene Hierarchy Mutation & Packed Scene Instantiation)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.scene_hierarchy import (
    DuplicateNodeInput,
    ReparentNodeInput,
    SetNodeOwnerInput,
)
from godot_engine_mcp.tools.scene_hierarchy_tools import (
    handle_duplicate_node,
    handle_reparent_node,
    handle_set_node_owner,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase16_tools_mock() -> None:
    """Test Phase 16 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Reparent node
    reparent_res = await handle_reparent_node(
        client,
        ReparentNodeInput(
            node_path="Player/Weapon",
            new_parent_path="Player/Hands",
            keep_global_transform=True,
            new_index=0,
        ),
    )
    assert "Reparented Node" in reparent_res
    assert "Player/Hands" in reparent_res
    assert "Global Transform Preserved" in reparent_res

    # 2. Duplicate node
    dup_res = await handle_duplicate_node(
        client,
        DuplicateNodeInput(
            node_path="World/Coin",
            new_name="Coin2",
            duplicate_groups=True,
            duplicate_scripts=True,
        ),
    )
    assert "Duplicated Node" in dup_res
    assert "Coin2" in dup_res
    assert "World" in dup_res

    # 3. Set node owner
    owner_res = await handle_set_node_owner(
        client,
        SetNodeOwnerInput(
            node_path="Player/Weapon",
            owner_node_path="Player",
            recursive=True,
        ),
    )
    assert "Node Owner Updated" in owner_res
    assert "Player/Weapon" in owner_res
    assert "Recursive: True" in owner_res


@pytest.mark.asyncio
async def test_phase16_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 16 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Reparent node headlessly
    reparent_res = await handle_reparent_node(
        client,
        ReparentNodeInput(
            node_path="Enemy/Sword",
            new_parent_path="Enemy/RightHand",
        ),
    )
    assert "Reparented Node" in reparent_res
    assert "Enemy/RightHand" in reparent_res

    # 2. Duplicate node headlessly
    dup_res = await handle_duplicate_node(
        client,
        DuplicateNodeInput(
            node_path="UI/Button",
            new_name="ButtonNext",
        ),
    )
    assert "Duplicated Node" in dup_res
    assert "ButtonNext" in dup_res

    # 3. Set node owner headlessly
    owner_res = await handle_set_node_owner(
        client,
        SetNodeOwnerInput(
            node_path="UI/ButtonNext",
            owner_node_path="UI",
        ),
    )
    assert "Node Owner Updated" in owner_res
    assert "UI/ButtonNext" in owner_res
