"""Unit and integration tests for material creation and shader attachment."""

from pathlib import Path

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.material import CreateMaterialInput, MaterialType
from godot_engine_mcp.tools.material_tools import handle_create_material


@pytest.mark.asyncio
async def test_create_material_headless() -> None:
    """Test creating StandardMaterial3D and ShaderMaterial with real Godot binary."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    proj_path = Path(__file__).parent / ".tmp_material_proj"
    proj_path.mkdir(exist_ok=True)
    try:
        (proj_path / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Test"\n', encoding="utf-8"
        )

        cfg = GodotConfig(executable_path=exe, project_path=str(proj_path))
        client = HeadlessCLIClient(cfg)

        # 1. Test StandardMaterial3D creation
        res1 = await handle_create_material(
            client,
            CreateMaterialInput(
                material_path="res://materials/cyan_glow.tres",
                material_type=MaterialType.STANDARD_3D,
                properties={
                    "albedo_color": [0.0, 1.0, 1.0, 1.0],
                    "metallic": 0.9,
                    "roughness": 0.1,
                    "emission_enabled": True,
                    "emission": [0.0, 1.0, 1.0, 1.0],
                    "emission_energy_multiplier": 3.0,
                },
            ),
        )
        assert "Created material" in res1
        assert "res://materials/cyan_glow.tres" in res1
        assert (proj_path / "materials" / "cyan_glow.tres").exists()

        # 2. Test ShaderMaterial creation with inline shader
        valid_shader = """shader_type spatial;
render_mode unshaded;
uniform vec4 glow_color : source_color = vec4(1.0, 0.0, 0.5, 1.0);
void fragment() {
    ALBEDO = glow_color.rgb;
}"""
        res2 = await handle_create_material(
            client,
            CreateMaterialInput(
                material_path="res://materials/custom_shader.tres",
                material_type=MaterialType.SHADER,
                shader_code=valid_shader,
                properties={"glow_color": [1.0, 0.0, 0.5, 1.0]},
            ),
        )
        assert "Created material" in res2
        assert "res://materials/custom_shader.tres" in res2
        assert (proj_path / "materials" / "custom_shader.tres").exists()
    finally:
        import shutil

        shutil.rmtree(proj_path, ignore_errors=True)
