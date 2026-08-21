"""Pydantic models for Godot Scene Tree and .tscn Diffing."""

from pydantic import BaseModel, Field


class DiffSceneInput(BaseModel):
    """Input model for godot_diff_scene."""

    scene_path: str | None = Field(
        default=None,
        description="Path to the saved .tscn file on disk to compare against the live edited scene in memory (e.g. 'res://scenes/main.tscn'). Defaults to current edited scene file.",
    )
    target_scene_path: str | None = Field(
        default=None,
        description="Optional path to a second .tscn file to perform a direct file-to-file scene diff.",
    )
