"""Pydantic models for Godot 3D Skeletons, Bone Attachments & Inverse Kinematics."""

from pydantic import BaseModel, Field


class InspectSkeletonInput(BaseModel):
    """Input model for godot_inspect_skeleton."""

    skeleton_node_path: str = Field(
        default="Skeleton3D",
        description="Path to the target Skeleton3D or Skeleton2D node in the active scene.",
    )


class ConfigureBoneAttachmentInput(BaseModel):
    """Input model for godot_configure_bone_attachment."""

    skeleton_node_path: str = Field(
        default="Skeleton3D",
        description="Path to the parent Skeleton3D node.",
    )
    bone_name: str = Field(
        description="Name of the bone to attach to (e.g. 'RightHand', 'Head', 'Spine').",
    )
    attachment_node_name: str = Field(
        default="BoneAttachment3D",
        description="Name of the BoneAttachment3D node in the scene tree.",
    )
    position_offset: list[float] | None = Field(
        default=None,
        description="Local 3D position offset [x, y, z] relative to the bone.",
    )
    rotation_offset_deg: list[float] | None = Field(
        default=None,
        description="Local 3D Euler rotation offset [rx, ry, rz] in degrees.",
    )
    scale_offset: list[float] | None = Field(
        default=None,
        description="Local 3D scale [sx, sy, sz].",
    )


class SetupInverseKinematicsInput(BaseModel):
    """Input model for godot_setup_inverse_kinematics."""

    skeleton_node_path: str = Field(
        default="Skeleton3D",
        description="Path to the parent Skeleton3D node.",
    )
    ik_node_name: str = Field(
        default="SkeletonIK3D",
        description="Name of the SkeletonIK3D node to create or configure.",
    )
    root_bone: str = Field(
        description="Starting/root bone in the kinematic chain (e.g. 'UpperArm.R' or 'Thigh.L').",
    )
    tip_bone: str = Field(
        description="Ending/tip bone in the kinematic chain (e.g. 'Hand.R' or 'Foot.L').",
    )
    target_node_path: str | None = Field(
        default=None,
        description="Optional path to a target Node3D/Marker3D that the IK chain will track.",
    )
    interpolation: float = Field(
        default=1.0,
        description="Interpolation factor (0.0 = rest pose, 1.0 = full IK influence).",
    )
    max_iterations: int = Field(
        default=10,
        description="Maximum iterations per solve step.",
    )
    min_distance: float = Field(
        default=0.01,
        description="Minimum distance threshold before solver considers target reached.",
    )
    use_magnet: bool = Field(
        default=False,
        description="Whether to use a magnet vector for bending direction (e.g. elbow/knee orientation).",
    )
    magnet_position: list[float] | None = Field(
        default=None,
        description="3D position vector [x, y, z] for magnet direction.",
    )
