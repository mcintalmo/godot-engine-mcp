"""Tool handlers for Godot GPU Compute Shaders & RenderingDevice Pipelines."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.rendering_device import (
    DispatchComputeShaderInput,
    InspectRenderingDeviceInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_dispatch_compute_shader(
    client: GodotClient,
    params: DispatchComputeShaderInput,
) -> str:
    """Handle godot_dispatch_compute_shader tool execution."""
    input_bufs = [b.model_dump() for b in params.input_buffers]
    result = await client.dispatch_compute_shader(
        shader_code=params.shader_code,
        input_buffers=input_bufs,
        workgroup_size=params.workgroup_size,
        output_binding=params.output_binding,
        output_element_count=params.output_element_count,
    )
    return format_result(result)


async def handle_inspect_rendering_device(
    client: GodotClient,
    params: InspectRenderingDeviceInput,
) -> str:
    """Handle godot_inspect_rendering_device tool execution."""
    result = await client.inspect_rendering_device(
        extended_info=params.extended_info,
    )
    return format_result(result)
