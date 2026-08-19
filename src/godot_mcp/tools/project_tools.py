"""Project tools implementation for Godot MCP."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.project import (
    GetProjectSettingsInput,
    GetVersionInput,
    ListProjectFilesInput,
    SetProjectSettingInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_version(client: GodotClient, params: GetVersionInput) -> str:
    """Get Godot Engine version and project metadata."""
    result = await client.get_version()
    return format_result(result, params.response_format)


async def handle_get_project_settings(
    client: GodotClient, params: GetProjectSettingsInput
) -> str:
    """Query settings from project.godot."""
    result = await client.get_project_settings(section=params.section)
    return format_result(result, params.response_format)


async def handle_set_project_setting(
    client: GodotClient, params: SetProjectSettingInput
) -> str:
    """Set a configuration value in project.godot."""
    result = await client.set_project_setting(name=params.name, value=params.value)
    return format_result(result, params.response_format)


async def handle_list_project_files(
    client: GodotClient, params: ListProjectFilesInput
) -> str:
    """List project assets and resource files."""
    result = await client.list_project_files(
        directory=params.directory,
        extension_filter=params.extension_filter,
        recursive=params.recursive,
    )
    return format_result(result, params.response_format)
