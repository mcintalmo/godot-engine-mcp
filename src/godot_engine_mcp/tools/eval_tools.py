"""Tool handlers for Godot Expression runtime evaluation."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.runtime_eval import EvaluateExpressionInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_evaluate_expression(
    client: GodotClient,
    params: EvaluateExpressionInput,
) -> str:
    """Handle godot_evaluate_expression tool execution."""
    result = await client.evaluate_expression(
        expression=params.expression,
        node_path=params.node_path,
        input_variables=params.input_variables,
    )
    return format_result(result)
