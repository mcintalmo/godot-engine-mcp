from unittest.mock import AsyncMock, patch

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.script import FormatScriptInput
from godot_engine_mcp.tools.script_tools import handle_format_script


@pytest.fixture
def client(tmp_path):
    config = GodotConfig(project_path=str(tmp_path), executable_path="/mock/godot")
    return HeadlessCLIClient(config)


@pytest.mark.asyncio
async def test_format_script_path_not_found(client):
    result = await client.format_script(script_path="res://non_existent.gd")
    assert not result.success
    assert result.error_code == "PATH_NOT_FOUND"


@pytest.mark.asyncio
async def test_format_script_success(client, tmp_path):
    script_file = tmp_path / "player.gd"
    script_file.write_text("extends Node\nfunc _ready():\n  pass\n")

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Formatted player.gd", b"")
        mock_exec.return_value = mock_proc

        result = await client.format_script(script_path="res://player.gd")
        assert result.success
        assert "formatted" in result.message.lower()


@pytest.mark.asyncio
async def test_handle_format_script_tool(client, tmp_path):
    script_file = tmp_path / "test.gd"
    script_file.write_text("extends Node\n")

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Formatted test.gd", b"")
        mock_exec.return_value = mock_proc

        params = FormatScriptInput(script_path="res://test.gd")
        response = await handle_format_script(client, params)
        assert "formatted" in response.lower()
