"""Pydantic models for Godot Play Mode and interactive debug controls."""

from enum import Enum

from pydantic import BaseModel, Field


class PlaySceneMode(str, Enum):
    """Play mode options for launching scenes."""

    MAIN = "main"
    CURRENT = "current"
    CUSTOM = "custom"


class PlaySceneInput(BaseModel):
    """Input model for godot_play_scene."""

    mode: PlaySceneMode = Field(
        default=PlaySceneMode.MAIN,
        description="Scene playback mode: 'main' (project main scene), 'current' (active scene tab in editor), or 'custom'.",
    )
    custom_scene_path: str | None = Field(
        default=None,
        description="Path to a custom scene to play when mode is 'custom' (e.g. 'res://levels/level_01.tscn').",
    )


class StopSceneInput(BaseModel):
    """Input model for godot_stop_scene."""


class GetPlayStateInput(BaseModel):
    """Input model for godot_get_play_state."""


class SetPlayStateInput(BaseModel):
    """Input model for godot_set_play_state."""

    pause: bool | None = Field(
        default=None,
        description="Set pause state of the running scene tree.",
    )
    time_scale: float | None = Field(
        default=None,
        description="Set global simulation speed multiplier (e.g. 0.2 for slow motion, 1.0 for normal, 2.0 for fast forward).",
    )
    step_frames: int | None = Field(
        default=None,
        description="Advance the simulation by N physics/process frames before re-pausing.",
    )
