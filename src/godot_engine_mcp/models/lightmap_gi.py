"""Pydantic models for Godot Global Illumination & Baked Lighting."""

from pydantic import BaseModel, Field


class ConfigureLightmapGIInput(BaseModel):
    """Input model for godot_configure_lightmap_gi."""

    gi_type: str = Field(
        default="lightmap_gi",
        description="Type of global illumination or probe: 'lightmap_gi', 'voxel_gi', 'reflection_probe', or 'lightmap_probe'.",
    )
    node_name: str = Field(
        default="LightmapGI",
        description="Name of the GI / probe node in the active scene.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene.",
    )
    quality: str = Field(
        default="medium",
        description="Bake quality preset: 'low', 'medium', 'high', or 'ultra'.",
    )
    bounces: int = Field(
        default=3,
        description="Number of indirect light bounce iterations.",
    )
    use_denoiser: bool = Field(
        default=True,
        description="Whether to use AI/GPU denoising for baked lightmaps.",
    )
    denoiser_name: str = Field(
        default="jnlm",
        description="Lightmap denoiser algorithm: 'jnlm' or 'oidn'.",
    )
    size: list[float] | None = Field(
        default=None,
        description="Extents / size box [x, y, z] for VoxelGI or ReflectionProbe.",
    )
    origin_offset: list[float] | None = Field(
        default=None,
        description="Local origin offset [x, y, z] in meters.",
    )
    interior: bool = Field(
        default=False,
        description="Whether the probe / GI volume is in an interior environment ignoring sky light.",
    )


class BakeLightmapsInput(BaseModel):
    """Input model for godot_bake_lightmaps."""

    lightmap_node_path: str = Field(
        default="LightmapGI",
        description="Path to the LightmapGI or VoxelGI node in the active scene.",
    )
    bake_mode: str = Field(
        default="scene",
        description="Bake scope: 'scene' (entire scene) or 'selected' (selected static meshes only).",
    )
    save_path: str | None = Field(
        default=None,
        description="Optional file path to save the baked lightmap texture resource (e.g. 'res://baked_lightmaps.lmbake').",
    )
