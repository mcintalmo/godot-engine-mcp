"""Tool handlers for Godot OpenXR & Spatial Computing (VR/AR/MR)."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.openxr import (
    ConfigureXRPassthroughInput,
    SetupXRRigInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_setup_xr_rig(
    client: GodotClient,
    params: SetupXRRigInput,
) -> str:
    """Handle godot_setup_xr_rig tool execution."""
    result = await client.setup_xr_rig(
        rig_name=params.rig_name,
        parent_path=params.parent_path,
        enable_controllers=params.enable_controllers,
        enable_hand_tracking=params.enable_hand_tracking,
        action_map_path=params.action_map_path,
    )
    return format_result(result)


async def handle_configure_xr_passthrough(
    client: GodotClient,
    params: ConfigureXRPassthroughInput,
) -> str:
    """Handle godot_configure_xr_passthrough tool execution."""
    result = await client.configure_xr_passthrough(
        xr_origin_path=params.xr_origin_path,
        enable_passthrough=params.enable_passthrough,
        reference_space=params.reference_space,
        foveated_rendering_level=params.foveated_rendering_level,
        dynamic_foveation=params.dynamic_foveation,
    )
    return format_result(result)
