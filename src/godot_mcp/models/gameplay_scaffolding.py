"""Pydantic models for Godot Gameplay AI & State Machine Scaffolding."""

from pydantic import BaseModel, Field


class ScaffoldStateMachineInput(BaseModel):
    """Input model for godot_scaffold_state_machine."""

    target_dir: str = Field(
        default="res://scripts/state_machine",
        description="Target project directory where generated GDScript files will be saved.",
    )
    machine_name: str = Field(
        default="CharacterStateMachine",
        description="Name of the StateMachine class and manager node.",
    )
    states: list[str] = Field(
        default_factory=lambda: ["Idle", "Move", "Jump", "Fall"],
        description="List of state names to generate (e.g. ['Idle', 'Move', 'Attack']).",
    )
    generate_node_hierarchy: bool = Field(
        default=True,
        description="Whether to automatically construct the StateMachine and child State nodes in the active edited scene.",
    )
    parent_node_path: str = Field(
        default=".",
        description="Parent node path in the active scene to attach the StateMachine node hierarchy to.",
    )


class DialogueOption(BaseModel):
    """Specification of a selectable dialogue choice/branch."""

    text: str = Field(
        description="Player choice text displayed in UI.",
    )
    target_id: str = Field(
        description="ID of the dialogue node to transition to when chosen.",
    )
    condition: str | None = Field(
        default=None,
        description="Optional GDScript boolean expression or variable check required for this option to appear.",
    )


class DialogueNode(BaseModel):
    """Specification of a single dialogue tree dialogue step."""

    id: str = Field(
        description="Unique identifier for this dialogue node (e.g. 'start', 'ask_quest').",
    )
    speaker: str = Field(
        description="Name of the character speaking.",
    )
    text: str = Field(
        description="Dialogue line or narrative text.",
    )
    options: list[DialogueOption] | None = Field(
        default=None,
        description="List of choices/responses available to the player.",
    )
    signals_on_enter: list[str] | None = Field(
        default=None,
        description="List of event/quest signals to emit when this node is reached.",
    )


class CreateDialogueResourceInput(BaseModel):
    """Input model for godot_create_dialogue_resource."""

    resource_path: str = Field(
        description="Target file path to save the dialogue tree (e.g. 'res://dialogue/npc_elder.json').",
    )
    format: str = Field(
        default="json",
        description="File format for the dialogue tree: 'json' or 'tres'.",
    )
    dialogue_nodes: list[DialogueNode] = Field(
        description="List of structured dialogue nodes forming the conversation graph.",
    )
