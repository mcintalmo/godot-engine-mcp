from typing import Any, cast

import pytest
from mcp.types import GetPromptResult, TextContent

from godot_mcp.server import create_server
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_mcp_resources_and_prompts() -> None:
    """Test dynamic MCP resources and workflow prompt registration."""
    client = MockGodotClient()
    server = create_server(client=client)

    # 1. Test static resource: project settings
    proj_raw = await server.read_resource("godot://project/settings")
    proj_res = list(cast(list[Any], proj_raw))
    assert len(proj_res) > 0
    res_text = getattr(proj_res[0], "content", getattr(proj_res[0], "text", ""))
    assert "settings" in str(res_text)

    # 2. Test static resource: editor log
    log_raw = await server.read_resource("godot://logs/editor.log")
    log_res = list(cast(list[Any], log_raw))
    assert len(log_res) > 0
    log_text = getattr(log_res[0], "content", getattr(log_res[0], "text", ""))
    assert "Live Bridge active" in str(log_text)

    # 3. Test prompts
    p1 = cast(GetPromptResult, await server.get_prompt("fix_scene_warnings"))
    assert len(p1.messages) > 0
    assert isinstance(p1.messages[0].content, TextContent)
    assert "godot_list_nodes" in p1.messages[0].content.text

    p2 = cast(GetPromptResult, await server.get_prompt("create_rich_ui"))
    assert len(p2.messages) > 0
    assert isinstance(p2.messages[0].content, TextContent)
    assert "godot_create_scene" in p2.messages[0].content.text

    p3 = cast(GetPromptResult, await server.get_prompt("scaffold_character"))
    assert len(p3.messages) > 0
    assert isinstance(p3.messages[0].content, TextContent)
    assert "CharacterBody2D" in p3.messages[0].content.text
