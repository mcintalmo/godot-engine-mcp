"""Pydantic models for Godot WorldEnvironment, post-processing, and skybox lighting."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BackgroundMode(str, Enum):
    """Background rendering modes for Environment."""

    CLEAR_COLOR = "clear_color"
    CUSTOM_COLOR = "custom_color"
    SKY = "sky"
    COLOR = "color"
    CANVAS = "canvas"
    KEEP = "keep"


class SkyType(str, Enum):
    """Sky resource types."""

    PROCEDURAL = "procedural"
    PHYSICAL = "physical"
    PANORAMA = "panorama"


class TonemapMode(str, Enum):
    """Tonemapping algorithms."""

    LINEAR = "linear"
    REINHARDT = "reinhardt"
    FILMIC = "filmic"
    ACES = "aces"


class GlowBlendMode(str, Enum):
    """Glow/Bloom blending modes."""

    ADDITIVE = "additive"
    SCREEN = "screen"
    SOFTLIGHT = "softlight"
    REPLACE = "replace"


class ConfigureEnvironmentInput(BaseModel):
    """Input model for godot_configure_environment."""

    save_path: str | None = Field(
        default=None,
        description="File path to save the Environment as a standalone resource (e.g. 'res://env/default_env.tres').",
    )
    node_path: str | None = Field(
        default=None,
        description="Path to a WorldEnvironment node in the active scene to update directly (e.g. 'WorldEnvironment').",
    )
    background_mode: BackgroundMode | None = Field(
        default=None,
        description="Background mode ('clear_color', 'custom_color', 'sky').",
    )
    background_color: str | None = Field(
        default=None,
        description="Hex RGBA background color when background_mode is 'custom_color' (e.g. '#1a1b26').",
    )
    sky_type: SkyType | None = Field(
        default=None,
        description="Sky material generator ('procedural', 'physical', 'panorama').",
    )
    sky_params: dict[str, Any] | None = Field(
        default=None,
        description="Parameters for the sky material (e.g. {'sky_top_color': '#2a4468', 'ground_bottom_color': '#111922', 'sun_angle_max': 30.0}).",
    )
    ambient_light_source: str | None = Field(
        default=None,
        description="Ambient light source ('bg', 'disabled', 'color', 'sky').",
    )
    ambient_light_color: str | None = Field(
        default=None,
        description="Hex RGBA ambient light color.",
    )
    ambient_light_energy: float | None = Field(
        default=None,
        description="Ambient light energy scalar multiplier.",
    )
    tonemap_mode: TonemapMode | None = Field(
        default=None,
        description="Tonemap operator ('linear', 'reinhardt', 'filmic', 'aces').",
    )
    tonemap_exposure: float | None = Field(
        default=None,
        description="Tonemap exposure scalar.",
    )
    glow_enabled: bool | None = Field(
        default=None,
        description="Toggle HDR glow and bloom.",
    )
    glow_intensity: float | None = Field(
        default=None,
        description="Glow overall intensity scalar.",
    )
    glow_bloom: float | None = Field(
        default=None,
        description="Glow bloom threshold / blend factor.",
    )
    glow_blend_mode: GlowBlendMode | None = Field(
        default=None,
        description="Glow blend mode ('additive', 'screen', 'softlight', 'replace').",
    )
    ssao_enabled: bool | None = Field(
        default=None,
        description="Toggle Screen-Space Ambient Occlusion.",
    )
    ssao_radius: float | None = Field(
        default=None,
        description="SSAO sampling radius in meters.",
    )
    ssao_intensity: float | None = Field(
        default=None,
        description="SSAO occlusion intensity.",
    )
    ssil_enabled: bool | None = Field(
        default=None,
        description="Toggle Screen-Space Indirect Lighting.",
    )
    ssr_enabled: bool | None = Field(
        default=None,
        description="Toggle Screen-Space Reflections.",
    )
    volumetric_fog_enabled: bool | None = Field(
        default=None,
        description="Toggle volumetric fog simulation.",
    )
    volumetric_fog_density: float | None = Field(
        default=None,
        description="Volumetric fog density (e.g. 0.05).",
    )
    volumetric_fog_albedo: str | None = Field(
        default=None,
        description="Hex RGBA color for volumetric fog scattering.",
    )
