"""Tool handlers for Godot Project Asset Audits, Orphan Cleanup, and Texture Inspection."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.asset_audit import (
    AuditAssetsInput,
    CleanOrphansInput,
    GetTextureInfoInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_audit_assets(
    client: GodotClient,
    params: AuditAssetsInput,
) -> str:
    """Handle godot_audit_assets tool execution."""
    result = await client.audit_assets(
        include_extensions=params.include_extensions,
        ignore_paths=params.ignore_paths,
    )
    return format_result(result)


async def handle_clean_orphans(
    client: GodotClient,
    params: CleanOrphansInput,
) -> str:
    """Handle godot_clean_orphans tool execution."""
    result = await client.clean_orphans(
        file_paths=params.file_paths,
        dry_run=params.dry_run,
        quarantine_folder=params.quarantine_folder,
    )
    return format_result(result)


async def handle_get_texture_info(
    client: GodotClient,
    params: GetTextureInfoInput,
) -> str:
    """Handle godot_get_texture_info tool execution."""
    result = await client.get_texture_info(texture_path=params.texture_path)
    return format_result(result)
