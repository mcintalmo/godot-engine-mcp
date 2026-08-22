"""Pydantic models for Godot GPU MultiMesh Scattering & Foliage Systems."""

from pydantic import BaseModel, Field


class ScatterMultiMeshInput(BaseModel):
    """Input model for godot_scatter_multimesh."""

    mesh_path: str | None = Field(
        default=None,
        description="Path to the source Mesh resource (e.g. 'res://assets/tree.tres'). If omitted, a default 3D prism/box foliage mesh is used.",
    )
    node_name: str = Field(
        default="MultiMeshInstance3D",
        description="Name of the MultiMeshInstance3D node in the active scene.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene.",
    )
    instance_count: int = Field(
        default=100,
        description="Total number of GPU instances to scatter.",
    )
    area_size: list[float] = Field(
        default=[50.0, 50.0],
        description="Scattering area dimensions [width_x, depth_z] in meters.",
    )
    min_scale: float = Field(
        default=0.8,
        description="Minimum random scale multiplier.",
    )
    max_scale: float = Field(
        default=1.3,
        description="Maximum random scale multiplier.",
    )
    random_yaw: bool = Field(
        default=True,
        description="Whether to apply random Y-axis rotation (0 to 360 degrees) to each instance.",
    )
    align_to_surface: bool = Field(
        default=False,
        description="Whether to align instance up-vectors with terrain/surface normals.",
    )


class ConfigureLODManagerInput(BaseModel):
    """Input model for godot_configure_lod_manager."""

    node_path: str = Field(
        default="GeometryInstance3D",
        description="Path to the target GeometryInstance3D or MeshInstance3D node.",
    )
    visibility_range_begin: float = Field(
        default=0.0,
        description="Distance in meters where the mesh starts becoming visible.",
    )
    visibility_range_end: float = Field(
        default=150.0,
        description="Distance in meters where the mesh stops being visible.",
    )
    visibility_range_begin_margin: float = Field(
        default=10.0,
        description="Margin distance for cross-fade at begin range.",
    )
    visibility_range_end_margin: float = Field(
        default=10.0,
        description="Margin distance for cross-fade at end range.",
    )
    fade_mode: str = Field(
        default="self",
        description="LOD fade mode: 'disabled', 'self', or 'dependencies'.",
    )
