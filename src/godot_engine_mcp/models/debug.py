"""Debugging, execution, test running, and screenshot models for Godot MCP."""

from pydantic import Field

from godot_engine_mcp.models.common import BaseInputModel, ResponseFormat


class RunProjectInput(BaseInputModel):
    """Input for launching the Godot project in debug mode."""

    scene_path: str | None = Field(
        default=None,
        description="Optional scene to run (e.g., 'res://levels/test_level.tscn'). Defaults to main scene.",
    )
    extra_arguments: list[str] = Field(
        default_factory=list,
        description="Optional command line arguments to pass to the running game",
    )
    timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=120,
        description="Maximum seconds to run and capture console logs before returning",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class RunTestsInput(BaseInputModel):
    """Input for running test scripts or GUT test suites headlessly."""

    test_path: str | None = Field(
        default=None,
        description="Path to specific test script or directory (e.g., 'res://test/unit/test_player.gd')",
    )
    extra_arguments: list[str] = Field(
        default_factory=list,
        description="Additional CLI arguments for test runner",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Test execution timeout in seconds",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )


class TakeScreenshotInput(BaseInputModel):
    """Input for capturing a screenshot of the active Godot viewport or editor."""

    viewport_type: str = Field(
        default="main_2d_3d",
        description="Viewport to capture: 'main_2d_3d', 'running_game', or 'editor_window'",
    )
    output_path: str | None = Field(
        default=None,
        description="Optional file path to save the PNG image. If None, returns base64 data URL.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Response format: 'markdown' or 'json'",
    )
