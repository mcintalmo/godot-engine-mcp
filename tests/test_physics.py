"""Unit and headless integration tests for Godot 3D physics tools."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.physics import (
    CastRay3DInput,
    CastShape3DInput,
    GetBodyPhysicsState3DInput,
    SetPhysicsDebugModeInput,
    ShapeType,
)
from godot_engine_mcp.tools.physics_tools import (
    handle_cast_ray_3d,
    handle_cast_shape_3d,
    handle_get_body_physics_state_3d,
    handle_set_physics_debug_mode,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_physics_tools_mock() -> None:
    """Test 3D physics tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Cast Ray 3D
    ray_res = await handle_cast_ray_3d(
        client,
        CastRay3DInput(
            from_pos=(0.0, 10.0, 0.0),
            to_pos=(0.0, 0.0, 0.0),
        ),
    )
    assert "HIT" in ray_res
    assert "StaticFloor" in ray_res
    assert "10.0" in ray_res

    # 2. Cast Shape 3D
    shape_res = await handle_cast_shape_3d(
        client,
        CastShape3DInput(
            shape_type=ShapeType.SPHERE,
            shape_params={"radius": 1.0},
            origin=(0.0, 1.0, 0.0),
            motion=(0.0, -1.0, 0.0),
        ),
    )
    assert "Shape Cast (SPHERE)" in shape_res
    assert "Enemy" in shape_res
    assert "Motion Sweep" in shape_res

    # 3. Get Body Physics State 3D
    body_res = await handle_get_body_physics_state_3d(
        client,
        GetBodyPhysicsState3DInput(node_path="Player/RigidBody"),
    )
    assert "Physics Body" in body_res
    assert "Linear Velocity" in body_res
    assert "Active Contacts" in body_res

    # 4. Set Physics Debug Mode
    debug_res = await handle_set_physics_debug_mode(
        client,
        SetPhysicsDebugModeInput(visible_collision_shapes=True),
    )
    assert "visible_collision_shapes = true" in debug_res


@pytest.mark.asyncio
async def test_physics_headless_client() -> None:
    """Test 3D physics handling in HeadlessCLIClient."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # 1. Raycast in headless mode
    ray_res = await handle_cast_ray_3d(
        client,
        CastRay3DInput(
            from_pos=(0.0, 5.0, 0.0),
            to_pos=(0.0, 0.0, 0.0),
        ),
    )
    assert (
        "NO INTERSECTION" in ray_res or "completed" in ray_res or "Raycast" in ray_res
    )

    # 2. Shape cast in headless mode
    shape_res = await handle_cast_shape_3d(
        client,
        CastShape3DInput(
            shape_type=ShapeType.BOX,
            shape_params={"size_x": 1.0, "size_y": 1.0, "size_z": 1.0},
            origin=(0.0, 0.0, 0.0),
        ),
    )
    assert "Shape Cast (BOX)" in shape_res

    # 3. Body state in headless mode
    body_res = await handle_get_body_physics_state_3d(
        client,
        GetBodyPhysicsState3DInput(node_path="World/Box"),
    )
    assert "Box" in body_res
    assert "RigidBody3D" in body_res
