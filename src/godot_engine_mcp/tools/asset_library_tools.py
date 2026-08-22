"""Asset Library tools implementation for Godot MCP."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.asset_library import (
    GetAssetDetailsInput,
    InstallAssetPackageInput,
    SearchAssetLibraryInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_search_asset_library(
    client: GodotClient, params: SearchAssetLibraryInput
) -> str:
    """Search the official Godot Asset Library for plugins, shaders, templates, and tools."""
    result = await client.search_asset_library(
        query=params.query,
        category=params.category,
        godot_version=params.godot_version,
        sort_by=params.sort_by.value,
        max_results=params.max_results,
    )
    return format_result(result, params.response_format)


async def handle_get_asset_details(
    client: GodotClient, params: GetAssetDetailsInput
) -> str:
    """Retrieve full details, previews, and download metadata for an asset from the Godot Asset Library."""
    result = await client.get_asset_details(asset_id=params.asset_id)
    return format_result(result, params.response_format)


async def handle_install_asset_package(
    client: GodotClient, params: InstallAssetPackageInput
) -> str:
    """Download and install a community asset or plugin package into the active project."""
    result = await client.install_asset_package(
        asset_id=params.asset_id,
        download_url=params.download_url,
        target_dir=params.target_dir,
        auto_enable_plugin=params.auto_enable_plugin,
    )
    return format_result(result, params.response_format)
