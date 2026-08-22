"""Unit and integration tests for engine reflection, ClassDB introspection, and shader validation."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.reflection import (
    GetClassInfoInput,
    GetDocumentationInput,
    ValidateShaderInput,
)
from godot_engine_mcp.tools.reflection_tools import (
    handle_get_class_info,
    handle_get_documentation,
    handle_validate_shader,
)


@pytest.mark.asyncio
async def test_reflection_tools_headless() -> None:
    """Test ClassDB reflection and shader validation using HeadlessCLIClient with real Godot binary."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    cfg = GodotConfig(executable_path=exe)
    client = HeadlessCLIClient(cfg)

    # 1. Test get_class_info for CharacterBody2D
    class_res = await handle_get_class_info(
        client,
        GetClassInfoInput(class_name="CharacterBody2D", category="all"),
    )
    assert "CharacterBody2D" in class_res
    assert "move_and_slide" in class_res
    assert "velocity" in class_res

    # 2. Test get_class_info with properties only
    props_res = await handle_get_class_info(
        client,
        GetClassInfoInput(class_name="StandardMaterial3D", category="properties"),
    )
    assert "StandardMaterial3D" in props_res
    assert "albedo_color" in props_res

    # 3. Test get_documentation
    doc_res = await handle_get_documentation(
        client,
        GetDocumentationInput(query="CharacterBody2D.move_and_slide"),
    )
    assert "CharacterBody2D.move_and_slide" in doc_res
    assert "move_and_slide" in doc_res

    # 4. Test valid shader code
    valid_shader = """shader_type spatial;
void fragment() {
    ALBEDO = vec3(0.0, 1.0, 0.0);
}"""
    valid_res = await handle_validate_shader(
        client,
        ValidateShaderInput(shader_code=valid_shader),
    )
    assert "SUCCESS" in valid_res
    assert "verified successfully" in valid_res

    # 5. Test invalid shader code
    invalid_shader = """shader_type spatial;
void fragment() {
    INVALID_VARIABLE = 123.0;
}"""
    invalid_res = await handle_validate_shader(
        client,
        ValidateShaderInput(shader_code=invalid_shader),
    )
    assert "FAILED" in invalid_res
    assert "Shader compilation failed" in invalid_res
