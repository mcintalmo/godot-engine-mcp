"""Script management and validation models for Godot MCP."""

from pydantic import Field

from godot_engine_mcp.models.common import BaseInputModel, ResponseFormat


class ScriptDiagnostic(BaseInputModel):
    """Script syntax or compilation diagnostic."""

    line: int = Field(..., description="1-indexed line number of the diagnostic")
    column: int = Field(default=0, description="Column offset")
    message: str = Field(..., description="Diagnostic error or warning description")
    severity: str = Field(
        default="error", description="Severity ('error', 'warning', 'info')"
    )


class ValidateScriptInput(BaseInputModel):
    """Input for checking GDScript syntax and compilation validity."""

    script_path: str | None = Field(
        default=None,
        description="Path to existing script file (e.g., 'res://player.gd'). Specify either script_path or code_content.",
    )
    code_content: str | None = Field(
        default=None,
        description="Raw GDScript code snippet to validate if testing inline code.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class CreateScriptInput(BaseInputModel):
    """Input for creating or updating a GDScript file."""

    path: str = Field(
        ...,
        description="Destination resource path (e.g., 'res://scripts/player_controller.gd')",
    )
    content: str = Field(..., description="Complete GDScript source code")
    inherits: str = Field(
        default="Node",
        description="Base class name (e.g., CharacterBody2D, Control, Node)",
    )
    attach_to_node: str | None = Field(
        default=None,
        description="Optional node path in active scene to immediately attach this script to",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )
