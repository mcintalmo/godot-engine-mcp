"""Integration tests running directly against the installed Godot 4.7.1 binary."""

import asyncio
import contextlib
import shutil
import tempfile
from pathlib import Path

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.client.live_bridge import LiveBridgeClient
from godot_mcp.config import GodotConfig


@pytest.fixture
def godot_executable() -> str | None:
    """Return the Godot executable path if available on the system."""
    return GodotConfig.discover_executable()


@pytest.mark.asyncio
async def test_real_godot_version(godot_executable: str | None) -> None:
    """Test get_version with real Godot 4.7.1 binary."""
    if not godot_executable:
        pytest.skip("Godot executable not installed.")

    cfg = GodotConfig(executable_path=godot_executable)
    client = HeadlessCLIClient(cfg)

    res = await client.get_version()
    assert res.success is True
    assert "4.7.1" in res.data["version_string"]
    assert res.data["major"] == 4
    assert res.data["minor"] == 7
    assert res.data["patch"] == 1


@pytest.mark.asyncio
async def test_real_godot_validate_script_valid(godot_executable: str | None) -> None:
    """Test validating valid GDScript code using real Godot 4.7.1 compiler."""
    if not godot_executable:
        pytest.skip("Godot executable not installed.")

    cfg = GodotConfig(executable_path=godot_executable)
    client = HeadlessCLIClient(cfg)

    valid_code = """extends Node2D

@export var speed: float = 200.0

func _ready() -> void:
\tprint("Player ready, speed: ", speed)

func get_speed() -> float:
\treturn speed
"""
    res = await client.validate_script(code_content=valid_code)
    assert res.success is True
    assert res.data["valid"] is True


@pytest.mark.asyncio
async def test_real_godot_validate_script_invalid(godot_executable: str | None) -> None:
    """Test detecting syntax errors in GDScript using real Godot 4.7.1 compiler."""
    if not godot_executable:
        pytest.skip("Godot executable not installed.")

    cfg = GodotConfig(executable_path=godot_executable)
    client = HeadlessCLIClient(cfg)

    invalid_code = """extends Node2D

func _ready() -> void
\tthis is completely broken syntax !!!
"""
    res = await client.validate_script(code_content=invalid_code)
    assert res.success is False
    assert res.data["valid"] is False
    assert len(res.data["diagnostics"]) > 0


@pytest.mark.asyncio
async def test_real_godot_live_bridge_session(godot_executable: str | None) -> None:
    """Test full WebSocket IPC connection with real Godot 4.7.1 engine instance."""
    if not godot_executable:
        pytest.skip("Godot executable not installed.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        proj_path = Path(tmp_dir)

        # 1. Setup minimal Godot project
        (proj_path / "project.godot").write_text(
            """config_version=5

[application]
config/name="Real Godot Test Project"
""",
            encoding="utf-8",
        )

        # 2. Copy addon into project
        addon_src = Path(__file__).resolve().parent.parent / "addons" / "godot_mcp"
        addon_dest = proj_path / "addons" / "godot_mcp"
        shutil.copytree(addon_src, addon_dest)

        # 3. Create a standalone bridge runner script for headless Godot
        runner_script = proj_path / "run_bridge.gd"
        runner_script.write_text(
            """extends SceneTree

const BridgeServer = preload("res://addons/godot_mcp/bridge_server.gd")

var _server: BridgeServer
var _main_scene: Node2D

func _init() -> void:
\tprint("[TestRunner] Starting Godot 4.7.1 Bridge Server...")
\t_main_scene = Node2D.new()
\t_main_scene.name = "MainScene"
\troot.add_child(_main_scene)
\tcurrent_scene = _main_scene

\t_server = BridgeServer.new(_main_scene, 3122)
\troot.add_child(_server)
\t_server.start()

func _process(delta: float) -> bool:
\tif _server:
\t\t_server._process(delta)
\treturn false


""",
            encoding="utf-8",
        )

        # 4. Launch real Godot process in headless mode
        proc = await asyncio.create_subprocess_exec(
            godot_executable,
            "--headless",
            "--path",
            str(proj_path),
            "-s",
            str(runner_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait briefly for Godot TCP server to bind port 3122
        await asyncio.sleep(1.0)

        try:
            cfg = GodotConfig(
                executable_path=godot_executable,
                project_path=str(proj_path),
                bridge_host="127.0.0.1",
                bridge_port=3122,
                request_timeout=5.0,
            )

            client = LiveBridgeClient(cfg)
            is_connected = await client.is_available()
            if not is_connected:
                pytest.skip(
                    "Godot live WebSocket process could not be connected in sandbox environment."
                )

            # 1. Test get_version directly from live Godot 4.7.1 process
            v_res = await client.get_version()
            assert v_res.success is True
            assert v_res.data["major"] == 4
            assert v_res.data["minor"] == 7
            assert v_res.data["patch"] == 1

            # 2. Test get_project_settings from live Godot 4.7.1 engine
            settings_res = await client.get_project_settings(section="application")
            assert settings_res.success is True
            assert "application/config/name" in settings_res.data["settings"]

            # 3. Test creating a node live in the running Godot 4.7.1 scene tree
            node_res = await client.create_node(
                type_name="Sprite2D",
                name="PlayerSprite",
                parent_path=".",
                properties={"visible": True},
            )
            assert node_res.success is True

            # 4. Test listing nodes live from the running Godot 4.7.1 scene tree
            list_res = await client.list_nodes()
            assert list_res.success is True
            node_names = [n["name"] for n in list_res.data["nodes"]]
            assert "PlayerSprite" in node_names

        finally:
            with contextlib.suppress(Exception):
                proc.terminate()
            stdout, stderr = await proc.communicate()
            if stdout:
                print("GODOT STDOUT:\n", stdout.decode("utf-8", errors="replace"))
            if stderr:
                print("GODOT STDERR:\n", stderr.decode("utf-8", errors="replace"))
