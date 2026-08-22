"""Tool handlers for Godot Deep Profiling & Memory Leak Diagnostics."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.profiling_diagnostics import (
    AuditOrphanNodesInput,
    CaptureProfilerTraceInput,
    InspectVRAMUsageInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_audit_orphan_nodes(
    client: GodotClient,
    params: AuditOrphanNodesInput,
) -> str:
    """Handle godot_audit_orphan_nodes tool execution."""
    result = await client.audit_orphan_nodes(
        print_orphans_to_stdout=params.print_orphans_to_stdout,
    )
    return format_result(result)


async def handle_capture_profiler_trace(
    client: GodotClient,
    params: CaptureProfilerTraceInput,
) -> str:
    """Handle godot_capture_profiler_trace tool execution."""
    result = await client.capture_profiler_trace(
        frames_to_sample=params.frames_to_sample,
    )
    return format_result(result)


async def handle_inspect_vram_usage(
    client: GodotClient,
    params: InspectVRAMUsageInput,
) -> str:
    """Handle godot_inspect_vram_usage tool execution."""
    result = await client.inspect_vram_usage(
        detailed=params.detailed,
    )
    return format_result(result)
