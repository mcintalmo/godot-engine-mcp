"""Tool handlers for Godot custom shaders and ShaderMaterial uniforms."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.shader import (
    CreateShaderInput,
    SetShaderParamInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_create_shader(
    client: GodotClient,
    params: CreateShaderInput,
) -> str:
    """Handle godot_create_shader tool execution."""
    result = await client.create_shader(
        path=params.path,
        shader_type=params.shader_type,
        code=params.code,
        create_material=params.create_material,
        material_save_path=params.material_save_path,
    )
    return format_result(result)


async def handle_set_shader_param(
    client: GodotClient,
    params: SetShaderParamInput,
) -> str:
    """Handle godot_set_shader_param tool execution."""
    result = await client.set_shader_param(
        parameter_name=params.parameter_name,
        value=params.value,
        node_path=params.node_path,
        material_path=params.material_path,
    )
    return format_result(result)
