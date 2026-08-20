"""End-to-end integration test simulating the live Godot Editor WebSocket bridge."""

import asyncio
import json
from typing import Any

import pytest
import websockets.exceptions
from mcp.types import CallToolResult
from websockets.legacy.server import WebSocketServerProtocol, serve

from godot_mcp.client.manager import ClientManager
from godot_mcp.config import GodotConfig
from godot_mcp.server import create_server


class MockGodotEditorBridgeServer:
    """Mock WebSocket server emulating the addons/godot_mcp GDScript bridge."""

    def __init__(self, host: str = "127.0.0.1", port: int = 3118) -> None:
        self.host = host
        self.port = port
        self._server: Any = None
        self.received_requests: list[dict[str, Any]] = []

    async def start(self) -> None:
        self._server = await serve(self._handler, self.host, self.port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handler(self, websocket: WebSocketServerProtocol) -> None:
        try:
            async for message in websocket:
                req = json.loads(message)
                self.received_requests.append(req)
                req_id = req.get("id")
                method = req.get("method")
                params = req.get("params", {})

                if method == "ping":
                    await websocket.send(
                        json.dumps(
                            {"jsonrpc": "2.0", "id": req_id, "result": {"pong": True}}
                        )
                    )
                elif method == "get_version":
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "success": True,
                                    "version_string": "4.7.1.stable",
                                    "major": 4,
                                    "minor": 7,
                                    "patch": 1,
                                    "mode": "live_editor",
                                },
                            }
                        )
                    )
                elif method == "list_nodes":
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "success": True,
                                    "nodes": [
                                        {
                                            "name": "Main",
                                            "node_path": ".",
                                            "type_name": "Node2D",
                                        },
                                        {
                                            "name": "Player",
                                            "node_path": "Player",
                                            "type_name": "CharacterBody2D",
                                        },
                                    ],
                                },
                            }
                        )
                    )
                elif method == "create_node":
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "success": True,
                                    "message": f"Created node '{params.get('name')}'",
                                    "node_path": f"{params.get('parent_path')}/{params.get('name')}".replace(
                                        "./", ""
                                    ),
                                },
                            }
                        )
                    )
                elif method == "take_screenshot":
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "success": True,
                                    "message": "Captured viewport screenshot (1920x1080)",
                                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                                    "width": 1920,
                                    "height": 1080,
                                },
                            }
                        )
                    )
                else:
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "success": True,
                                    "message": f"Operation '{method}' succeeded on Godot Editor",
                                    "data": params,
                                },
                            }
                        )
                    )
        except websockets.exceptions.ConnectionClosed, OSError:
            return


@pytest.mark.asyncio
async def test_e2e_live_editor_bridge_call() -> None:
    """Test full round-trip from FastMCP tool call through LiveBridgeClient to Godot WebSocket server."""
    port = 3119  # Dedicated test port
    bridge = MockGodotEditorBridgeServer(port=port)
    await bridge.start()
    await asyncio.sleep(0.1)

    try:
        cfg = GodotConfig(
            executable_path=None,
            project_path="/tmp/test_project",
            bridge_host="127.0.0.1",
            bridge_port=port,
            request_timeout=3.0,
        )

        client_mgr = ClientManager(cfg)
        if not await client_mgr.live_client.is_available():
            pytest.skip(
                "Localhost socket connections restricted in current sandbox environment."
            )

        server = create_server(client=client_mgr, config=cfg)

        def extract_text(res: Any) -> str:
            assert isinstance(res, CallToolResult)
            assert len(res.content) > 0
            return getattr(res.content[0], "text", "")

        # 1. Test live get_version
        v_res = await server.call_tool(
            "godot_get_version", {"params": {"response_format": "json"}}
        )
        v_text = extract_text(v_res)
        assert "4.7.1.stable" in v_text
        assert "live_editor" in v_text

        # 2. Test live list_nodes
        nodes_res = await server.call_tool("godot_list_nodes", {"params": {}})
        assert "CharacterBody2D" in extract_text(nodes_res)

        # 3. Test live create_node
        create_res = await server.call_tool(
            "godot_create_node",
            {
                "params": {
                    "type_name": "Sprite2D",
                    "name": "TestSprite",
                    "parent_path": ".",
                }
            },
        )
        assert "Created node 'TestSprite'" in extract_text(create_res)

        # 4. Test live take_screenshot
        shot_res = await server.call_tool("godot_take_screenshot", {"params": {}})
        assert "Captured viewport screenshot" in extract_text(shot_res)

        # Verify all RPCs were received by the bridge
        methods_received = [r.get("method") for r in bridge.received_requests]
        assert "get_version" in methods_received
        assert "list_nodes" in methods_received
        assert "create_node" in methods_received
        assert "take_screenshot" in methods_received

    finally:
        await bridge.stop()
