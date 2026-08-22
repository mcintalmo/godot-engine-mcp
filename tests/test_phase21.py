"""Unit and headless tests for Godot Phase 21 tools (3D GridMaps & Procedural Bezier Paths)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.gridmap_path import (
    ConfigureGridMapInput,
    CreateCurvePathInput,
    CurvePoint,
    GridMapCell,
)
from godot_engine_mcp.tools.gridmap_path_tools import (
    handle_configure_gridmap,
    handle_create_curve_path,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase21_tools_mock() -> None:
    """Test Phase 21 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure GridMap
    gm_res = await handle_configure_gridmap(
        client,
        ConfigureGridMapInput(
            gridmap_node_path="LevelGridMap",
            mesh_library_path="res://assets/tiles.meshlib",
            cells_to_set=[
                GridMapCell(position=[0, 0, 0], item_id=1, orientation=0),
                GridMapCell(position=[1, 0, 0], item_id=2, orientation=4),
            ],
        ),
    )
    assert "Configured GridMap" in gm_res
    assert "LevelGridMap" in gm_res
    assert "Placed/Updated 2 cells" in gm_res

    # 2. Create Curve Path
    path_res = await handle_create_curve_path(
        client,
        CreateCurvePathInput(
            path_type="3d",
            node_name="PatrolRoute",
            points=[
                CurvePoint(position=[0.0, 0.0, 0.0], out_handle=[0.0, 0.0, 5.0]),
                CurvePoint(position=[10.0, 0.0, 10.0], in_handle=[-5.0, 0.0, 0.0]),
            ],
            closed=True,
            add_path_follow=True,
        ),
    )
    assert "Created 3D Curve Path" in path_res
    assert "PatrolRoute" in path_res
    assert "Control Points" in path_res
    assert "Attached PathFollow Node" in path_res


@pytest.mark.asyncio
async def test_phase21_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 21 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure GridMap headlessly
    gm_res = await handle_configure_gridmap(
        client,
        ConfigureGridMapInput(
            gridmap_node_path="GridMap",
            cells_to_set=[
                GridMapCell(position=[0, 0, 0], item_id=0),
            ],
        ),
    )
    assert "Configured GridMap" in gm_res
    assert "GridMap" in gm_res

    # 2. Create Curve Path 2D headlessly
    path_res = await handle_create_curve_path(
        client,
        CreateCurvePathInput(
            path_type="2d",
            node_name="Track2D",
            points=[
                CurvePoint(position=[0.0, 0.0]),
                CurvePoint(position=[100.0, 50.0]),
            ],
        ),
    )
    assert "Created 2D Curve Path" in path_res
    assert "Track2D" in path_res
