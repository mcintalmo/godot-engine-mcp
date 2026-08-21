"""Pydantic models for Godot AnimationTree and State Machine graphs."""

from typing import Any

from pydantic import BaseModel, Field


class ConfigureAnimationTreeInput(BaseModel):
    """Input model for godot_configure_animation_tree."""

    node_path: str | None = Field(
        default=None,
        description="Path to an existing AnimationTree node in the active scene, or None to create a new one.",
    )
    parent_path: str | None = Field(
        default=None,
        description="Parent node path if creating a new AnimationTree (defaults to edited scene root).",
    )
    node_name: str = Field(
        default="AnimationTree",
        description="Name of the AnimationTree node.",
    )
    anim_player_path: str | None = Field(
        default=None,
        description="Relative node path or NodePath to the target AnimationPlayer (e.g. '../AnimationPlayer' or 'AnimationPlayer').",
    )
    tree_type: str = Field(
        default="state_machine",
        description="Root node type: 'state_machine' (AnimationNodeStateMachine) or 'blend_tree' (AnimationNodeBlendTree).",
    )
    active: bool = Field(
        default=True,
        description="Whether to set the AnimationTree active state to true.",
    )
    states: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of state definitions to add to the state machine, each containing 'name' and 'animation' (e.g. [{'name': 'idle', 'animation': 'Idle'}, {'name': 'walk', 'animation': 'Walk'}]).",
    )
    transitions: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of transition definitions between states, each containing 'from', 'to', optional 'advance_condition' (string bool condition), or 'advance_expression' (string expression).",
    )
    save_as_resource_path: str | None = Field(
        default=None,
        description="Optional path to save the tree root state machine resource as a .tres file.",
    )
