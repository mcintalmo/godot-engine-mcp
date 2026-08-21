"""Pydantic models for Godot custom shaders and ShaderMaterial uniforms."""

from typing import Any

from pydantic import BaseModel, Field


class CreateShaderInput(BaseModel):
    """Input model for godot_create_shader."""

    path: str = Field(
        description="Resource path for the shader file (e.g. 'res://shaders/water.gdshader', 'res://shaders/outline.gdshader').",
    )
    shader_type: str = Field(
        default="spatial",
        description="Godot shader type: 'spatial' (3D), 'canvas_item' (2D/UI), 'particles' (VFX), or 'fog' (Volumetric Fog).",
    )
    code: str | None = Field(
        default=None,
        description="Optional custom GDShader code string. If omitted, standard starter template for the shader_type will be generated.",
    )
    create_material: bool = Field(
        default=True,
        description="Whether to also generate a matching ShaderMaterial (.tres) resource.",
    )
    material_save_path: str | None = Field(
        default=None,
        description="Optional destination path for the generated ShaderMaterial (e.g. 'res://materials/water_mat.tres'). Defaults to path with .tres extension.",
    )


class SetShaderParamInput(BaseModel):
    """Input model for godot_set_shader_param."""

    parameter_name: str = Field(
        description="Name of the shader uniform / parameter (e.g. 'wave_speed', 'albedo_color', 'roughness', 'dissolve_threshold').",
    )
    value: Any = Field(
        description="New value for the uniform parameter (float, int, bool, hex color string, or array/list of numbers for Vector2/3/4).",
    )
    node_path: str | None = Field(
        default=None,
        description="Optional path of the node in the active scene possessing the ShaderMaterial (e.g. 'WaterMesh', 'Player/Sprite2D').",
    )
    material_path: str | None = Field(
        default=None,
        description="Optional resource path to a standalone ShaderMaterial file (e.g. 'res://materials/water_mat.tres'). Required if node_path is not specified.",
    )
