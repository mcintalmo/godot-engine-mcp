"""Unit and headless tests for Godot Phase 25 tools (CSG Whiteboxing & Procedural Mesh Generation)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.procedural_geometry import (
    CreateCSGShapeInput,
    GenerateProceduralMeshInput,
)
from godot_mcp.tools.procedural_geometry_tools import (
    handle_create_csg_shape,
    handle_generate_procedural_mesh,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase25_tools_mock() -> None:
    """Test Phase 25 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Create CSG Shape
    csg_res = await handle_create_csg_shape(
        client,
        CreateCSGShapeInput(
            shape_type="cylinder",
            node_name="ColumnCutout",
            operation="subtraction",
            radius=1.5,
            height=4.0,
            position=[0.0, 2.0, 0.0],
            use_collision=True,
        ),
    )
    assert "Created CSG Shape" in csg_res
    assert "ColumnCutout" in csg_res
    assert "CYLINDER" in csg_res
    assert "SUBTRACTION" in csg_res

    # 2. Generate Procedural Mesh
    mesh_res = await handle_generate_procedural_mesh(
        client,
        GenerateProceduralMeshInput(
            mesh_type="grid",
            node_name="TerrainMesh",
            size=[20.0, 20.0],
            subdivisions=[8, 8],
            generate_normals=True,
            generate_tangents=True,
            save_to_resource_path="res://terrain.tres",
        ),
    )
    assert "Generated Procedural Mesh" in mesh_res
    assert "TerrainMesh" in mesh_res
    assert "GRID" in mesh_res
    assert "terrain.tres" in mesh_res


@pytest.mark.asyncio
async def test_phase25_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 25 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Create CSG Shape headlessly
    csg_res = await handle_create_csg_shape(
        client,
        CreateCSGShapeInput(
            shape_type="box",
            node_name="RoomWall",
            size=[5.0, 3.0, 0.3],
        ),
    )
    assert "Created CSG Shape" in csg_res
    assert "RoomWall" in csg_res

    # 2. Generate Procedural Mesh headlessly
    mesh_res = await handle_generate_procedural_mesh(
        client,
        GenerateProceduralMeshInput(
            mesh_type="pyramid",
            node_name="RoofMesh",
            size=[4.0, 2.0, 4.0],
        ),
    )
    assert "Generated Procedural Mesh" in mesh_res
    assert "RoofMesh" in mesh_res
