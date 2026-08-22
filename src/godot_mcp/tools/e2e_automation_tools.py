"""Tool handlers for 'Playwright for Godot' Autonomous E2E Testing & UI Automation Engine."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.e2e_automation import (
    AssertNodeStateInput,
    FindElementsInput,
    InteractNodeInput,
    WaitForConditionInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_find_elements(
    client: GodotClient,
    params: FindElementsInput,
) -> str:
    """Handle godot_find_elements tool execution."""
    result = await client.find_elements(
        selector_type=params.selector_type,
        query=params.query,
        root_path=params.root_path,
        max_results=params.max_results,
    )
    return format_result(result)


async def handle_interact_node(
    client: GodotClient,
    params: InteractNodeInput,
) -> str:
    """Handle godot_interact_node tool execution."""
    result = await client.interact_node(
        node_path=params.node_path,
        action=params.action,
        text=params.text,
        clear_before_type=params.clear_before_type,
        drag_to_position=params.drag_to_position,
        scroll_delta=params.scroll_delta,
    )
    return format_result(result)


async def handle_wait_for_condition(
    client: GodotClient,
    params: WaitForConditionInput,
) -> str:
    """Handle godot_wait_for_condition tool execution."""
    result = await client.wait_for_condition(
        condition_type=params.condition_type,
        node_path=params.node_path,
        property_name=params.property_name,
        expected_value=params.expected_value,
        expression=params.expression,
        timeout_ms=params.timeout_ms,
        poll_interval_ms=params.poll_interval_ms,
    )
    return format_result(result)


async def handle_assert_node_state(
    client: GodotClient,
    params: AssertNodeStateInput,
) -> str:
    """Handle godot_assert_node_state tool execution."""
    result = await client.assert_node_state(
        node_path=params.node_path,
        assertions=params.assertions,
    )
    return format_result(result)
