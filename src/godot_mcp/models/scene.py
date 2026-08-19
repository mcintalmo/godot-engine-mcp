"""Scene and node models for Godot MCP."""

from typing import Any

from pydantic import Field

from godot_mcp.models.common import BaseInputModel, ResponseFormat


class PropertyInfo(BaseInputModel):
    """Information about a node property."""

    name: str = Field(..., description="Property name")
    type_name: str = Field(
        ..., description="Godot Variant type name (e.g., Vector2, int, String)"
    )
    value: Any = Field(default=None, description="Current property value")
    is_exported: bool = Field(
        default=False, description="Whether the property is exported (@export)"
    )


class SignalConnection(BaseInputModel):
    """Information about a connected signal."""

    signal_name: str = Field(..., description="Name of the emitted signal")
    target_node_path: str = Field(
        ..., description="Target node path receiving the signal"
    )
    method_name: str = Field(..., description="Method name called on the target node")


class NodeInfo(BaseInputModel):
    """Detailed node representation in the scene tree."""

    name: str = Field(..., description="Node name")
    node_path: str = Field(
        ..., description="Absolute or relative NodePath in the scene"
    )
    type_name: str = Field(
        ..., description="Godot class name (e.g., CharacterBody2D, Camera3D, Control)"
    )
    parent_path: str | None = Field(default=None, description="Path to parent node")
    child_count: int = Field(
        default=0, ge=0, description="Total immediate children count"
    )
    script_path: str | None = Field(
        default=None, description="Attached GDScript resource path if any"
    )
    unique_name_in_owner: bool = Field(
        default=False, description="Whether node uses %UniqueName access"
    )
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Key node properties"
    )
    signals: list[SignalConnection] = Field(
        default_factory=list, description="Connected signals"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Configuration warnings"
    )


class ListNodesInput(BaseInputModel):
    """Input for listing nodes in the active scene."""

    root_path: str = Field(
        default=".", description="Root node path from which to traverse (default '.')"
    )
    max_depth: int = Field(
        default=4, ge=1, le=20, description="Maximum tree traversal depth"
    )
    include_properties: bool = Field(
        default=False, description="Whether to include node property dictionaries"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class GetNodeInput(BaseInputModel):
    """Input for retrieving a specific node's details."""

    node_path: str = Field(
        ..., description="Node path to inspect (e.g., 'Player/Sprite2D' or '.')"
    )
    include_inherited_properties: bool = Field(
        default=False,
        description="Whether to include all default/inherited engine properties",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class CreateNodeInput(BaseInputModel):
    """Input for creating and adding a node to the active scene."""

    type_name: str = Field(
        ...,
        description="Godot class name to instantiate (e.g., Sprite2D, CharacterBody2D, Area3D, Label, Panel)",
    )
    name: str = Field(
        ..., min_length=1, max_length=128, description="Name for the newly created node"
    )
    parent_path: str = Field(
        default=".",
        description="Node path of the parent node (default '.' for scene root)",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial properties to set on the node (e.g., {'position': [100, 200], 'visible': True})",
    )
    script_path: str | None = Field(
        default=None,
        description="Optional GDScript resource path to attach immediately (e.g., 'res://player.gd')",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class ModifyNodeInput(BaseInputModel):
    """Input for modifying properties of an existing node."""

    node_path: str = Field(..., description="Node path to modify")
    properties: dict[str, Any] = Field(
        ..., min_length=1, description="Dictionary of property names and new values"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class DeleteNodeInput(BaseInputModel):
    """Input for deleting a node from the scene."""

    node_path: str = Field(..., description="Node path of the node to remove")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class ConnectSignalInput(BaseInputModel):
    """Input for connecting a node signal to a target method."""

    source_node_path: str = Field(..., description="Path to node emitting the signal")
    signal_name: str = Field(
        ...,
        description="Name of the signal (e.g., 'pressed', 'body_entered', 'timeout')",
    )
    target_node_path: str = Field(..., description="Path to node receiving the signal")
    method_name: str = Field(..., description="Target method name on the receiver node")
    flags: int = Field(
        default=0,
        ge=0,
        description="Godot ConnectFlags bitmask (e.g., 0 for default, 1 for deferred)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class InstantiateSceneInput(BaseInputModel):
    """Input for instantiating a packed scene (.tscn) into the current scene."""

    scene_path: str = Field(
        ...,
        description="Resource path to the packed scene file (e.g., 'res://player.tscn')",
    )
    parent_path: str = Field(
        default=".", description="Node path to parent the instantiated instance under"
    )
    name: str | None = Field(
        default=None, description="Optional custom name for the instantiated node"
    )
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Optional override properties"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class SaveSceneInput(BaseInputModel):
    """Input for saving the active or specified scene."""

    scene_path: str | None = Field(
        default=None,
        description="Destination path (e.g., 'res://scenes/main.tscn'). If None, saves active scene in place.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class OpenSceneInput(BaseInputModel):
    """Input for opening a scene in the Godot Editor."""

    scene_path: str = Field(
        ...,
        description="Resource path to the scene to open (e.g., 'res://scenes/main.tscn')",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class CreateSceneInput(BaseInputModel):
    """Input for creating a brand new scene with its own dedicated root node."""

    scene_path: str = Field(
        ...,
        description="Destination path for the new scene (e.g., 'res://scenes/rich_gui.tscn')",
    )
    root_type: str = Field(
        default="Control",
        description="Godot class name for the root node (e.g., 'Control', 'Node2D', 'Node3D', 'CanvasLayer')",
    )
    root_name: str = Field(
        default="Root",
        description="Name for the root node (e.g., 'CyberDashboard', 'GameLevel')",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial properties for the root node (e.g., {'anchors_preset': 15})",
    )
    open_in_editor: bool = Field(
        default=True,
        description="Whether to open the newly created scene tab in the Godot Editor",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )
