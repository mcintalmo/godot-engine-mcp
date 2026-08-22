"""Unit and headless tests for TileMapLayer cell painting and layer creation."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.tilemap import (
    CreateTileMapLayerInput,
    GetTileMapCellsInput,
    SetTileMapCellsInput,
    TileCell,
)
from godot_engine_mcp.tools.tilemap_tools import (
    handle_create_tilemap_layer,
    handle_get_tilemap_cells,
    handle_set_tilemap_cells,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_tilemap_tools_mock() -> None:
    """Test tilemap tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Create TileMapLayer
    res = await handle_create_tilemap_layer(
        client,
        CreateTileMapLayerInput(
            name="GroundLayer",
            parent_node_path="World",
            tile_set_path="res://tilesets/ground.tres",
        ),
    )
    assert "Created TileMapLayer 'GroundLayer'" in res
    assert "GroundLayer" in res
    assert "res://tilesets/ground.tres" in res

    # 2. Batch Paint Cells
    res = await handle_set_tilemap_cells(
        client,
        SetTileMapCellsInput(
            node_path="World/GroundLayer",
            cells=[
                TileCell(coords=[0, 0], source_id=0, atlas_coords=[0, 0]),
                TileCell(coords=[1, 0], source_id=0, atlas_coords=[1, 0]),
                TileCell(coords=[2, 0], source_id=0, atlas_coords=[2, 0]),
                TileCell(coords=[3, 0], source_id=-1),
            ],
            clear_before_paint=False,
        ),
    )
    assert "Applied tile cells" in res
    assert "`3` cells" in res
    assert "`1` cells" in res

    # 3. Query Cells
    res = await handle_get_tilemap_cells(
        client,
        GetTileMapCellsInput(node_path="World/GroundLayer"),
    )
    assert "Retrieved 2 cells" in res
    assert "Total Used Cells" in res
    assert "Coords `[0, 0]`" in res


@pytest.mark.asyncio
async def test_tilemap_headless_creation() -> None:
    """Test headless handling of TileMapLayer node creation and cell painting."""
    cfg = GodotConfig(project_path=".")
    client = HeadlessCLIClient(cfg)

    res = await handle_create_tilemap_layer(
        client,
        CreateTileMapLayerInput(name="WaterLayer"),
    )
    # Headless interactive node creation informs the user an editor is required
    assert "EDITOR_REQUIRED" in res or "WaterLayer" in res

    paint_res = await handle_set_tilemap_cells(
        client,
        SetTileMapCellsInput(
            node_path="WaterLayer",
            cells=[
                TileCell(coords=[0, 0], source_id=0, atlas_coords=[0, 0]),
                TileCell(coords=[0, 1], source_id=0, atlas_coords=[0, 1]),
            ],
        ),
    )
    assert "Applied 2 tile cell operations" in paint_res

    get_res = await handle_get_tilemap_cells(
        client,
        GetTileMapCellsInput(node_path="WaterLayer"),
    )
    assert "Queried tile cells" in get_res
