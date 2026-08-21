"""Tool handlers for Godot Camera Presets, High-Res Viewport Capture & Rendering Pipeline."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.camera_rendering import (
    CaptureViewportInput,
    ConfigureCameraInput,
    ConfigureRenderSettingsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_configure_camera(
    client: GodotClient,
    params: ConfigureCameraInput,
) -> str:
    """Handle godot_configure_camera tool execution."""
    result = await client.configure_camera(
        camera_node_path=params.camera_node_path,
        projection=params.projection,
        fov=params.fov,
        size=params.size,
        near=params.near,
        far=params.far,
        current=params.current,
        zoom=params.zoom,
        position_smoothing_enabled=params.position_smoothing_enabled,
        position_smoothing_speed=params.position_smoothing_speed,
        limits=params.limits,
    )
    return format_result(result)


async def handle_configure_render_settings(
    client: GodotClient,
    params: ConfigureRenderSettingsInput,
) -> str:
    """Handle godot_configure_render_settings tool execution."""
    result = await client.configure_render_settings(
        msaa_2d=params.msaa_2d,
        msaa_3d=params.msaa_3d,
        screen_space_aa=params.screen_space_aa,
        use_taa=params.use_taa,
        scaling_3d_mode=params.scaling_3d_mode,
        scaling_3d_scale=params.scaling_3d_scale,
        directional_shadow_size=params.directional_shadow_size,
        positional_shadow_atlas_size=params.positional_shadow_atlas_size,
        vsync_mode=params.vsync_mode,
    )
    return format_result(result)


async def handle_capture_viewport(
    client: GodotClient,
    params: CaptureViewportInput,
) -> str:
    """Handle godot_capture_viewport tool execution."""
    result = await client.capture_viewport(
        output_path=params.output_path,
        max_width=params.max_width,
        max_height=params.max_height,
        format=params.format,
        include_base64=params.include_base64,
    )
    return format_result(result)
