"""Unit and headless tests for Godot Phase 20 tools ('Playwright for Godot' Autonomous E2E Testing & UI Automation Engine)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.e2e_automation import (
    AssertNodeStateInput,
    FindElementsInput,
    InteractNodeInput,
    WaitForConditionInput,
)
from godot_engine_mcp.tools.e2e_automation_tools import (
    handle_assert_node_state,
    handle_find_elements,
    handle_interact_node,
    handle_wait_for_condition,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase20_tools_mock() -> None:
    """Test Phase 20 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Find Elements
    find_res = await handle_find_elements(
        client,
        FindElementsInput(
            selector_type="text",
            query="Start Game",
        ),
    )
    assert "Matched 1 Elements" in find_res
    assert "StartButton" in find_res
    assert "Start Game" in find_res

    # 2. Interact Node (Click)
    click_res = await handle_interact_node(
        client,
        InteractNodeInput(
            node_path="UI/StartButton",
            action="click",
        ),
    )
    assert "Node Interaction Completed" in click_res
    assert "StartButton" in click_res
    assert "click" in click_res

    # 3. Wait For Condition
    wait_res = await handle_wait_for_condition(
        client,
        WaitForConditionInput(
            condition_type="node_exists",
            node_path="UI/GameOverScreen",
            timeout_ms=3000,
        ),
    )
    assert "Wait Condition Evaluation" in wait_res
    assert "node_exists" in wait_res
    assert "Satisfied" in wait_res

    # 4. Assert Node State
    assert_res = await handle_assert_node_state(
        client,
        AssertNodeStateInput(
            node_path="UI/ScoreLabel",
            assertions={
                "visible": True,
                "text": "Score: 100",
            },
        ),
    )
    assert "Node State Assertions [PASSED]" in assert_res
    assert "ScoreLabel" in assert_res
    assert "Score: 100" in assert_res


@pytest.mark.asyncio
async def test_phase20_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 20 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Find Elements headlessly
    find_res = await handle_find_elements(
        client,
        FindElementsInput(
            selector_type="role",
            query="Button",
        ),
    )
    assert "Matched 1 Elements" in find_res

    # 2. Interact Node (Type Text) headlessly
    type_res = await handle_interact_node(
        client,
        InteractNodeInput(
            node_path="UI/PlayerNameInput",
            action="type_text",
            text="GodotHero",
        ),
    )
    assert "Node Interaction Completed" in type_res
    assert "type_text" in type_res

    # 3. Wait For Condition headlessly
    wait_res = await handle_wait_for_condition(
        client,
        WaitForConditionInput(
            condition_type="property_equals",
            node_path="UI/PlayerNameInput",
            property_name="text",
            expected_value="GodotHero",
        ),
    )
    assert "Wait Condition Evaluation" in wait_res

    # 4. Assert Node State headlessly
    assert_res = await handle_assert_node_state(
        client,
        AssertNodeStateInput(
            node_path="UI/PlayerNameInput",
            assertions={
                "visible": True,
            },
        ),
    )
    assert "Node State Assertions [PASSED]" in assert_res
