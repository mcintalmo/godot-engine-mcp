"""Pydantic input models for material and shader resource creation."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MaterialType(str, Enum):
    """Supported Godot Material subclasses."""

    STANDARD_3D = "StandardMaterial3D"
    SHADER = "ShaderMaterial"
    CANVAS_ITEM = "CanvasItemMaterial"
    ORM_3D = "ORMMaterial3D"


class CreateMaterialInput(BaseModel):
    """Input model for godot_create_material."""

    material_path: str = Field(
        ...,
        description="Target destination resource path (e.g. 'res://materials/player_neon.tres').",
    )
    material_type: MaterialType = Field(
        default=MaterialType.STANDARD_3D,
        description="Type of Material to instantiate (StandardMaterial3D, ShaderMaterial, CanvasItemMaterial, ORMMaterial3D).",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Key-value dictionary of PBR / material properties to set (e.g. "
            "{'albedo_color': [0.2, 0.8, 1.0, 1.0], 'roughness': 0.3, 'metallic': 0.8, "
            "'emission_enabled': True, 'emission': [0.2, 0.8, 1.0, 1.0], 'emission_energy_multiplier': 2.0})."
        ),
    )
    shader_path: str | None = Field(
        default=None,
        description="Optional path to existing .gdshader resource for ShaderMaterial (e.g. 'res://shaders/water.gdshader').",
    )
    shader_code: str | None = Field(
        default=None,
        description="Optional inline .gdshader code to compile and attach if material_type is ShaderMaterial.",
    )
    assign_to_node_path: str | None = Field(
        default=None,
        description="Optional node path in the current scene to attach the new material to (e.g. 'Player/MeshInstance3D').",
    )
