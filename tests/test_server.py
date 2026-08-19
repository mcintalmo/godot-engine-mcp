"""Unit tests for FastMCP server tool registration and routing."""

import pytest
from mcp.server import MCPServer
from mcp.types import CallToolResult

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.server import create_server


@pytest.mark.asyncio
async def test_server_tools_registered(mock_config: GodotConfig) -> None:
    """Test that all required tools are registered in FastMCP server."""
    client = HeadlessCLIClient(mock_config)
    server: MCPServer = create_server(client=client, config=mock_config)

    # Verify tool names registered
    tool_names = [tool.name for tool in await server.list_tools()]
    expected_tools = [
        "godot_get_version",
        "godot_get_project_settings",
        "godot_set_project_setting",
        "godot_list_project_files",
        "godot_list_nodes",
        "godot_get_node",
        "godot_create_node",
        "godot_modify_node",
        "godot_delete_node",
        "godot_connect_signal",
        "godot_instantiate_scene",
        "godot_save_scene",
        "godot_validate_script",
        "godot_create_script",
        "godot_run_project",
        "godot_run_tests",
        "godot_take_screenshot",
    ]

    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool registration: {expected}"


@pytest.mark.asyncio
async def test_server_call_get_project_settings(mock_config: GodotConfig) -> None:
    """Test executing a tool via FastMCP server."""
    client = HeadlessCLIClient(mock_config)
    server = create_server(client=client, config=mock_config)

    res = await server.call_tool(
        "godot_get_project_settings", {"params": {"section": "application"}}
    )
    assert isinstance(res, CallToolResult)
    assert len(res.content) > 0
    first_block = res.content[0]
    assert hasattr(first_block, "text")
    assert "Test Godot Project" in getattr(first_block, "text", "")
