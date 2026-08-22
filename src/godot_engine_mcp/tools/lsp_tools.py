"""Tool handlers for Godot GDScript Language Server Protocol (LSP) operations."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.lsp import (
    LSPQueryInput,
    LSPRenameInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_lsp_query(
    client: GodotClient,
    params: LSPQueryInput,
) -> str:
    """Handle godot_lsp_query tool execution."""
    result = await client.query_lsp(
        file_path=params.file_path,
        query_type=params.query_type.value,
        line=params.line,
        character=params.character,
        symbol_name=params.symbol_name,
    )
    return format_result(result)


async def handle_lsp_rename(
    client: GodotClient,
    params: LSPRenameInput,
) -> str:
    """Handle godot_lsp_rename tool execution."""
    result = await client.rename_lsp_symbol(
        file_path=params.file_path,
        line=params.line,
        character=params.character,
        new_name=params.new_name,
    )
    return format_result(result)
