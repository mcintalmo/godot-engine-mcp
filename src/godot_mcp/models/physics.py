"""Pydantic models for Godot 3D physics queries, raycasting, shape casting, and body state."""

from enum import Enum

from pydantic import BaseModel, Field


class ShapeType(str, Enum):
    """Supported 3D collision shape types."""

    SPHERE = "sphere"
    BOX = "box"
    CAPSULE = "capsule"
    CYLINDER = "cylinder"


class CastRay3DInput(BaseModel):
    """Input model for godot_cast_ray_3d."""

    from_pos: tuple[float, float, float] = Field(
        description="Starting coordinates (x, y, z) of the ray in world space.",
    )
    to_pos: tuple[float, float, float] = Field(
        description="Target end coordinates (x, y, z) of the ray in world space.",
    )
    collision_mask: int = Field(
        default=0xFFFFFFFF,
        description="Collision layer bitmask to query against (default 0xFFFFFFFF queries all 32 layers).",
    )
    collide_with_bodies: bool = Field(
        default=True,
        description="Whether the raycast should detect PhysicsBody3D colliders.",
    )
    collide_with_areas: bool = Field(
        default=False,
        description="Whether the raycast should detect Area3D colliders.",
    )
    hit_from_inside: bool = Field(
        default=False,
        description="If true, ray detects collisions starting from inside a shape.",
    )
    exclude_nodes: list[str] = Field(
        default_factory=list,
        description="List of node paths or names to exclude from raycast hits (e.g. ['Player', 'Weapon']).",
    )


class CastShape3DInput(BaseModel):
    """Input model for godot_cast_shape_3d."""

    shape_type: ShapeType = Field(
        default=ShapeType.SPHERE,
        description="Geometric shape primitive to cast ('sphere', 'box', 'capsule', 'cylinder').",
    )
    shape_params: dict[str, float] = Field(
        default_factory=dict,
        description="Geometric dimensions: sphere {'radius': 0.5}, box {'size_x': 1.0, 'size_y': 1.0, 'size_z': 1.0}, capsule/cylinder {'radius': 0.5, 'height': 2.0}.",
    )
    origin: tuple[float, float, float] = Field(
        description="World space origin coordinates (x, y, z) of the shape.",
    )
    motion: tuple[float, float, float] | None = Field(
        default=None,
        description="Optional motion vector (x, y, z) to sweep the shape along. If omitted, performs stationary overlap test.",
    )
    collision_mask: int = Field(
        default=0xFFFFFFFF,
        description="Collision layer bitmask to query against.",
    )
    max_results: int = Field(
        default=32,
        description="Maximum number of overlapping colliders to return.",
    )


class GetBodyPhysicsState3DInput(BaseModel):
    """Input model for godot_get_body_physics_state_3d."""

    node_path: str = Field(
        description="Path to the target physics body in the active scene (e.g. 'Player', 'Enemies/Boss', 'Vehicles/Car').",
    )


class SetPhysicsDebugModeInput(BaseModel):
    """Input model for godot_set_physics_debug_mode."""

    visible_collision_shapes: bool | None = Field(
        default=None,
        description="Toggle visible wireframe collision shapes in the editor / runtime preview.",
    )
    visible_paths: bool | None = Field(
        default=None,
        description="Toggle visible path visualization.",
    )
    visible_navigation: bool | None = Field(
        default=None,
        description="Toggle navigation mesh debug overlay.",
    )
    collision_debug_color: str | None = Field(
        default=None,
        description="Hex RGBA color for collision debug visualization (e.g. '#00ff7f7f').",
    )
