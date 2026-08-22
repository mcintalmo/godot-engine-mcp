"""Unit and headless tests for Godot Phase 24 tools (Gameplay AI & State Machine Scaffolding)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.gameplay_scaffolding import (
    CreateDialogueResourceInput,
    DialogueNode,
    DialogueOption,
    ScaffoldStateMachineInput,
)
from godot_engine_mcp.tools.gameplay_scaffolding_tools import (
    handle_create_dialogue_resource,
    handle_scaffold_state_machine,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase24_tools_mock() -> None:
    """Test Phase 24 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Scaffold State Machine
    fsm_res = await handle_scaffold_state_machine(
        client,
        ScaffoldStateMachineInput(
            target_dir="res://scripts/player_fsm",
            machine_name="PlayerStateMachine",
            states=["Idle", "Run", "Jump", "Attack"],
            generate_node_hierarchy=True,
        ),
    )
    assert "Scaffolded State Machine" in fsm_res
    assert "PlayerStateMachine" in fsm_res
    assert "States Generated" in fsm_res
    assert "Node Hierarchy Attached" in fsm_res

    # 2. Create Dialogue Resource
    diag_res = await handle_create_dialogue_resource(
        client,
        CreateDialogueResourceInput(
            resource_path="res://dialogue/elder.json",
            format="json",
            dialogue_nodes=[
                DialogueNode(
                    id="start",
                    speaker="Elder",
                    text="Greetings, brave traveler!",
                    options=[
                        DialogueOption(
                            text="Tell me about the realm", target_id="lore"
                        ),
                        DialogueOption(text="Farewell", target_id="end"),
                    ],
                ),
                DialogueNode(
                    id="lore",
                    speaker="Elder",
                    text="Long ago, the dragons ruled the sky.",
                    options=[DialogueOption(text="Fascinating", target_id="end")],
                ),
            ],
        ),
    )
    assert "Created Dialogue Tree Resource" in diag_res
    assert "elder.json" in diag_res
    assert "Total Dialogue Nodes" in diag_res


@pytest.mark.asyncio
async def test_phase24_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 24 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Scaffold State Machine headlessly
    fsm_res = await handle_scaffold_state_machine(
        client,
        ScaffoldStateMachineInput(
            machine_name="EnemyFSM",
            states=["Patrol", "Chase", "Attack"],
        ),
    )
    assert "Scaffolded State Machine" in fsm_res
    assert "EnemyFSM" in fsm_res

    # 2. Create Dialogue Resource headlessly
    diag_res = await handle_create_dialogue_resource(
        client,
        CreateDialogueResourceInput(
            resource_path="res://dialogue/quest.json",
            dialogue_nodes=[
                DialogueNode(
                    id="start",
                    speaker="QuestGiver",
                    text="Can you slay 5 goblins?",
                ),
            ],
        ),
    )
    assert "Created Dialogue Tree Resource" in diag_res
    assert "quest.json" in diag_res
