"""Pydantic models for animation track and keyframe authoring."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TrackType(str, Enum):
    """Type of animation track in Godot."""

    VALUE = "value"
    POSITION_3D = "position_3d"
    ROTATION_3D = "rotation_3d"
    SCALE_3D = "scale_3d"
    METHOD = "method"
    BEZIER = "bezier"
    AUDIO = "audio"


class LoopMode(str, Enum):
    """Looping behavior for Godot animations."""

    NONE = "none"
    LINEAR = "linear"
    PINGPONG = "pingpong"


class InterpolationType(str, Enum):
    """Interpolation curve between keyframes."""

    LINEAR = "linear"
    NEAREST = "nearest"
    CUBIC = "cubic"


class KeyframeData(BaseModel):
    """Individual keyframe point on an animation track."""

    time: float = Field(
        ...,
        description="Timestamp position of the keyframe in seconds (e.g. 0.0, 0.5, 1.0).",
    )
    value: Any = Field(
        ...,
        description=(
            "Keyframe target value. For property tracks: scalar float/int, string, bool, [x, y] Vector2, "
            "[x, y, z] Vector3, or [r, g, b, a] Color. For method tracks: {'method': 'name', 'args': []}."
        ),
    )
    transition: float = Field(
        default=1.0,
        description="Easing curve exponent (1.0 = linear, >1.0 = ease in, <1.0 = ease out).",
    )


class TrackData(BaseModel):
    """Configuration for a single track within an animation."""

    track_type: TrackType = Field(
        default=TrackType.VALUE,
        description="Track type: 'value' (property), 'position_3d', 'rotation_3d', 'scale_3d', 'method', etc.",
    )
    node_path: str = Field(
        ...,
        description="Target node path and property name (e.g. 'Sprite2D:position', 'Player:scale', or 'AudioPlayer').",
    )
    interpolation: InterpolationType = Field(
        default=InterpolationType.LINEAR,
        description="Track interpolation type ('linear', 'nearest', 'cubic').",
    )
    update_mode: str = Field(
        default="continuous",
        description="Update mode for value tracks: 'continuous', 'discrete', or 'capture'.",
    )
    keyframes: list[KeyframeData] = Field(
        default_factory=list,
        description="Ordered list of keyframes along the track timeline.",
    )


class CreateAnimationInput(BaseModel):
    """Input model for godot_create_animation."""

    animation_name: str = Field(
        ...,
        description="Name identifier for the animation (e.g. 'idle', 'walk', 'jump', 'fade_in').",
    )
    length: float = Field(
        default=1.0,
        description="Total duration of the animation in seconds.",
    )
    loop_mode: LoopMode = Field(
        default=LoopMode.NONE,
        description="Looping mode: 'none' (play once), 'linear' (loop continuously), 'pingpong' (forward and reverse).",
    )
    step: float = Field(
        default=0.1,
        description="Snapping time step in seconds for keyframe editing.",
    )
    tracks: list[TrackData] = Field(
        default_factory=list,
        description="List of animation tracks containing keyframes and targets.",
    )
    animation_player_path: str | None = Field(
        default=None,
        description="Optional target AnimationPlayer node path in the active scene to insert this animation into.",
    )
    save_path: str | None = Field(
        default=None,
        description="Optional .tres resource path to save the created Animation on disk (e.g. 'res://animations/walk.tres').",
    )
