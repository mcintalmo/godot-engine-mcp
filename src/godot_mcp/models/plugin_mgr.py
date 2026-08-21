"""Pydantic models for Godot Editor Plugin / Addon lifecycle management."""

from pydantic import BaseModel, Field


class GetPluginsInput(BaseModel):
    """Input model for godot_get_plugins."""

    enabled_only: bool = Field(
        default=False,
        description="Whether to only return currently enabled editor plugins.",
    )


class SetPluginStatusInput(BaseModel):
    """Input model for godot_set_plugin_status."""

    plugin_name: str = Field(
        description="Directory name or identifier of the plugin inside res://addons/ (e.g. 'godot_mcp', 'terrain_3d').",
    )
    enabled: bool = Field(
        default=True,
        description="True to enable the plugin, False to disable it.",
    )
