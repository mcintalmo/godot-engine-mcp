"""Tool handlers for Godot Physics Joints, Constraints & Ragdoll Simulation."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.physics_constraints import (
    ConfigurePhysicsJointInput,
    GenerateRagdollInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_physics_joint(
    client: GodotClient,
    params: ConfigurePhysicsJointInput,
) -> str:
    """Handle godot_configure_physics_joint tool execution."""
    result = await client.configure_physics_joint(
        joint_type=params.joint_type,
        node_name=params.node_name,
        parent_path=params.parent_path,
        node_a_path=params.node_a_path,
        node_b_path=params.node_b_path,
        position=params.position,
        rotation_deg=params.rotation_deg,
        parameters=params.parameters,
    )
    return format_result(result)


async def handle_generate_ragdoll(
    client: GodotClient,
    params: GenerateRagdollInput,
) -> str:
    """Handle godot_generate_ragdoll tool execution."""
    result = await client.generate_ragdoll(
        skeleton_node_path=params.skeleton_node_path,
        bone_names=params.bone_names,
        shape_type=params.shape_type,
        mass_per_bone=params.mass_per_bone,
        friction=params.friction,
        bounce=params.bounce,
    )
    return format_result(result)
