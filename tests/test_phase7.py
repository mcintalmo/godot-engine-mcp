"""Unit and headless tests for Godot Phase 7 tools (DCC / Blender Model Import, VFX Particles, Export Build)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.dcc_asset import (
    CollisionGenerationMode,
    ConfigureGLTFImportInput,
    InstantiateModelInput,
)
from godot_engine_mcp.models.export_build import (
    ExportProjectInput,
    GetExportPresetsInput,
)
from godot_engine_mcp.models.particles import (
    ConfigureParticlesInput,
    ParticleEmissionShape,
    ParticleEngineType,
)
from godot_engine_mcp.tools.build_tools import (
    handle_export_project,
    handle_get_export_presets,
)
from godot_engine_mcp.tools.dcc_tools import (
    handle_configure_gltf_import,
    handle_instantiate_model,
)
from godot_engine_mcp.tools.particle_tools import handle_configure_particles
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase7_tools_mock() -> None:
    """Test Phase 7 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Instantiate Model
    inst_res = await handle_instantiate_model(
        client,
        InstantiateModelInput(
            source_path="res://assets/models/chest.glb",
            node_name="TreasureChest",
            position=(0.0, 1.0, 0.0),
            collision_mode=CollisionGenerationMode.BOX,
        ),
    )
    assert "TreasureChest" in inst_res
    assert "Colliders Created" in inst_res

    # 2. Configure GLTF Import
    gltf_res = await handle_configure_gltf_import(
        client,
        ConfigureGLTFImportInput(
            model_path="res://assets/models/character.glb",
            generate_lods=True,
            generate_shadow_mesh=True,
        ),
    )
    assert "character.glb" in gltf_res
    assert "generate_lods" in gltf_res

    # 3. Configure Particles
    part_res = await handle_configure_particles(
        client,
        ConfigureParticlesInput(
            node_name="CampfireSparks",
            particle_type=ParticleEngineType.GPU_3D,
            emission_shape=ParticleEmissionShape.SPHERE,
            emission_sphere_radius=0.5,
            amount=128,
            color_gradient=["#ff9900ff", "#ff2200aa", "#00000000"],
        ),
    )
    assert "CampfireSparks" in part_res
    assert "gpu_3d" in part_res

    # 4. Get Export Presets
    presets_res = await handle_get_export_presets(client, GetExportPresetsInput())
    assert "Export Presets" in presets_res
    assert "Windows Desktop" in presets_res

    # 5. Export Project
    export_res = await handle_export_project(
        client,
        ExportProjectInput(
            preset_name="Windows Desktop",
            output_path="builds/game.exe",
            debug=False,
        ),
    )
    assert "Export Build" in export_res
    assert "builds/game.exe" in export_res


@pytest.mark.asyncio
async def test_phase7_headless_client() -> None:
    """Test Phase 7 tools with HeadlessCLIClient."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # 1. Instantiate model headlessly
    inst_res = await handle_instantiate_model(
        client,
        InstantiateModelInput(
            source_path="res://models/sword.glb",
            node_name="Sword",
            collision_mode=CollisionGenerationMode.TRIMESH,
        ),
    )
    assert "Sword" in inst_res

    # 2. Configure particles headlessly
    part_res = await handle_configure_particles(
        client,
        ConfigureParticlesInput(
            node_name="Dust",
            particle_type=ParticleEngineType.GPU_3D,
            emission_shape=ParticleEmissionShape.BOX,
            save_path="res://particles/dust.tres",
        ),
    )
    assert "Dust" in part_res

    # 3. Get export presets headlessly
    presets_res = await handle_get_export_presets(client, GetExportPresetsInput())
    assert "Export Presets" in presets_res
