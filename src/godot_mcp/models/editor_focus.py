"""Pydantic models for Godot Editor selection, node focusing, and workspace navigation."""

from pydantic import BaseModel, Field


class SetEditorSelectionInput(BaseModel):
    """Input model for godot_set_editor_selection."""

    node_paths: list[str] = Field(
        description="List of node paths in the active scene to select in the Scene dock (e.g. ['Player', 'Enemies/Boss']).",
    )
    clear_previous: bool = Field(
        default=True,
        description="Whether to clear existing node selections before adding new ones.",
    )


class FocusNodeInput(BaseModel):
    """Input model for godot_focus_node."""

    node_path: str = Field(
        description="Path of the target node in the active scene to focus in the Inspector and viewport.",
    )
    main_screen: str | None = Field(
        default=None,
        description="Optional workspace main screen to switch to ('2D', '3D', 'Script').",
    )
