"""Debugging, execution, and screenshot tool handlers for Godot MCP."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.debug import (
    RunProjectInput,
    RunTestsInput,
    TakeScreenshotInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_run_project(client: GodotClient, params: RunProjectInput) -> str:
    """Run the Godot project in debug mode and capture console output."""
    result = await client.run_project(
        scene_path=params.scene_path,
        extra_arguments=params.extra_arguments,
        timeout_seconds=params.timeout_seconds,
    )
    return format_result(result, params.response_format)


async def handle_run_tests(client: GodotClient, params: RunTestsInput) -> str:
    """Run headless tests and parse results."""
    result = await client.run_tests(
        test_path=params.test_path,
        extra_arguments=params.extra_arguments,
        timeout_seconds=params.timeout_seconds,
    )
    return format_result(result, params.response_format)


async def handle_take_screenshot(
    client: GodotClient, params: TakeScreenshotInput
) -> str:
    """Capture a screenshot of the active Godot viewport or editor."""
    result = await client.take_screenshot(
        viewport_type=params.viewport_type,
        output_path=params.output_path,
    )
    return format_result(result, params.response_format)
