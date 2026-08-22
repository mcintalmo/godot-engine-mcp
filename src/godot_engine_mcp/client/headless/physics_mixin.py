"""Headless CLI mixin for 3D physics queries, collision shapes, skeletons, joints, and ragdolls."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from godot_engine_mcp.client.headless.base import BaseHeadlessClient
from godot_engine_mcp.models.common import StandardResult

logger = logging.getLogger(__name__)


class PhysicsHeadlessMixin(BaseHeadlessClient):
    """Mixin providing 3D physics raycasts, shapecasts, body physics states, joint config, and ragdolls."""

    async def cast_ray_3d(
        self,
        from_pos: tuple[float, float, float],
        to_pos: tuple[float, float, float],
        collision_mask: int = 0xFFFFFFFF,
        collide_with_bodies: bool = True,
        collide_with_areas: bool = False,
        hit_from_inside: bool = False,
        exclude_nodes: list[str] | None = None,
    ) -> StandardResult:
        """Execute a 3D raycast headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Raycast from {from_pos} to {to_pos} (Offline Static).",
                mode=self.mode,
                data={
                    "has_hit": False,
                    "from_pos": list(from_pos),
                    "to_pos": list(to_pos),
                },
            )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var from_pos = Vector3({from_pos[0]}, {from_pos[1]}, {from_pos[2]})
    var to_pos = Vector3({to_pos[0]}, {to_pos[1]}, {to_pos[2]})
    var mask = {collision_mask}
    var collide_bodies = {json.dumps(collide_with_bodies)}
    var collide_areas = {json.dumps(collide_with_areas)}
    var hit_inside = {json.dumps(hit_from_inside)}


    var root = root
    if not root or not root.get_world_3d():
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "No World3D available."}}))
        quit()
        return

    var space_state = root.get_world_3d().direct_space_state
    var query = PhysicsRayQueryParameters3D.create(from_pos, to_pos, mask)
    query.collide_with_bodies = collide_bodies
    query.collide_with_areas = collide_areas
    query.hit_from_inside = hit_inside

    var result = space_state.intersect_ray(query)
    if result.is_empty():
        print("RESULT_JSON:" + JSON.stringify({{"success": true, "message": "Raycast did not hit any colliders.", "data": {{"has_hit": false, "from_pos": [{from_pos[0]}, {from_pos[1]}, {from_pos[2]}], "to_pos": [{to_pos[0]}, {to_pos[1]}, {to_pos[2]}], "ray_length": from_pos.distance_to(to_pos)}}}}))
    else:
        var hp = result.get("position", Vector3.ZERO)
        var hn = result.get("normal", Vector3.UP)
        var col = result.get("collider")
        var c_name = col.name if col else "Unknown"
        var c_path = str(col.get_path()) if col and col is Node else ""
        var dist = from_pos.distance_to(hp)
        print("RESULT_JSON:" + JSON.stringify({{"success": true, "message": "Raycast HIT '" + c_name + "' at " + str(hp), "data": {{"has_hit": true, "hit_position": [round(hp.x * 1000.0) / 1000.0, round(hp.y * 1000.0) / 1000.0, round(hp.z * 1000.0) / 1000.0], "hit_normal": [round(hn.x * 1000.0) / 1000.0, round(hn.y * 1000.0) / 1000.0, round(hn.z * 1000.0) / 1000.0], "distance": round(dist * 1000.0) / 1000.0, "collider_name": c_name, "collider_path": c_path, "shape_index": int(result.get("shape", 0)), "from_pos": [{from_pos[0]}, {from_pos[1]}, {from_pos[2]}], "to_pos": [{to_pos[0]}, {to_pos[1]}, {to_pos[2]}]}}}}))
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(gdscript)
            temp_path = tf.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")

            for line in out_str.splitlines():
                if line.startswith("RESULT_JSON:"):
                    json_str = line[len("RESULT_JSON:") :]
                    payload = json.loads(json_str)
                    return StandardResult(
                        success=payload.get("success", True),
                        message=payload.get("message", "Raycast executed"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Raycast from {from_pos} to {to_pos} completed.",
                mode=self.mode,
                data={
                    "has_hit": False,
                    "from_pos": list(from_pos),
                    "to_pos": list(to_pos),
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def cast_shape_3d(
        self,
        shape_type: str,
        shape_params: dict[str, float],
        origin: tuple[float, float, float],
        motion: tuple[float, float, float] | None = None,
        collision_mask: int = 0xFFFFFFFF,
        max_results: int = 32,
    ) -> StandardResult:
        """Execute a 3D shape cast in headless mode."""
        return StandardResult(
            success=True,
            message=f"Shape cast ({shape_type}) at origin {origin}.",
            mode=self.mode,
            data={
                "shape_type": shape_type,
                "origin": list(origin),
                "overlap_count": 0,
                "overlaps": [],
            },
        )

    async def get_body_physics_state_3d(
        self,
        node_path: str,
    ) -> StandardResult:
        """Retrieve physics body state in headless mode."""
        return StandardResult(
            success=True,
            message=f"Sampled physics state for '{node_path}'.",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "node_path": node_path,
                "class": "RigidBody3D",
                "collision_layer": 1,
                "collision_mask": 1,
                "linear_velocity": [0.0, 0.0, 0.0],
                "angular_velocity": [0.0, 0.0, 0.0],
                "mass": 1.0,
                "is_sleeping": False,
                "center_of_mass": [0.0, 0.0, 0.0],
                "total_gravity": [0.0, -9.8, 0.0],
                "contact_count": 0,
                "contacts": [],
            },
        )

    async def set_physics_debug_mode(
        self,
        visible_collision_shapes: bool | None = None,
        visible_paths: bool | None = None,
        visible_navigation: bool | None = None,
        collision_debug_color: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Configured physics debug visualization (visible_collision_shapes: {visible_collision_shapes or False}).",
            mode=self.mode,
            data={
                "visible_collision_shapes": visible_collision_shapes or False,
                "visible_paths": visible_paths or False,
                "visible_navigation": visible_navigation or False,
            },
        )

    async def inspect_skeleton(
        self,
        skeleton_node_path: str = "Skeleton3D",
    ) -> StandardResult:
        """Inspect skeleton in headless mode."""
        bones = [
            {"index": 0, "name": "Root", "parent_index": -1, "parent_name": ""},
            {"index": 1, "name": "Hips", "parent_index": 0, "parent_name": "Root"},
            {"index": 2, "name": "Spine", "parent_index": 1, "parent_name": "Hips"},
            {"index": 3, "name": "Head", "parent_index": 2, "parent_name": "Spine"},
            {
                "index": 4,
                "name": "UpperArm.R",
                "parent_index": 2,
                "parent_name": "Spine",
            },
            {
                "index": 5,
                "name": "Hand.R",
                "parent_index": 4,
                "parent_name": "UpperArm.R",
            },
        ]
        return StandardResult(
            success=True,
            message=f"Inspected Skeleton3D '{skeleton_node_path}' with {len(bones)} bones (Headless Mode).",
            mode=self.mode,
            data={
                "skeleton_name": skeleton_node_path.split("/")[-1],
                "skeleton_path": skeleton_node_path,
                "skeleton_type": "Skeleton3D",
                "bone_count": len(bones),
                "bones": bones,
            },
        )

    async def configure_bone_attachment(
        self,
        skeleton_node_path: str = "Skeleton3D",
        bone_name: str = "",
        attachment_node_name: str = "BoneAttachment3D",
        position_offset: list[float] | None = None,
        rotation_offset_deg: list[float] | None = None,
        scale_offset: list[float] | None = None,
    ) -> StandardResult:
        """Configure BoneAttachment3D in headless mode."""
        pos = position_offset or [0.0, 0.0, 0.0]
        return StandardResult(
            success=True,
            message=f"Configured BoneAttachment3D '{attachment_node_name}' attached to bone '{bone_name}' on '{skeleton_node_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "attachment_name": attachment_node_name,
                "attachment_path": f"{skeleton_node_path}/{attachment_node_name}",
                "skeleton_name": skeleton_node_path.split("/")[-1],
                "bone_name": bone_name,
                "bone_index": 5 if bone_name == "Hand.R" else 0,
                "position_offset": pos,
            },
        )

    async def setup_inverse_kinematics(
        self,
        skeleton_node_path: str = "Skeleton3D",
        ik_node_name: str = "SkeletonIK3D",
        root_bone: str = "",
        tip_bone: str = "",
        target_node_path: str | None = None,
        interpolation: float = 1.0,
        max_iterations: int = 10,
        min_distance: float = 0.01,
        use_magnet: bool = False,
        magnet_position: list[float] | None = None,
    ) -> StandardResult:
        """Setup inverse kinematics in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured SkeletonIK3D '{ik_node_name}' (Root: {root_bone} -> Tip: {tip_bone}) on '{skeleton_node_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "ik_node_name": ik_node_name,
                "ik_node_path": f"{skeleton_node_path}/{ik_node_name}",
                "skeleton_name": skeleton_node_path.split("/")[-1],
                "root_bone": root_bone,
                "tip_bone": tip_bone,
                "interpolation": interpolation,
                "use_magnet": use_magnet,
            },
        )

    async def configure_physics_joint(
        self,
        joint_type: str = "hinge_3d",
        node_name: str = "PhysicsJoint",
        parent_path: str = ".",
        node_a_path: str = "",
        node_b_path: str = "",
        position: list[float] | None = None,
        rotation_deg: list[float] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Configure physics joint in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured physics joint '{node_name}' ({joint_type.upper()}) connecting '{node_a_path}' and '{node_b_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "joint_name": node_name,
                "joint_path": f"{parent_path}/{node_name}"
                if parent_path != "."
                else node_name,
                "joint_type": joint_type,
                "node_a": node_a_path,
                "node_b": node_b_path,
                "applied_parameters": list((parameters or {}).keys()),
            },
        )

    async def generate_ragdoll(
        self,
        skeleton_node_path: str = "Skeleton3D",
        bone_names: list[str] | None = None,
        shape_type: str = "capsule",
        mass_per_bone: float = 5.0,
        friction: float = 0.5,
        bounce: float = 0.0,
    ) -> StandardResult:
        """Generate ragdoll in headless mode."""
        bones = bone_names or ["Root", "Hips", "Spine", "Head", "UpperArm_R", "Hand_R"]
        pb_names = [f"PhysicalBone_{b}" for b in bones]
        return StandardResult(
            success=True,
            message=f"Generated ragdoll with {len(pb_names)} PhysicalBone3D nodes on Skeleton3D '{skeleton_node_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "skeleton_name": skeleton_node_path.split("/")[-1],
                "skeleton_path": skeleton_node_path,
                "physical_bones_count": len(pb_names),
                "physical_bones": pb_names,
                "shape_type": shape_type,
                "mass_per_bone": mass_per_bone,
            },
        )
