"""Unit and headless tests for Godot Phase 22 tools (Deep Profiling & Memory Leak Diagnostics)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.profiling_diagnostics import (
    AuditOrphanNodesInput,
    CaptureProfilerTraceInput,
    InspectVRAMUsageInput,
)
from godot_mcp.tools.profiling_diagnostics_tools import (
    handle_audit_orphan_nodes,
    handle_capture_profiler_trace,
    handle_inspect_vram_usage,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase22_tools_mock() -> None:
    """Test Phase 22 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Audit Orphan Nodes
    orphan_res = await handle_audit_orphan_nodes(
        client,
        AuditOrphanNodesInput(print_orphans_to_stdout=False),
    )
    assert "Orphan Node Memory Leak Audit" in orphan_res
    assert "HEALTHY" in orphan_res
    assert "Orphan Nodes" in orphan_res

    # 2. Capture Profiler Trace
    trace_res = await handle_capture_profiler_trace(
        client,
        CaptureProfilerTraceInput(frames_to_sample=15),
    )
    assert "Performance Profiler Trace" in trace_res
    assert "Framerate" in trace_res
    assert "Process Loop" in trace_res
    assert "Physics Loop" in trace_res

    # 3. Inspect VRAM Usage
    vram_res = await handle_inspect_vram_usage(
        client,
        InspectVRAMUsageInput(detailed=True),
    )
    assert "GPU VRAM Memory Telemetry" in vram_res
    assert "Total VRAM Allocated" in vram_res
    assert "Texture Memory" in vram_res


@pytest.mark.asyncio
async def test_phase22_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 22 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Audit Orphan Nodes headlessly
    orphan_res = await handle_audit_orphan_nodes(
        client,
        AuditOrphanNodesInput(),
    )
    assert "Orphan Node Memory Leak Audit" in orphan_res

    # 2. Capture Profiler Trace headlessly
    trace_res = await handle_capture_profiler_trace(
        client,
        CaptureProfilerTraceInput(frames_to_sample=5),
    )
    assert "Performance Profiler Trace" in trace_res

    # 3. Inspect VRAM Usage headlessly
    vram_res = await handle_inspect_vram_usage(
        client,
        InspectVRAMUsageInput(),
    )
    assert "GPU VRAM Memory Telemetry" in vram_res
