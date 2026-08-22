"""Pydantic models for Godot Autoload singletons in project.godot."""

from pydantic import BaseModel, Field


class GetAutoloadsInput(BaseModel):
    """Input model for godot_get_autoloads."""


class SetAutoloadInput(BaseModel):
    """Input model for godot_set_autoload."""

    name: str = Field(
        description="Name of the autoload singleton (e.g. 'GameManager', 'GlobalAudio', 'EventBus').",
    )
    path: str | None = Field(
        default=None,
        description="Resource path to script or packed scene (e.g. 'res://scripts/game_manager.gd' or 'res://scenes/audio.tscn'). Required when adding or updating.",
    )
    is_singleton: bool = Field(
        default=True,
        description="Whether to expose the autoload in the global script scope as a singleton.",
    )
    remove: bool = Field(
        default=False,
        description="If true, removes the autoload singleton from project.godot.",
    )
