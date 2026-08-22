"""Tool handlers for Godot 3D Skeletons, Bone Attachments & Inverse Kinematics."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.skeleton_ik import (
    ConfigureBoneAttachmentInput,
    InspectSkeletonInput,
    SetupInverseKinematicsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_inspect_skeleton(
    client: GodotClient,
    params: InspectSkeletonInput,
) -> str:
    """Handle godot_inspect_skeleton tool execution."""
    result = await client.inspect_skeleton(
        skeleton_node_path=params.skeleton_node_path,
    )
    return format_result(result)


async def handle_configure_bone_attachment(
    client: GodotClient,
    params: ConfigureBoneAttachmentInput,
) -> str:
    """Handle godot_configure_bone_attachment tool execution."""
    result = await client.configure_bone_attachment(
        skeleton_node_path=params.skeleton_node_path,
        bone_name=params.bone_name,
        attachment_node_name=params.attachment_node_name,
        position_offset=params.position_offset,
        rotation_offset_deg=params.rotation_offset_deg,
        scale_offset=params.scale_offset,
    )
    return format_result(result)


async def handle_setup_inverse_kinematics(
    client: GodotClient,
    params: SetupInverseKinematicsInput,
) -> str:
    """Handle godot_setup_inverse_kinematics tool execution."""
    result = await client.setup_inverse_kinematics(
        skeleton_node_path=params.skeleton_node_path,
        ik_node_name=params.ik_node_name,
        root_bone=params.root_bone,
        tip_bone=params.tip_bone,
        target_node_path=params.target_node_path,
        interpolation=params.interpolation,
        max_iterations=params.max_iterations,
        min_distance=params.min_distance,
        use_magnet=params.use_magnet,
        magnet_position=params.magnet_position,
    )
    return format_result(result)
