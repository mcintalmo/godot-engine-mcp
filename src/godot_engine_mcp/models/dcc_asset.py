"""Pydantic models for DCC / Blender 3D asset import, GLTF configuration, and model instancing."""

from enum import Enum

from pydantic import BaseModel, Field


class CollisionGenerationMode(str, Enum):
    """Collision shape generation modes for 3D model meshes."""

    NONE = "none"
    TRIMESH = "trimesh"
    CONVEX = "convex"
    MULTIPLE_CONVEX = "multiple_convex"
    BOX = "box"


class InstantiateModelInput(BaseModel):
    """Input model for godot_instantiate_model."""

    source_path: str = Field(
        description="Path to the 3D model asset (e.g. 'res://assets/models/chest.glb', '.gltf', '.blend', or '.tscn').",
    )
    parent_path: str | None = Field(
        default=None,
        description="Path of parent node in active scene tree. Defaults to edited scene root.",
    )
    node_name: str | None = Field(
        default=None,
        description="Optional custom node name for the instantiated model instance.",
    )
    position: tuple[float, float, float] | None = Field(
        default=None,
        description="World position coordinates (x, y, z) in meters.",
    )
    rotation: tuple[float, float, float] | None = Field(
        default=None,
        description="Rotation Euler angles (x, y, z) in degrees.",
    )
    scale: tuple[float, float, float] | None = Field(
        default=None,
        description="Scale multiplier (x, y, z). Defaults to (1.0, 1.0, 1.0).",
    )
    collision_mode: CollisionGenerationMode = Field(
        default=CollisionGenerationMode.NONE,
        description="Auto-generate collision shapes ('none', 'trimesh', 'convex', 'multiple_convex', 'box').",
    )
    save_as_scene_path: str | None = Field(
        default=None,
        description="Optional destination path to save the instantiated hierarchy as a new scene (e.g. 'res://scenes/chest.tscn').",
    )


class ConfigureGLTFImportInput(BaseModel):
    """Input model for godot_configure_gltf_import."""

    model_path: str = Field(
        description="Path to the 3D model file (e.g. 'res://assets/models/character.glb').",
    )
    import_as_skeleton_bones: bool | None = Field(
        default=None,
        description="Import armature hierarchy as Skeleton3D bones.",
    )
    generate_lods: bool | None = Field(
        default=None,
        description="Generate Level-of-Detail (LOD) meshes automatically.",
    )
    lod_threshold: float | None = Field(
        default=None,
        description="Mesh LOD distance metric threshold.",
    )
    generate_shadow_mesh: bool | None = Field(
        default=None,
        description="Generate optimized shadow meshes.",
    )
    extract_materials: bool | None = Field(
        default=None,
        description="Extract embedded materials to external .tres resources.",
    )
    reimport: bool = Field(
        default=True,
        description="Trigger immediate reimport via EditorFileSystem.",
    )
