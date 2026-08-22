"""Pydantic models for Godot OpenXR & Spatial Computing."""

from pydantic import BaseModel, Field


class SetupXRRigInput(BaseModel):
    """Input model for godot_setup_xr_rig."""

    rig_name: str = Field(
        default="XROrigin3D",
        description="Name of the XROrigin3D root node in the scene tree.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene.",
    )
    enable_controllers: bool = Field(
        default=True,
        description="Whether to instantiate LeftHand and RightHand XRController3D nodes.",
    )
    enable_hand_tracking: bool = Field(
        default=False,
        description="Whether to configure OpenXR hand tracking skeleton and mesh generators.",
    )
    action_map_path: str | None = Field(
        default=None,
        description="Optional resource path to custom OpenXRActionMap (.tres).",
    )


class ConfigureXRPassthroughInput(BaseModel):
    """Input model for godot_configure_xr_passthrough."""

    xr_origin_path: str = Field(
        default="XROrigin3D",
        description="Path to the XROrigin3D node in the active scene.",
    )
    enable_passthrough: bool = Field(
        default=True,
        description="Whether to enable AR/MR camera passthrough mode.",
    )
    reference_space: str = Field(
        default="stage",
        description="OpenXR reference space: 'stage' (roomscale), 'local_floor' (standing/seated), or 'local' (seated/head-relative).",
    )
    foveated_rendering_level: str = Field(
        default="high",
        description="Foveated rendering optimization level: 'off', 'low', 'medium', or 'high'.",
    )
    dynamic_foveation: bool = Field(
        default=True,
        description="Whether to dynamically adjust foveation based on GPU frametime.",
    )
