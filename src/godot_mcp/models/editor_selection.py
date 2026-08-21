"""Pydantic models for Godot Editor SceneTree selection management."""

from pydantic import BaseModel, Field


class GetSelectedNodesInput(BaseModel):
    """Input model for godot_get_selected_nodes."""

    include_properties: bool = Field(
        default=True,
        description="Whether to include key node properties (class, position, visible) for each selected node.",
    )


class SetSelectedNodesInput(BaseModel):
    """Input model for godot_set_selected_nodes."""

    node_paths: list[str] = Field(
        description="List of node paths in the active scene to select (e.g. ['Player', 'Player/Camera3D']).",
    )
    clear_previous: bool = Field(
        default=True,
        description="Whether to clear existing editor selection before selecting the specified nodes.",
    )
    inspect_primary: bool = Field(
        default=True,
        description="Whether to inspect/edit the first selected node in the editor Inspector dock.",
    )
