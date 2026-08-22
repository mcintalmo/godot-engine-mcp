"""Unit and headless tests for Godot Phase 11 tools (Navigation Obstacles, TileSet Terrains & Scene Diff)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.nav_obstacle import ConfigureNavigationObstacleInput
from godot_engine_mcp.models.scene_diff import DiffSceneInput
from godot_engine_mcp.models.tileset_terrain import ConfigureTileSetTerrainInput
from godot_engine_mcp.tools.nav_obstacle_tools import (
    handle_configure_navigation_obstacle,
)
from godot_engine_mcp.tools.scene_diff_tools import handle_diff_scene
from godot_engine_mcp.tools.tileset_terrain_tools import (
    handle_configure_tileset_terrain,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase11_tools_mock() -> None:
    """Test Phase 11 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure Navigation Obstacle
    obs_res = await handle_configure_navigation_obstacle(
        client,
        ConfigureNavigationObstacleInput(
            node_name="TreeObstacle",
            is_3d=True,
            radius=2.0,
            avoidance_layers=3,
        ),
    )
    assert "NavigationObstacle" in obs_res
    assert "TreeObstacle" in obs_res

    # 2. Configure TileSet Terrain
    terrain_res = await handle_configure_tileset_terrain(
        client,
        ConfigureTileSetTerrainInput(
            tileset_path="res://tilesets/world.tres",
            terrain_set=0,
            mode="match_corners_and_sides",
            terrains=[
                {"name": "Grass", "color": "#00ff00"},
                {"name": "Water", "color": "#0000ff"},
            ],
        ),
    )
    assert "TileSet Terrain Set 0" in terrain_res
    assert "world.tres" in terrain_res

    # 3. Diff Scene
    diff_res = await handle_diff_scene(
        client,
        DiffSceneInput(scene_path="res://scenes/main.tscn"),
    )
    assert "Scene Diff" in diff_res
    assert "Main/NewLight" in diff_res


@pytest.mark.asyncio
async def test_phase11_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 11 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure Navigation Obstacle headlessly
    obs_res = await handle_configure_navigation_obstacle(
        client,
        ConfigureNavigationObstacleInput(
            node_name="RockObstacle2D",
            is_3d=False,
            radius=1.5,
        ),
    )
    assert "NavigationObstacle" in obs_res

    # 2. Configure TileSet Terrain headlessly
    terrain_res = await handle_configure_tileset_terrain(
        client,
        ConfigureTileSetTerrainInput(
            tileset_path="res://tilesets/dungeon.tres",
        ),
    )
    assert "TileSet Terrain Set 0" in terrain_res

    # 3. Diff Scene headlessly
    diff_res = await handle_diff_scene(
        client,
        DiffSceneInput(scene_path="res://scenes/level.tscn"),
    )
    assert "Scene Diff" in diff_res
