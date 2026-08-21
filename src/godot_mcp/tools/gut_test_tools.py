"""Tool handlers for Godot Unit Test (GUT) execution and test file scaffolding."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.gut_test import (
    GenerateGUTTestInput,
    RunGUTTestsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_run_gut_tests(
    client: GodotClient,
    params: RunGUTTestsInput,
) -> str:
    """Handle godot_run_gut_tests tool execution."""
    result = await client.run_gut_tests(
        test_dir=params.test_dir,
        test_file=params.test_file,
        prefix=params.prefix,
        config_file=params.config_file,
        extra_args=params.extra_args,
    )
    return format_result(result)


async def handle_generate_gut_test(
    client: GodotClient,
    params: GenerateGUTTestInput,
) -> str:
    """Handle godot_generate_gut_test tool execution."""
    result = await client.generate_gut_test(
        target_script_path=params.target_script_path,
        test_file_path=params.test_file_path,
        test_methods=params.test_methods,
    )
    return format_result(result)
