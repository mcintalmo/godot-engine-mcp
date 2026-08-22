"""Unit and headless integration tests for NavMesh baking and NavigationRegion tools."""

from pathlib import Path

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.navigation import (
    BakeNavMeshInput,
    CreateNavigationRegionInput,
    NavDimension,
)
from godot_engine_mcp.tools.navigation_tools import (
    handle_bake_navmesh,
    handle_create_navigation_region,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_navigation_tools_mock() -> None:
    """Test navigation tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Create NavigationRegion3D
    res3d = await handle_create_navigation_region(
        client,
        CreateNavigationRegionInput(
            name="NavRegion3D",
            dimension=NavDimension.THREE_D,
            parent_node_path="World",
            navmesh_path="res://nav/custom_navmesh.tres",
        ),
    )
    assert "Created NavigationRegion3D" in res3d
    assert "NavRegion3D" in res3d
    assert "3D" in res3d
    assert "res://nav/custom_navmesh.tres" in res3d

    # 2. Create NavigationRegion2D
    res2d = await handle_create_navigation_region(
        client,
        CreateNavigationRegionInput(
            name="NavRegion2D",
            dimension=NavDimension.TWO_D,
            parent_node_path="World",
        ),
    )
    assert "Created NavigationRegion2D" in res2d
    assert "NavRegion2D" in res2d
    assert "2D" in res2d

    # 3. Bake NavMesh with agent parameters
    bake_res = await handle_bake_navmesh(
        client,
        BakeNavMeshInput(
            node_path="World/NavRegion3D",
            dimension=NavDimension.THREE_D,
            agent_radius=0.5,
            agent_height=1.8,
            agent_max_climb=0.4,
            agent_max_slope=45.0,
            cell_size=0.25,
            save_navmesh_path="res://nav/baked_mesh.tres",
        ),
    )
    assert "Triggered 3D navigation mesh baking" in bake_res
    assert "NavRegion3D" in bake_res
    assert "`agent_radius` = `0.5`" in bake_res
    assert "`agent_height` = `1.8`" in bake_res
    assert "res://nav/baked_mesh.tres" in bake_res


@pytest.mark.asyncio
async def test_bake_navmesh_headless() -> None:
    """Test creating and saving a NavigationMesh resource headlessly with Godot CLI."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    proj_path = Path(__file__).parent / ".tmp_nav_proj"
    proj_path.mkdir(exist_ok=True)
    try:
        (proj_path / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="NavTest"\n',
            encoding="utf-8",
        )

        cfg = GodotConfig(executable_path=exe, project_path=str(proj_path))
        client = HeadlessCLIClient(cfg)

        res = await handle_bake_navmesh(
            client,
            BakeNavMeshInput(
                node_path="NavRegion3D",
                dimension=NavDimension.THREE_D,
                agent_radius=0.6,
                agent_height=2.0,
                agent_max_slope=35.0,
                cell_size=0.3,
                save_navmesh_path="res://nav/main_navmesh.tres",
            ),
        )
        assert "navigation" in res.lower()

        nav_file = proj_path / "nav" / "main_navmesh.tres"
        assert nav_file.exists()
        content = nav_file.read_text(encoding="utf-8")
        assert "NavigationMesh" in content
        assert "agent_radius = 0.6" in content or "0.6" in content
    finally:
        import shutil

        shutil.rmtree(proj_path, ignore_errors=True)
