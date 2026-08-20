"""Unit and integration tests for Godot performance telemetry tools and resources."""

import json
from pathlib import Path

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.performance import (
    GetPerformanceMetricsInput,
    MetricCategory,
)
from godot_mcp.server import create_server
from godot_mcp.tools.performance_tools import handle_get_performance_metrics
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_performance_tools_mock() -> None:
    """Test performance metric tool handler with MockGodotClient."""
    client = MockGodotClient()

    # 1. Query all metrics
    res_all = await handle_get_performance_metrics(
        client,
        GetPerformanceMetricsInput(category=MetricCategory.ALL),
    )
    assert "Performance Telemetry" in res_all
    assert "Framerate & Timing" in res_all
    assert "FPS" in res_all
    assert "Rendering & GPU" in res_all
    assert "Draw Calls" in res_all
    assert "Memory Allocations" in res_all
    assert "Static RAM" in res_all
    assert "Object & Node Tracking" in res_all
    assert "Node Count" in res_all

    # 2. Query time only
    res_time = await handle_get_performance_metrics(
        client,
        GetPerformanceMetricsInput(category=MetricCategory.TIME),
    )
    assert "Framerate & Timing" in res_time


@pytest.mark.asyncio
async def test_performance_dynamic_resource() -> None:
    """Test dynamic MCP resource godot://performance/metrics."""
    client = MockGodotClient()
    server = create_server(client=client)

    res_raw = await server.read_resource("godot://performance/metrics")
    res_list = list(res_raw)
    assert len(res_list) > 0
    content = str(getattr(res_list[0], "content", getattr(res_list[0], "text", "")))
    assert "time" in content
    assert "fps" in content
    payload = json.loads(content)
    assert "render" in payload
    assert "memory" in payload


@pytest.mark.asyncio
async def test_performance_headless_sampling() -> None:
    """Test sampling performance metrics headlessly with Godot CLI."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    tmp_proj = Path(__file__).parent / ".tmp_perf_proj"
    tmp_proj.mkdir(exist_ok=True)
    try:
        (tmp_proj / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="PerfTest"\n',
            encoding="utf-8",
        )
        cfg = GodotConfig(executable_path=exe, project_path=str(tmp_proj))
        client = HeadlessCLIClient(cfg)

        res = await handle_get_performance_metrics(
            client,
            GetPerformanceMetricsInput(category=MetricCategory.ALL),
        )
        assert "Performance Telemetry" in res
        assert "FPS" in res
    finally:
        import shutil

        shutil.rmtree(tmp_proj, ignore_errors=True)
