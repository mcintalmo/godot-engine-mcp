"""Unit and headless tests for Godot Phase 31 tools (GPU MultiMesh Scattering & Foliage Systems)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.multimesh_scatter import (
    ConfigureLODManagerInput,
    ScatterMultiMeshInput,
)
from godot_engine_mcp.tools.multimesh_scatter_tools import (
    handle_configure_lod_manager,
    handle_scatter_multimesh,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase31_tools_mock() -> None:
    """Test Phase 31 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Scatter MultiMesh
    scatter_res = await handle_scatter_multimesh(
        client,
        ScatterMultiMeshInput(
            mesh_path="res://assets/pine_tree.tres",
            node_name="ForestScatter",
            instance_count=500,
            area_size=[100.0, 100.0],
            min_scale=0.5,
            max_scale=1.5,
        ),
    )
    assert "Scattered GPU MultiMesh" in scatter_res
    assert "ForestScatter" in scatter_res
    assert "500" in scatter_res
    assert "pine_tree.tres" in scatter_res

    # 2. Configure LOD Manager
    lod_res = await handle_configure_lod_manager(
        client,
        ConfigureLODManagerInput(
            node_path="ForestScatter",
            visibility_range_begin=0.0,
            visibility_range_end=250.0,
            fade_mode="self",
        ),
    )
    assert "Configured Geometry LOD Settings" in lod_res
    assert "ForestScatter" in lod_res
    assert "250.0m" in lod_res
    assert "SELF" in lod_res


@pytest.mark.asyncio
async def test_phase31_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 31 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Scatter MultiMesh headlessly
    scatter_res = await handle_scatter_multimesh(
        client,
        ScatterMultiMeshInput(
            node_name="GrassScatter",
            instance_count=1000,
        ),
    )
    assert "Scattered GPU MultiMesh" in scatter_res
    assert "GrassScatter" in scatter_res
    assert "1000" in scatter_res

    # 2. Configure LOD Manager headlessly
    lod_res = await handle_configure_lod_manager(
        client,
        ConfigureLODManagerInput(
            node_path="GrassScatter",
            visibility_range_end=100.0,
        ),
    )
    assert "Configured Geometry LOD Settings" in lod_res
    assert "GrassScatter" in lod_res
    assert "100.0m" in lod_res
