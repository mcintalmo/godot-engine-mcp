"""Tool handlers for Godot export presets and headless build execution."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.export_build import (
    ExportProjectInput,
    GetExportPresetsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_export_presets(
    client: GodotClient,
    params: GetExportPresetsInput,
) -> str:
    """Handle godot_get_export_presets tool execution."""
    result = await client.get_export_presets()
    return format_result(result)


async def handle_export_project(
    client: GodotClient,
    params: ExportProjectInput,
) -> str:
    """Handle godot_export_project tool execution."""
    result = await client.export_project(
        preset_name=params.preset_name,
        output_path=params.output_path,
        debug=params.debug,
    )
    return format_result(result)
