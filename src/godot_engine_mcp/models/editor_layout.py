"""Pydantic models for Godot Editor Workspace Layout and Dock Management."""

from pydantic import BaseModel, Field


class GetEditorLayoutInput(BaseModel):
    """Input model for godot_get_editor_layout."""

    include_open_scenes: bool = Field(
        default=True,
        description="Whether to include currently open scene tabs in the editor response.",
    )


class SetEditorLayoutInput(BaseModel):
    """Input model for godot_set_editor_layout."""

    main_screen: str | None = Field(
        default=None,
        description="Main workspace screen to activate ('2D', '3D', 'Script', or 'AssetLib').",
    )
    distraction_free_mode: bool | None = Field(
        default=None,
        description="Enable or disable distraction-free full-editor workspace mode.",
    )
    active_scene_path: str | None = Field(
        default=None,
        description="Optional scene file path (e.g. 'res://scenes/main.tscn') to open or activate in editor tabs.",
    )
