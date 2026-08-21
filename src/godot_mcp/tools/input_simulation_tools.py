"""Tool handlers for Godot Interactive Runtime Input Simulation & Debug Drawing."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.input_simulation import (
    ClearDebugShapesInput,
    DrawDebugShapesInput,
    SimulateInputInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_simulate_input(
    client: GodotClient,
    params: SimulateInputInput,
) -> str:
    """Handle godot_simulate_input tool execution."""
    result = await client.simulate_input(
        event_type=params.event_type,
        action=params.action,
        pressed=params.pressed,
        strength=params.strength,
        key=params.key,
        button_index=params.button_index,
        position=params.position,
        relative=params.relative,
    )
    return format_result(result)


async def handle_draw_debug_shapes(
    client: GodotClient,
    params: DrawDebugShapesInput,
) -> str:
    """Handle godot_draw_debug_shapes tool execution."""
    result = await client.draw_debug_shapes(
        shapes=[s.model_dump() for s in params.shapes],
    )
    return format_result(result)


async def handle_clear_debug_shapes(
    client: GodotClient,
    params: ClearDebugShapesInput,
) -> str:
    """Handle godot_clear_debug_shapes tool execution."""
    result = await client.clear_debug_shapes(
        category=params.category,
    )
    return format_result(result)
