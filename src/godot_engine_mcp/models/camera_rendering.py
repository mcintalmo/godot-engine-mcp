"""Pydantic models for Godot Camera Presets, High-Res Viewport Capture & Rendering Pipeline."""

from pydantic import BaseModel, Field


class ConfigureCameraInput(BaseModel):
    """Input model for godot_configure_camera."""

    camera_node_path: str = Field(
        description="Path to the Camera2D or Camera3D node in the active scene.",
    )
    projection: str | None = Field(
        default=None,
        description="3D Camera projection mode: 'perspective', 'orthogonal', or 'frustum'.",
    )
    fov: float | None = Field(
        default=None,
        description="3D Camera field of view (FOV) in degrees (e.g. 75.0).",
    )
    size: float | None = Field(
        default=None,
        description="3D Camera size for orthogonal/frustum projection modes.",
    )
    near: float | None = Field(
        default=None,
        description="Near clipping plane distance.",
    )
    far: float | None = Field(
        default=None,
        description="Far clipping plane distance.",
    )
    current: bool | None = Field(
        default=None,
        description="Whether to make this camera the active/current camera.",
    )
    zoom: list[float] | None = Field(
        default=None,
        description="2D Camera zoom [x, y] (e.g. [1.5, 1.5]).",
    )
    position_smoothing_enabled: bool | None = Field(
        default=None,
        description="2D Camera position smoothing toggle.",
    )
    position_smoothing_speed: float | None = Field(
        default=None,
        description="2D Camera position smoothing speed.",
    )
    limits: dict[str, int] | None = Field(
        default=None,
        description="2D Camera limits dictionary (e.g. {'left': -1000, 'top': -500, 'right': 1000, 'bottom': 500}).",
    )


class ConfigureRenderSettingsInput(BaseModel):
    """Input model for godot_configure_render_settings."""

    msaa_2d: str | None = Field(
        default=None,
        description="2D MSAA anti-aliasing: 'disabled', '2x', '4x', '8x'.",
    )
    msaa_3d: str | None = Field(
        default=None,
        description="3D MSAA anti-aliasing: 'disabled', '2x', '4x', '8x'.",
    )
    screen_space_aa: str | None = Field(
        default=None,
        description="Screen-space anti-aliasing: 'disabled', 'fxaa'.",
    )
    use_taa: bool | None = Field(
        default=None,
        description="Temporal anti-aliasing (TAA) toggle.",
    )
    scaling_3d_mode: str | None = Field(
        default=None,
        description="3D viewport scaling mode: 'bilinear', 'fsr', 'fsr2'.",
    )
    scaling_3d_scale: float | None = Field(
        default=None,
        description="3D resolution scale factor between 0.25 and 2.0 (e.g. 1.0 for native, 0.77 for FSR quality).",
    )
    directional_shadow_size: int | None = Field(
        default=None,
        description="Directional light shadow map resolution (e.g. 2048, 4096).",
    )
    positional_shadow_atlas_size: int | None = Field(
        default=None,
        description="Positional (omni/spot) light shadow atlas resolution (e.g. 2048, 4096).",
    )
    vsync_mode: str | None = Field(
        default=None,
        description="Vertical sync mode: 'disabled', 'enabled', 'adaptive', 'mailbox'.",
    )


class CaptureViewportInput(BaseModel):
    """Input model for godot_capture_viewport."""

    output_path: str | None = Field(
        default=None,
        description="Optional file path to save the captured image (e.g. 'res://screenshots/main_view.png').",
    )
    max_width: int = Field(
        default=1280,
        description="Maximum image width in pixels for scaling (preserves aspect ratio).",
    )
    max_height: int = Field(
        default=720,
        description="Maximum image height in pixels for scaling.",
    )
    format: str = Field(
        default="png",
        description="Image encoding format: 'png', 'webp', or 'jpeg'.",
    )
    include_base64: bool = Field(
        default=False,
        description="Whether to include base64-encoded image data in the response for direct AI vision processing.",
    )
