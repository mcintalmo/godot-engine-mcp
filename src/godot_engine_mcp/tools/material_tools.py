"""Tool handlers for material and shader resource operations."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.common import ResponseFormat
from godot_engine_mcp.models.material import CreateMaterialInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_create_material(
    client: GodotClient,
    params: CreateMaterialInput,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """Handle godot_create_material tool execution."""
    result = await client.create_material(
        material_path=params.material_path,
        material_type=params.material_type.value,
        properties=params.properties,
        shader_path=params.shader_path,
        shader_code=params.shader_code,
        assign_to_node_path=params.assign_to_node_path,
    )
    return format_result(result, response_format)
