"""Reflection, ClassDB introspection, documentation, and shader tools implementation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.reflection import (
    GetClassInfoInput,
    GetDocumentationInput,
    ValidateShaderInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_class_info(client: GodotClient, params: GetClassInfoInput) -> str:
    """Retrieve Godot ClassDB inheritance, properties, methods, signals, and constants."""
    result = await client.get_class_info(
        class_name=params.class_name,
        include_inherited=params.include_inherited,
        category=params.category,
    )
    return format_result(result, params.response_format)


async def handle_get_documentation(
    client: GodotClient, params: GetDocumentationInput
) -> str:
    """Retrieve Godot API documentation and signatures for classes, methods, and properties."""
    result = await client.get_documentation(
        query=params.query,
        category=params.category,
    )
    return format_result(result, params.response_format)


async def handle_validate_shader(
    client: GodotClient, params: ValidateShaderInput
) -> str:
    """Validate Godot .gdshader code syntax and compilation."""
    result = await client.validate_shader(
        shader_path=params.shader_path,
        shader_code=params.shader_code,
    )
    return format_result(result, params.response_format)
