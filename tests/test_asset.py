"""Unit and headless integration tests for asset reimport and collision polygon creation."""

from pathlib import Path

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.asset import (
    CreateCollisionPolygonInput,
    ImportPreset,
    PolygonType,
    ReimportAssetInput,
)
from godot_mcp.tools.asset_tools import (
    handle_create_collision_polygon,
    handle_reimport_asset,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_asset_tool_handlers_mock() -> None:
    """Test asset reimport and collision polygon tool handlers with mock client."""
    client = MockGodotClient()

    # 1. Test reimport_asset
    r1 = await handle_reimport_asset(
        client,
        ReimportAssetInput(
            asset_path="res://sprites/player.png",
            preset=ImportPreset.PIXEL_ART_2D,
            custom_params={"compress/mode": 0},
        ),
    )
    assert "Reimported asset res://sprites/player.png" in r1
    assert "pixel_art_2d" in r1

    # 2. Test create_collision_polygon 2D
    r2 = await handle_create_collision_polygon(
        client,
        CreateCollisionPolygonInput(
            points=[[-16.0, -16.0], [16.0, -16.0], [16.0, 16.0], [-16.0, 16.0]],
            polygon_type=PolygonType.TWO_D,
            parent_node_path="Player",
            node_name="PlayerCollider",
        ),
    )
    assert "Created 2D collision polygon" in r2
    assert "4 points" in r2

    # 3. Test create_collision_polygon 3D
    r3 = await handle_create_collision_polygon(
        client,
        CreateCollisionPolygonInput(
            points=[[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0]],
            polygon_type=PolygonType.THREE_D,
            depth=2.5,
            parent_node_path="Wall",
            node_name="WallCollider3D",
        ),
    )
    assert "Created 3D collision polygon" in r3
    assert "Extrusion Depth" in r3


@pytest.mark.asyncio
async def test_reimport_asset_headless() -> None:
    """Test reimporting an asset and creating .import configuration file headlessly."""
    proj_path = Path(__file__).parent / ".tmp_asset_proj"
    proj_path.mkdir(exist_ok=True)
    try:
        (proj_path / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="AssetTest"\n',
            encoding="utf-8",
        )
        sprites_dir = proj_path / "sprites"
        sprites_dir.mkdir(exist_ok=True)
        sample_png = sprites_dir / "hero.png"
        sample_png.write_bytes(b"\x89PNG\r\n\x1a\nfake_image_data")

        cfg = GodotConfig(executable_path=None, project_path=str(proj_path))
        client = HeadlessCLIClient(cfg)

        res = await handle_reimport_asset(
            client,
            ReimportAssetInput(
                asset_path="res://sprites/hero.png",
                preset=ImportPreset.PIXEL_ART_2D,
            ),
        )
        assert "Updated .import file" in res
        assert "pixel_art_2d" in res

        import_file = proj_path / "sprites" / "hero.png.import"
        assert import_file.exists()
        content = import_file.read_text(encoding="utf-8")
        assert "mipmaps/generate=false" in content
        assert "compress/mode=0" in content
    finally:
        import shutil

        shutil.rmtree(proj_path, ignore_errors=True)
