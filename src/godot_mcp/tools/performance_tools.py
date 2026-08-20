"""Tool handlers for Godot engine performance metrics and telemetry."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.performance import GetPerformanceMetricsInput
from godot_mcp.tools.formatters import format_result


async def handle_get_performance_metrics(
    client: GodotClient,
    params: GetPerformanceMetricsInput,
) -> str:
    """Handle godot_get_performance_metrics tool execution."""
    result = await client.get_performance_metrics(
        category=params.category.value,
        include_custom_monitors=params.include_custom_monitors,
    )
    return format_result(result)
