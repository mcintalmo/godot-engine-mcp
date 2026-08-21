"""Unit and headless tests for Godot Phase 14 tools (Automated Engine Test Runner & GUT Integration)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.gut_test import (
    GenerateGUTTestInput,
    RunGUTTestsInput,
)
from godot_mcp.tools.gut_test_tools import (
    handle_generate_gut_test,
    handle_run_gut_tests,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase14_tools_mock() -> None:
    """Test Phase 14 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Run GUT tests
    run_res = await handle_run_gut_tests(
        client,
        RunGUTTestsInput(test_dir="res://test/unit"),
    )
    assert "GUT Test Run" in run_res
    assert "ALL PASSED" in run_res
    assert "Total Tests" in run_res
    assert "Total Assertions" in run_res

    # 2. Generate GUT test suite
    gen_res = await handle_generate_gut_test(
        client,
        GenerateGUTTestInput(
            target_script_path="res://scripts/player.gd",
            test_file_path="res://test/unit/test_player.gd",
            test_methods=["jump", "attack"],
        ),
    )
    assert "GUT Test Scaffolded" in gen_res
    assert "res://test/unit/test_player.gd" in gen_res
    assert "res://scripts/player.gd" in gen_res


@pytest.mark.asyncio
async def test_phase14_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 14 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Run GUT tests headlessly
    run_res = await handle_run_gut_tests(client, RunGUTTestsInput())
    assert "GUT Test Run" in run_res

    # 2. Generate GUT test headlessly
    gen_res = await handle_generate_gut_test(
        client,
        GenerateGUTTestInput(
            target_script_path="res://scripts/enemy.gd",
            test_file_path="res://test/unit/test_enemy.gd",
        ),
    )
    assert "GUT Test Scaffolded" in gen_res
