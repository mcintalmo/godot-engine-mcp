"""Pydantic models for Godot Resource UIDs and Asset Dependencies."""

from pydantic import BaseModel, Field


class GetUIDInput(BaseModel):
    """Input model for godot_get_uid."""

    path: str = Field(
        description="Resource path in the project (e.g. 'res://scenes/player.tscn', 'res://scripts/game_manager.gd', 'res://icon.svg').",
    )


class ResolveUIDInput(BaseModel):
    """Input model for godot_resolve_uid."""

    uid: str = Field(
        description="Resource UID string (e.g. 'uid://b8k14nx4v2a9', 'uid://c01p831y6n8q').",
    )


class GetDependenciesInput(BaseModel):
    """Input model for godot_get_dependencies."""

    path: str = Field(
        description="Resource or scene path to query dependencies for (e.g. 'res://scenes/main.tscn', 'res://materials/water_mat.tres').",
    )
