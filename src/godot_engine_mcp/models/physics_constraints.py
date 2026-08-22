"""Pydantic models for Godot Physics Joints, Constraints & Ragdoll Simulation."""

from typing import Any

from pydantic import BaseModel, Field


class ConfigurePhysicsJointInput(BaseModel):
    """Input model for godot_configure_physics_joint."""

    joint_type: str = Field(
        default="hinge_3d",
        description="Joint type: 'pin_3d', 'hinge_3d', 'slider_3d', 'cone_twist_3d', 'generic_6dof_3d', 'pin_2d', 'groove_2d', or 'damped_spring_2d'.",
    )
    node_name: str = Field(
        default="PhysicsJoint",
        description="Name of the joint node in the scene tree.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene.",
    )
    node_a_path: str = Field(
        description="NodePath to the first physics body (RigidBody / StaticBody).",
    )
    node_b_path: str = Field(
        description="NodePath to the second physics body.",
    )
    position: list[float] | None = Field(
        default=None,
        description="Local 3D position [x, y, z] or 2D position [x, y] of the joint.",
    )
    rotation_deg: list[float] | None = Field(
        default=None,
        description="Local Euler rotation [rx, ry, rz] in degrees for 3D joints, or rotation angle for 2D.",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Dictionary of joint-specific parameters (e.g. angular limits, stiffness, damping, motor velocity, bias).",
    )


class GenerateRagdollInput(BaseModel):
    """Input model for godot_generate_ragdoll."""

    skeleton_node_path: str = Field(
        default="Skeleton3D",
        description="Path to the target Skeleton3D node in the active scene.",
    )
    bone_names: list[str] | None = Field(
        default=None,
        description="Optional list of specific bone names to generate PhysicalBone3D nodes for. If omitted, generates for all major limbs/torso.",
    )
    shape_type: str = Field(
        default="capsule",
        description="Collision shape type for the physical bones: 'capsule', 'box', or 'sphere'.",
    )
    mass_per_bone: float = Field(
        default=5.0,
        description="Mass in kg assigned to each physical bone.",
    )
    friction: float = Field(
        default=0.5,
        description="Friction coefficient for physical bone physics material.",
    )
    bounce: float = Field(
        default=0.0,
        description="Bounce/restitution factor (0.0 to 1.0).",
    )
