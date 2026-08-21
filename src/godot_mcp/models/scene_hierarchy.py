"""Pydantic models for Godot Scene Hierarchy Mutations and Packed Scene Instantiation."""

from pydantic import BaseModel, Field


class ReparentNodeInput(BaseModel):
    """Input model for godot_reparent_node."""

    node_path: str = Field(
        description="Path to the node to reparent (e.g. 'Player/Weapon' or 'World/Enemy').",
    )
    new_parent_path: str = Field(
        description="Path to the target parent node (e.g. 'Player/Hands' or '.').",
    )
    keep_global_transform: bool = Field(
        default=True,
        description="Whether to preserve the node's global transform when changing parents.",
    )
    new_index: int | None = Field(
        default=None,
        description="Optional child index under the new parent (e.g. 0 to make it the first child).",
    )


class DuplicateNodeInput(BaseModel):
    """Input model for godot_duplicate_node."""

    node_path: str = Field(
        description="Path to the node to duplicate (e.g. 'World/Coin' or 'UI/ItemButton').",
    )
    new_name: str | None = Field(
        default=None,
        description="Optional custom name for the duplicated node.",
    )
    target_parent_path: str | None = Field(
        default=None,
        description="Optional target parent path for the duplicate. Defaults to the same parent as the source node.",
    )
    duplicate_signals: bool = Field(
        default=False,
        description="Whether to duplicate signal connections.",
    )
    duplicate_groups: bool = Field(
        default=True,
        description="Whether to duplicate group memberships.",
    )
    duplicate_scripts: bool = Field(
        default=True,
        description="Whether to duplicate attached script and its state.",
    )


class SetNodeOwnerInput(BaseModel):
    """Input model for godot_set_node_owner."""

    node_path: str = Field(
        description="Path to the node whose owner should be updated.",
    )
    owner_node_path: str = Field(
        default=".",
        description="Path to the node that will own the target node (defaults to edited scene root '.').",
    )
    recursive: bool = Field(
        default=True,
        description="Whether to recursively update the owner for all children under the target node.",
    )
