"""Pydantic models for Godot Live Script Lifecycle, Hot-Reload & Exported Property Reflection."""

from typing import Any

from pydantic import BaseModel, Field


class AttachScriptInput(BaseModel):
    """Input model for godot_attach_script."""

    node_path: str = Field(
        description="Path to the target node (e.g. 'Player' or 'Enemies/Goblin').",
    )
    script_path: str | None = Field(
        default=None,
        description="Path to the script file to attach (e.g. 'res://scripts/player.gd'). Pass null or empty string to detach script.",
    )
    initial_properties: dict[str, Any] | None = Field(
        default=None,
        description="Optional dictionary of initial exported property values to assign after attaching the script (e.g. {'speed': 350.0, 'health': 100}).",
    )


class ReloadScriptsInput(BaseModel):
    """Input model for godot_reload_scripts."""

    script_paths: list[str] | None = Field(
        default=None,
        description="Optional list of specific script paths to reload (e.g. ['res://scripts/player.gd']). If null or empty, reloads all loaded scripts in memory cache.",
    )


class GetNodeScriptInfoInput(BaseModel):
    """Input model for godot_get_node_script_info."""

    node_path: str = Field(
        description="Path to the target node whose script and exported properties should be inspected.",
    )
