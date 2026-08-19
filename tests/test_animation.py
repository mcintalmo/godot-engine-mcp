"""Unit and headless integration tests for animation track and keyframe creation."""

from pathlib import Path

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.animation import (
    CreateAnimationInput,
    InterpolationType,
    KeyframeData,
    LoopMode,
    TrackData,
    TrackType,
)
from godot_mcp.tools.animation_tools import handle_create_animation
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_animation_tool_mock() -> None:
    """Test create_animation tool handler with mock client."""
    client = MockGodotClient()

    res = await handle_create_animation(
        client,
        CreateAnimationInput(
            animation_name="walk",
            length=1.5,
            loop_mode=LoopMode.LINEAR,
            step=0.05,
            tracks=[
                TrackData(
                    track_type=TrackType.VALUE,
                    node_path="Sprite2D:position",
                    interpolation=InterpolationType.LINEAR,
                    keyframes=[
                        KeyframeData(time=0.0, value=[0.0, 0.0]),
                        KeyframeData(time=0.75, value=[10.0, -5.0]),
                        KeyframeData(time=1.5, value=[0.0, 0.0]),
                    ],
                ),
                TrackData(
                    track_type=TrackType.METHOD,
                    node_path="AudioPlayer",
                    keyframes=[
                        KeyframeData(
                            time=0.5,
                            value={"method": "play_footstep", "args": ["gravel"]},
                        )
                    ],
                ),
            ],
            animation_player_path="AnimationPlayer",
            save_path="res://animations/walk.tres",
        ),
    )
    assert "Created animation" in res
    assert "walk" in res
    assert "1.5s" in res
    assert "`2` tracks" in res
    assert "`4` keyframes" in res


@pytest.mark.asyncio
async def test_create_animation_headless() -> None:
    """Test creating an Animation resource and saving .tres headlessly with Godot CLI."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    proj_path = Path(__file__).parent / ".tmp_anim_proj"
    proj_path.mkdir(exist_ok=True)
    try:
        (proj_path / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="AnimTest"\n',
            encoding="utf-8",
        )

        cfg = GodotConfig(executable_path=exe, project_path=str(proj_path))
        client = HeadlessCLIClient(cfg)

        res = await handle_create_animation(
            client,
            CreateAnimationInput(
                animation_name="fade_out",
                length=1.0,
                loop_mode=LoopMode.NONE,
                tracks=[
                    TrackData(
                        track_type=TrackType.VALUE,
                        node_path="CanvasItem:modulate",
                        interpolation=InterpolationType.CUBIC,
                        keyframes=[
                            KeyframeData(
                                time=0.0,
                                value=[1.0, 1.0, 1.0, 1.0],
                                transition=1.0,
                            ),
                            KeyframeData(
                                time=1.0,
                                value=[1.0, 1.0, 1.0, 0.0],
                                transition=2.0,
                            ),
                        ],
                    ),
                    TrackData(
                        track_type=TrackType.POSITION_3D,
                        node_path="MeshInstance3D",
                        keyframes=[
                            KeyframeData(time=0.0, value=[0.0, 0.0, 0.0]),
                            KeyframeData(time=1.0, value=[0.0, 5.0, 0.0]),
                        ],
                    ),
                ],
                save_path="res://animations/fade_out.tres",
            ),
        )
        assert "Created animation" in res
        assert "fade_out" in res

        anim_file = proj_path / "animations" / "fade_out.tres"
        assert anim_file.exists()
        content = anim_file.read_text(encoding="utf-8")
        assert "CanvasItem:modulate" in content
        assert "MeshInstance3D" in content
    finally:
        import shutil

        shutil.rmtree(proj_path, ignore_errors=True)
