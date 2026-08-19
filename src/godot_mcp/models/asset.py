"""Pydantic models for asset reimport and collision polygon generation."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ImportPreset(str, Enum):
    """Standard presets for asset import configuration."""

    PIXEL_ART_2D = "pixel_art_2d"
    HIGH_QUALITY_3D = "high_quality_3d"
    UNCOMPRESSED_AUDIO = "uncompressed_audio"
    CUSTOM = "custom"


class PolygonType(str, Enum):
    """Type of collision polygon to generate."""

    TWO_D = "2D"
    THREE_D = "3D"


class ReimportAssetInput(BaseModel):
    """Input model for godot_reimport_asset."""

    asset_path: str = Field(
        ...,
        description="Path to the asset in the project (e.g. 'res://sprites/player.png' or 'res://audio/jump.wav').",
    )
    preset: ImportPreset | None = Field(
        default=None,
        description="Predefined import preset ('pixel_art_2d', 'high_quality_3d', 'uncompressed_audio').",
    )
    custom_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value dictionary of custom import parameters to set in the .import file.",
    )


class CreateCollisionPolygonInput(BaseModel):
    """Input model for godot_create_collision_polygon."""

    points: list[list[float]] = Field(
        ...,
        description=(
            "List of 2D coordinate pairs [[x1, y1], [x2, y2], ...] defining the polygon vertices (clockwise or counter-clockwise)."
        ),
    )
    polygon_type: PolygonType = Field(
        default=PolygonType.TWO_D,
        description="Collision polygon dimension: '2D' (CollisionPolygon2D) or '3D' (CollisionPolygon3D).",
    )
    parent_node_path: str = Field(
        default=".",
        description="Target parent node path in the active scene to attach the collision polygon to (e.g. 'Player' or '.').",
    )
    node_name: str = Field(
        default="CollisionPolygon",
        description="Name of the collision polygon node to create.",
    )
    depth: float = Field(
        default=1.0,
        description="Extrusion depth for 3D collision polygon (applicable only if polygon_type is '3D').",
    )
    disabled: bool = Field(
        default=False,
        description="Whether the collision polygon is initially disabled.",
    )
