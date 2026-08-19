"""Pydantic models for Godot engine reflection, ClassDB introspection, doc queries, and shader validation."""

from pydantic import Field

from godot_mcp.models.common import BaseInputModel, ResponseFormat


class GetClassInfoInput(BaseInputModel):
    """Input for inspecting Godot engine classes via ClassDB."""

    class_name: str = Field(
        ...,
        description="Godot class name to inspect (e.g., 'CharacterBody2D', 'StandardMaterial3D', 'Node3D', 'Vector3')",
    )
    include_inherited: bool = Field(
        default=True,
        description="Whether to include properties, methods, signals, and constants from ancestor classes",
    )
    category: str = Field(
        default="all",
        description="Filter to specific metadata category: 'all', 'properties', 'methods', 'signals', 'enums', 'constants'",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class GetDocumentationInput(BaseInputModel):
    """Input for querying official Godot engine API documentation and method signatures."""

    query: str = Field(
        ...,
        description="Class name, method name, or property to look up (e.g., 'CharacterBody2D', 'move_and_slide', 'Node.get_children', 'StandardMaterial3D.albedo_color')",
    )
    category: str = Field(
        default="all",
        description="Filter documentation type: 'class', 'method', 'property', 'signal', or 'all'",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class ValidateShaderInput(BaseInputModel):
    """Input for validating Godot .gdshader code syntax and compilation."""

    shader_path: str | None = Field(
        default=None,
        description="Path to a .gdshader file to validate (e.g., 'res://shaders/water.gdshader')",
    )
    shader_code: str | None = Field(
        default=None,
        description="Raw GDShader code string to validate directly",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )
