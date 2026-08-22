"""Pydantic models for Godot Unit Test (GUT) and engine test runner."""

from pydantic import BaseModel, Field


class RunGUTTestsInput(BaseModel):
    """Input model for godot_run_gut_tests."""

    test_dir: str = Field(
        default="res://test/unit",
        description="Directory containing GUT test scripts (e.g. 'res://test/unit' or 'res://tests').",
    )
    test_file: str | None = Field(
        default=None,
        description="Optional single test file to run (e.g. 'res://test/unit/test_player.gd').",
    )
    prefix: str = Field(
        default="test_",
        description="Prefix used to match test files.",
    )
    config_file: str | None = Field(
        default=None,
        description="Optional custom GUT configuration file path (e.g. 'res://.gutconfig.json').",
    )
    extra_args: list[str] | None = Field(
        default=None,
        description="Optional list of additional CLI arguments to pass to GUT.",
    )


class GenerateGUTTestInput(BaseModel):
    """Input model for godot_generate_gut_test."""

    target_script_path: str = Field(
        description="Path to the GDScript file or scene to test (e.g. 'res://scripts/player.gd').",
    )
    test_file_path: str = Field(
        description="Destination path for the generated GUT test file (e.g. 'res://test/unit/test_player.gd').",
    )
    test_methods: list[str] | None = Field(
        default=None,
        description="Optional list of specific method names to scaffold test cases for.",
    )
