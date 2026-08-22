"""Unit and headless tests for Godot Phase 28 tools (Global Illumination & Baked Lighting)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.lightmap_gi import (
    BakeLightmapsInput,
    ConfigureLightmapGIInput,
)
from godot_engine_mcp.tools.lightmap_gi_tools import (
    handle_bake_lightmaps,
    handle_configure_lightmap_gi,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase28_tools_mock() -> None:
    """Test Phase 28 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure LightmapGI
    gi_res = await handle_configure_lightmap_gi(
        client,
        ConfigureLightmapGIInput(
            gi_type="lightmap_gi",
            node_name="LevelLightmap",
            quality="high",
            bounces=4,
            use_denoiser=True,
            denoiser_name="oidn",
            interior=True,
        ),
    )
    assert "Configured Global Illumination" in gi_res
    assert "LevelLightmap" in gi_res
    assert "LIGHTMAP_GI" in gi_res
    assert "HIGH" in gi_res
    assert "OIDN" in gi_res

    # 2. Configure VoxelGI / ReflectionProbe
    vgi_res = await handle_configure_lightmap_gi(
        client,
        ConfigureLightmapGIInput(
            gi_type="voxel_gi",
            node_name="ArenaVoxelGI",
            size=[30.0, 15.0, 30.0],
        ),
    )
    assert "Configured Global Illumination" in vgi_res
    assert "ArenaVoxelGI" in vgi_res
    assert "VOXEL_GI" in vgi_res

    # 3. Bake Lightmaps
    bake_res = await handle_bake_lightmaps(
        client,
        BakeLightmapsInput(
            lightmap_node_path="LevelLightmap",
            bake_mode="scene",
            save_path="res://baked_lightmaps.lmbake",
        ),
    )
    assert "Lightmap Bake Summary" in bake_res
    assert "LevelLightmap" in bake_res
    assert "SCENE" in bake_res
    assert "baked_lightmaps.lmbake" in bake_res


@pytest.mark.asyncio
async def test_phase28_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 28 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure LightmapGI headlessly
    gi_res = await handle_configure_lightmap_gi(
        client,
        ConfigureLightmapGIInput(
            gi_type="reflection_probe",
            node_name="HallwayProbe",
        ),
    )
    assert "Configured Global Illumination" in gi_res
    assert "HallwayProbe" in gi_res

    # 2. Bake Lightmaps headlessly
    bake_res = await handle_bake_lightmaps(
        client,
        BakeLightmapsInput(
            lightmap_node_path="HallwayProbe",
        ),
    )
    assert "Lightmap Bake Summary" in bake_res
    assert "HallwayProbe" in bake_res
