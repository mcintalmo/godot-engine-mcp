"""Unit and headless tests for Godot Phase 26 tools (3D Skeletons, Bone Attachments & Inverse Kinematics)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.skeleton_ik import (
    ConfigureBoneAttachmentInput,
    InspectSkeletonInput,
    SetupInverseKinematicsInput,
)
from godot_engine_mcp.tools.skeleton_ik_tools import (
    handle_configure_bone_attachment,
    handle_inspect_skeleton,
    handle_setup_inverse_kinematics,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase26_tools_mock() -> None:
    """Test Phase 26 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Inspect Skeleton
    skel_res = await handle_inspect_skeleton(
        client,
        InspectSkeletonInput(skeleton_node_path="Player/Skeleton3D"),
    )
    assert "Skeleton Hierarchy" in skel_res
    assert "Skeleton3D" in skel_res
    assert "Total Bones" in skel_res
    assert "Hand.R" in skel_res

    # 2. Configure Bone Attachment
    attach_res = await handle_configure_bone_attachment(
        client,
        ConfigureBoneAttachmentInput(
            skeleton_node_path="Player/Skeleton3D",
            bone_name="Hand.R",
            attachment_node_name="SwordSocket",
            position_offset=[0.0, 0.1, 0.0],
        ),
    )
    assert "Configured BoneAttachment3D" in attach_res
    assert "SwordSocket" in attach_res
    assert "Hand.R" in attach_res

    # 3. Setup Inverse Kinematics
    ik_res = await handle_setup_inverse_kinematics(
        client,
        SetupInverseKinematicsInput(
            skeleton_node_path="Player/Skeleton3D",
            ik_node_name="RightArmIK",
            root_bone="UpperArm.R",
            tip_bone="Hand.R",
            target_node_path="../AimTarget",
            interpolation=0.85,
            use_magnet=True,
            magnet_position=[0.0, 0.0, -1.0],
        ),
    )
    assert "Configured SkeletonIK3D" in ik_res
    assert "RightArmIK" in ik_res
    assert "UpperArm.R" in ik_res
    assert "Hand.R" in ik_res


@pytest.mark.asyncio
async def test_phase26_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 26 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Inspect Skeleton headlessly
    skel_res = await handle_inspect_skeleton(
        client,
        InspectSkeletonInput(skeleton_node_path="Skeleton3D"),
    )
    assert "Skeleton Hierarchy" in skel_res

    # 2. Configure Bone Attachment headlessly
    attach_res = await handle_configure_bone_attachment(
        client,
        ConfigureBoneAttachmentInput(
            skeleton_node_path="Skeleton3D",
            bone_name="Head",
            attachment_node_name="HatSocket",
        ),
    )
    assert "Configured BoneAttachment3D" in attach_res
    assert "HatSocket" in attach_res

    # 3. Setup Inverse Kinematics headlessly
    ik_res = await handle_setup_inverse_kinematics(
        client,
        SetupInverseKinematicsInput(
            skeleton_node_path="Skeleton3D",
            root_bone="Thigh.L",
            tip_bone="Foot.L",
        ),
    )
    assert "Configured SkeletonIK3D" in ik_res
    assert "Thigh.L" in ik_res
