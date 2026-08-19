"""Script tools implementation for Godot MCP."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.script import (
    CreateScriptInput,
    ValidateScriptInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_validate_script(
    client: GodotClient, params: ValidateScriptInput
) -> str:
    """Validate GDScript syntax and compilation."""
    result = await client.validate_script(
        script_path=params.script_path,
        code_content=params.code_content,
    )
    return format_result(result, params.response_format)


async def handle_create_script(client: GodotClient, params: CreateScriptInput) -> str:
    """Create or write a GDScript file."""
    result = await client.create_script(
        path=params.path,
        content=params.content,
        inherits=params.inherits,
        attach_to_node=params.attach_to_node,
    )
    return format_result(result, params.response_format)
