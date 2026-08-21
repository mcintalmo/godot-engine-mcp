"""Unit and headless tests for Godot Phase 9 tools (Shaders, Animation Trees & Localization)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.anim_tree import ConfigureAnimationTreeInput
from godot_mcp.models.localization import (
    AddTranslationInput,
    GetTranslationsInput,
)
from godot_mcp.models.shader import (
    CreateShaderInput,
    SetShaderParamInput,
)
from godot_mcp.tools.anim_tree_tools import handle_configure_animation_tree
from godot_mcp.tools.localization_tools import (
    handle_add_translation,
    handle_get_translations,
)
from godot_mcp.tools.shader_tools import (
    handle_create_shader,
    handle_set_shader_param,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase9_tools_mock() -> None:
    """Test Phase 9 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Create Shader
    shd_res = await handle_create_shader(
        client,
        CreateShaderInput(
            path="res://shaders/water.gdshader",
            shader_type="spatial",
            create_material=True,
        ),
    )
    assert "Custom Shader" in shd_res
    assert "water.gdshader" in shd_res

    # 2. Set Shader Param
    param_res = await handle_set_shader_param(
        client,
        SetShaderParamInput(
            node_path="/root/Main/WaterMesh",
            parameter_name="wave_speed",
            value=2.5,
        ),
    )
    assert "Shader Parameter Updated" in param_res
    assert "wave_speed" in param_res

    # 3. Configure AnimationTree
    tree_res = await handle_configure_animation_tree(
        client,
        ConfigureAnimationTreeInput(
            node_name="PlayerAnimTree",
            anim_player_path="../AnimationPlayer",
            states=[
                {"name": "idle", "animation": "Idle"},
                {"name": "walk", "animation": "Walk"},
            ],
            transitions=[
                {"from": "idle", "to": "walk", "advance_condition": "is_walking"},
            ],
        ),
    )
    assert "AnimationTree" in tree_res
    assert "PlayerAnimTree" in tree_res

    # 4. Get Translations
    trans_res = await handle_get_translations(client, GetTranslationsInput())
    assert "Translation Tables" in trans_res
    assert "localization/en.csv" in trans_res

    # 5. Add Translation
    add_trans_res = await handle_add_translation(
        client,
        AddTranslationInput(
            translation_path="res://localization/fr.csv",
            test_locale="fr",
        ),
    )
    assert "Translation Registered" in add_trans_res
    assert "fr.csv" in add_trans_res


@pytest.mark.asyncio
async def test_phase9_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 9 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Create Shader headlessly
    shd_res = await handle_create_shader(
        client,
        CreateShaderInput(
            path="res://shaders/outline.gdshader",
            shader_type="canvas_item",
        ),
    )
    assert "Custom Shader" in shd_res

    # 2. Set Shader Param headlessly
    param_res = await handle_set_shader_param(
        client,
        SetShaderParamInput(
            material_path="res://materials/outline_mat.tres",
            parameter_name="outline_color",
            value="#ff0000ff",
        ),
    )
    assert "Shader Parameter Updated" in param_res

    # 3. Configure AnimationTree headlessly
    tree_res = await handle_configure_animation_tree(
        client,
        ConfigureAnimationTreeInput(
            node_name="EnemyAnimTree",
            tree_type="state_machine",
        ),
    )
    assert "AnimationTree" in tree_res

    # 4. Get Translations headlessly
    trans_res = await handle_get_translations(client, GetTranslationsInput())
    assert "Translation Tables" in trans_res

    # 5. Add Translation headlessly
    add_res = await handle_add_translation(
        client,
        AddTranslationInput(
            translation_path="res://localization/de.csv",
            test_locale="de",
        ),
    )
    assert "Translation Registered" in add_res
