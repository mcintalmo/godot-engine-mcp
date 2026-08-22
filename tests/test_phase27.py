"""Unit and headless tests for Godot Phase 27 tools (Physics Joints, Constraints & Ragdoll Simulation)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.physics_constraints import (
    ConfigurePhysicsJointInput,
    GenerateRagdollInput,
)
from godot_engine_mcp.tools.physics_constraints_tools import (
    handle_configure_physics_joint,
    handle_generate_ragdoll,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase27_tools_mock() -> None:
    """Test Phase 27 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure Physics Joint
    joint_res = await handle_configure_physics_joint(
        client,
        ConfigurePhysicsJointInput(
            joint_type="hinge_3d",
            node_name="DoorHinge",
            node_a_path="DoorFrame/StaticBody3D",
            node_b_path="Door/RigidBody3D",
            position=[0.0, 1.0, 0.0],
            parameters={
                "angular_limit_lower": -1.57,
                "angular_limit_upper": 1.57,
            },
        ),
    )
    assert "Configured Physics Joint" in joint_res
    assert "DoorHinge" in joint_res
    assert "HINGE_3D" in joint_res
    assert "DoorFrame/StaticBody3D" in joint_res

    # 2. Generate Ragdoll
    ragdoll_res = await handle_generate_ragdoll(
        client,
        GenerateRagdollInput(
            skeleton_node_path="Enemy/Skeleton3D",
            bone_names=["Head", "Spine", "UpperArm_R", "Hand_R"],
            shape_type="capsule",
            mass_per_bone=4.5,
        ),
    )
    assert "Generated Ragdoll Physical Bones" in ragdoll_res
    assert "CAPSULE" in ragdoll_res
    assert "4.5 kg" in ragdoll_res


@pytest.mark.asyncio
async def test_phase27_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 27 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure Physics Joint headlessly
    joint_res = await handle_configure_physics_joint(
        client,
        ConfigurePhysicsJointInput(
            joint_type="pin_3d",
            node_name="RopePin",
            node_a_path="Anchor",
            node_b_path="Weight",
        ),
    )
    assert "Configured Physics Joint" in joint_res
    assert "RopePin" in joint_res

    # 2. Generate Ragdoll headlessly
    ragdoll_res = await handle_generate_ragdoll(
        client,
        GenerateRagdollInput(
            skeleton_node_path="Skeleton3D",
            shape_type="box",
        ),
    )
    assert "Generated Ragdoll Physical Bones" in ragdoll_res
    assert "BOX" in ragdoll_res
