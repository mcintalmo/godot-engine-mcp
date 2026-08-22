"""Project settings, version info, and filesystem models for Godot MCP."""

from typing import Any

from pydantic import Field

from godot_engine_mcp.models.common import BaseInputModel, EngineMode, ResponseFormat


class GodotVersionInfo(BaseInputModel):
    """Engine version and environment information."""

    version_string: str = Field(
        ..., description="Full Godot version string (e.g., '4.7.1.stable')"
    )
    major: int = Field(..., description="Major version number")
    minor: int = Field(..., description="Minor version number")
    patch: int = Field(..., description="Patch version number")
    status: str = Field(default="stable", description="Release status string")
    build: str = Field(default="official", description="Build type")
    mode: EngineMode = Field(
        ..., description="Connection mode (live_editor or headless_cli)"
    )
    executable_path: str | None = Field(
        default=None, description="Path to Godot binary"
    )
    project_path: str | None = Field(
        default=None, description="Active Godot project root path"
    )


class GetVersionInput(BaseInputModel):
    """Input for retrieving Godot engine and project metadata."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class GetProjectSettingsInput(BaseInputModel):
    """Input for querying project.godot settings."""

    section: str | None = Field(
        default=None,
        description="Optional filter by section or prefix (e.g., 'application', 'display/window', 'autoload')",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class SetProjectSettingInput(BaseInputModel):
    """Input for setting a project configuration value."""

    name: str = Field(
        ...,
        min_length=1,
        description="Setting name in dot/slash format (e.g., 'application/config/name', 'display/window/size/viewport_width')",
    )
    value: Any = Field(
        ..., description="Setting value to write (string, int, float, bool, or list)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class ProjectFileInfo(BaseInputModel):
    """Metadata about a project asset or resource file."""

    path: str = Field(..., description="Resource path (e.g., 'res://scenes/main.tscn')")
    type_name: str = Field(
        ...,
        description="Resource type (e.g., PackedScene, GDScript, Texture2D, AudioStream)",
    )
    uid: str | None = Field(
        default=None, description="Godot 4+ unique resource identifier (uid://...)"
    )
    size_bytes: int = Field(default=0, ge=0, description="File size in bytes")


class ListProjectFilesInput(BaseInputModel):
    """Input for listing and querying project files/assets."""

    directory: str = Field(
        default="res://", description="Directory to search (default 'res://')"
    )
    extension_filter: list[str] = Field(
        default_factory=list,
        description="Optional file extensions to filter (e.g., ['gd', 'tscn', 'tres', 'png'])",
    )
    recursive: bool = Field(
        default=True, description="Whether to search subdirectories recursively"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )
