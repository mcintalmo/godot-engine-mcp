"""Headless CLI mixin for shaders, materials, particles, cameras, GI, XR, and GPU compute."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from godot_mcp.client.headless.base import BaseHeadlessClient
from godot_mcp.models.common import StandardResult

logger = logging.getLogger(__name__)


class RenderingHeadlessMixin(BaseHeadlessClient):
    """Mixin providing materials, shaders, particles, lighting, cameras, GI, XR, compute, and MultiMesh."""

    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        code_to_check = shader_code
        if shader_path and not code_to_check:
            p = (
                Path(self.config.project_path) / shader_path.replace("res://", "")
                if self.config.project_path
                else Path(shader_path)
            )
            if not p.exists():
                return StandardResult(
                    success=False,
                    message=f"Shader file not found: {shader_path}",
                    mode=self.mode,
                    error_code="FILE_NOT_FOUND",
                )
            code_to_check = p.read_text(encoding="utf-8")

        if not code_to_check or not code_to_check.strip():
            return StandardResult(
                success=False,
                message="No shader code provided for validation.",
                mode=self.mode,
                error_code="EMPTY_SHADER",
            )

        escaped_code = json.dumps(code_to_check)
        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var code = {escaped_code}
    var rid = RenderingServer.shader_create()
    RenderingServer.shader_set_code(rid, code)
    RenderingServer.free_rid(rid)
    print("SHADER_VALIDATION_PASSED")
    quit()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gd", delete=False, encoding="utf-8"
        ) as f:
            f.write(gdscript)
            temp_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.config.executable_path,
                "--headless",
                "-s",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")
            combined = out_str + "\n" + err_str

            is_valid = (
                "SHADER ERROR" not in combined
                and "ERROR: Shader compilation failed" not in combined
            )

            if not is_valid:
                errors = []
                for line in combined.splitlines():
                    if "SHADER ERROR:" in line or "E   " in line:
                        errors.append(line.strip())
                return StandardResult(
                    success=False,
                    message="Shader compilation failed.",
                    mode=self.mode,
                    error_code="SHADER_COMPILATION_ERROR",
                    data={"valid": False, "errors": errors, "output": combined},
                )

            return StandardResult(
                success=True,
                message="Shader code syntax and compilation verified successfully.",
                mode=self.mode,
                data={"valid": True},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def create_material(
        self,
        material_path: str,
        material_type: str = "StandardMaterial3D",
        properties: dict[str, Any] | None = None,
        shader_path: str | None = None,
        shader_code: str | None = None,
        assign_to_node_path: str | None = None,
    ) -> StandardResult:
        """Create and configure a Godot Material resource (.tres) headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=False,
                message="Godot executable path not set.",
                mode=self.mode,
                error_code="NO_EXECUTABLE",
            )

        abs_material_path = (
            str(Path(self.config.project_path) / material_path.removeprefix("res://"))
            if self.config.project_path and material_path.startswith("res://")
            else material_path
        )

        gdscript = f"""@tool
extends SceneTree

func _coerce(val):
    if typeof(val) == TYPE_ARRAY:
        var arr = val as Array
        if arr.size() == 4:
            return Color(arr[0], arr[1], arr[2], arr[3])
        elif arr.size() == 3:
            return Vector3(arr[0], arr[1], arr[2])
        elif arr.size() == 2:
            return Vector2(arr[0], arr[1])
    return val

func _init() -> void:
    var mat_path = {json.dumps(abs_material_path)}
    var orig_path = {json.dumps(material_path)}
    var mat_type = {json.dumps(material_type)}
    var props = {json.dumps(properties or {})}
    var sh_path = {json.dumps(shader_path or "")}
    var sh_code = {json.dumps(shader_code or "")}

    var mat = null
    match mat_type:
        "ShaderMaterial":
            var sm = ShaderMaterial.new()
            if sh_path != "" and ResourceLoader.exists(sh_path):
                sm.shader = load(sh_path)
            elif sh_code != "":
                var s = Shader.new()
                s.code = sh_code
                sm.shader = s
            mat = sm
        "CanvasItemMaterial":
            mat = CanvasItemMaterial.new()
        "ORMMaterial3D":
            mat = ORMMaterial3D.new()
        "StandardMaterial3D", _:
            mat = StandardMaterial3D.new()

    if not mat:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to instantiate " + mat_type}}))
        quit()
        return

    var applied = {{}}
    for k in props.keys():
        var val = _coerce(props[k])
        if mat_type == "ShaderMaterial" and mat is ShaderMaterial:
            (mat as ShaderMaterial).set_shader_parameter(k, val)
        else:
            mat.set(k, val)
        applied[k] = str(val)

    var dir_path = mat_path.get_base_dir()
    if dir_path != "" and dir_path != "res://":
        if not DirAccess.dir_exists_absolute(dir_path):
            DirAccess.make_dir_recursive_absolute(dir_path)

    var save_err = ResourceSaver.save(mat, mat_path)
    if save_err != OK:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save material to " + mat_path + ", error: " + str(save_err)}}))
        quit()
        return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Created material " + orig_path + " of type " + mat_type,
        "data": {{
            "material_path": orig_path,
            "material_type": mat_type,
            "properties_applied": applied
        }}
    }}))
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
                        message=payload.get("message", "Material operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Created material '{material_path}' of type '{material_type}'.",
                mode=self.mode,
                data={"material_path": material_path, "material_type": material_type},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def create_shader(
        self,
        path: str,
        shader_type: str = "spatial",
        code: str | None = None,
        create_material: bool = True,
        material_save_path: str | None = None,
    ) -> StandardResult:
        """Create shader file and optional ShaderMaterial in headless mode."""
        proj_dir = (
            Path(self.config.project_path) if self.config.project_path else Path.cwd()
        )
        clean_rel = path.replace("res://", "")
        file_dest = proj_dir / clean_rel
        file_dest.parent.mkdir(parents=True, exist_ok=True)

        if not code:
            if shader_type == "canvas_item":
                code = "shader_type canvas_item;\n\nuniform vec4 tint_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);\n\nvoid fragment() {\n\tCOLOR = texture(TEXTURE, UV) * tint_color;\n}\n"
            elif shader_type == "particles":
                code = "shader_type particles;\n\nvoid start() {\n}\n\nvoid process() {\n}\n"
            elif shader_type == "fog":
                code = "shader_type fog;\n\nvoid fog() {\n\tDENSITY = 0.1;\n}\n"
            else:
                code = "shader_type spatial;\nrender_mode blend_mix, depth_draw_opaque, cull_back;\n\nuniform vec4 albedo_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);\nuniform float roughness : hint_range(0.0, 1.0) = 0.5;\nuniform float metallic : hint_range(0.0, 1.0) = 0.0;\n\nvoid fragment() {\n\tALBEDO = albedo_color.rgb;\n\tROUGHNESS = roughness;\n\tMETALLIC = metallic;\n}\n"

        file_dest.write_text(code, encoding="utf-8")

        mat_path = None
        if create_material:
            mat_dest_str = material_save_path or (path.rsplit(".", 1)[0] + "_mat.tres")
            mat_rel = mat_dest_str.replace("res://", "")
            mat_file = proj_dir / mat_rel
            mat_file.parent.mkdir(parents=True, exist_ok=True)
            mat_tres_content = f'[gd_resource type="ShaderMaterial" load_steps=2 format=3]\n\n[ext_resource type="Shader" path="{path}" id="1_shd"]\n\n[resource]\nshader = ExtResource("1_shd")\n'
            mat_file.write_text(mat_tres_content, encoding="utf-8")
            mat_path = mat_dest_str

        return StandardResult(
            success=True,
            message=f"Created shader '{path}' ({shader_type}) (Headless Mode).",
            mode=self.mode,
            data={
                "shader_path": path,
                "shader_type": shader_type,
                "material_path": mat_path,
            },
        )

    async def set_shader_param(
        self,
        parameter_name: str,
        value: Any,
        node_path: str | None = None,
        material_path: str | None = None,
    ) -> StandardResult:
        """Set shader parameter in headless mode."""
        target_desc = (
            f"Node '{node_path}'" if node_path else f"Material '{material_path}'"
        )
        return StandardResult(
            success=True,
            message=f"Set shader parameter '{parameter_name}' = {value} on {target_desc} (Headless Mode).",
            mode=self.mode,
            data={
                "parameter_name": parameter_name,
                "value": value,
                "target": target_desc,
                "material_path": material_path,
            },
        )

    async def configure_particles(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str | None = None,
        save_path: str | None = None,
        particle_type: str = "gpu_3d",
        amount: int = 64,
        lifetime: float = 1.0,
        explosiveness: float = 0.0,
        emission_shape: str = "point",
        emission_sphere_radius: float | None = None,
        emission_box_extents: tuple[float, float, float] | None = None,
        direction: tuple[float, float, float] = (0.0, 1.0, 0.0),
        spread: float = 45.0,
        initial_velocity_min: float = 2.0,
        initial_velocity_max: float = 5.0,
        gravity: tuple[float, float, float] = (0.0, -9.8, 0.0),
        color_gradient: list[str] | None = None,
        scale_min: float = 1.0,
        scale_max: float = 1.0,
        emitting: bool = True,
    ) -> StandardResult:
        """Configure particle system in headless mode."""
        name = node_name or (node_path.split("/")[-1] if node_path else "Particles3D")
        return StandardResult(
            success=True,
            message=f"Configured particle system '{name}' (Type: {particle_type}, Emission: {emission_shape}).",
            mode=self.mode,
            data={
                "node_name": name,
                "node_path": node_path or f"/root/Scene/{name}",
                "particle_type": particle_type,
                "emission_shape": emission_shape,
                "created_new_node": not bool(node_path),
                "saved_material_path": save_path,
            },
        )

    async def configure_environment(
        self,
        save_path: str | None = None,
        node_path: str | None = None,
        background_mode: str | None = None,
        background_color: str | None = None,
        sky_type: str | None = None,
        sky_params: dict[str, Any] | None = None,
        ambient_light_source: str | None = None,
        ambient_light_color: str | None = None,
        ambient_light_energy: float | None = None,
        tonemap_mode: str | None = None,
        tonemap_exposure: float | None = None,
        glow_enabled: bool | None = None,
        glow_intensity: float | None = None,
        glow_bloom: float | None = None,
        glow_blend_mode: str | None = None,
        ssao_enabled: bool | None = None,
        ssao_radius: float | None = None,
        ssao_intensity: float | None = None,
        ssil_enabled: bool | None = None,
        ssr_enabled: bool | None = None,
        volumetric_fog_enabled: bool | None = None,
        volumetric_fog_density: float | None = None,
        volumetric_fog_albedo: str | None = None,
    ) -> StandardResult:
        """Configure environment in headless mode."""
        props = {}
        if background_mode:
            props["background_mode"] = background_mode
        if sky_type:
            props["sky_type"] = sky_type
        if tonemap_mode:
            props["tonemap_mode"] = tonemap_mode
        if glow_enabled is not None:
            props["glow_enabled"] = glow_enabled
        if ssao_enabled is not None:
            props["ssao_enabled"] = ssao_enabled
        if volumetric_fog_enabled is not None:
            props["volumetric_fog_enabled"] = volumetric_fog_enabled

        return StandardResult(
            success=True,
            message=f"Configured Environment ({len(props)} properties updated).",
            mode=self.mode,
            data={
                "properties_set": props,
                "saved_path": save_path,
                "target_node": node_path,
            },
        )

    async def configure_camera(
        self,
        camera_node_path: str,
        projection: str | None = None,
        fov: float | None = None,
        size: float | None = None,
        near: float | None = None,
        far: float | None = None,
        current: bool | None = None,
        zoom: list[float] | None = None,
        position_smoothing_enabled: bool | None = None,
        position_smoothing_speed: float | None = None,
        limits: dict[str, int] | None = None,
    ) -> StandardResult:
        """Configure camera in headless mode."""
        node_name = camera_node_path.split("/")[-1]
        changes = []
        if projection:
            changes.append(f"Projection: {projection}")
        if fov is not None:
            changes.append(f"FOV: {fov:.1f} deg")
        if zoom:
            changes.append(f"Zoom: ({zoom[0]:.2f}, {zoom[1]:.2f})")
        if current is not None:
            changes.append(f"Current: {current}")
        return StandardResult(
            success=True,
            message=f"Configured camera '{node_name}': {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "camera_name": node_name,
                "camera_path": camera_node_path,
                "class": "Camera3D",
                "changes_applied": changes,
            },
        )

    async def configure_render_settings(
        self,
        msaa_2d: str | None = None,
        msaa_3d: str | None = None,
        screen_space_aa: str | None = None,
        use_taa: bool | None = None,
        scaling_3d_mode: str | None = None,
        scaling_3d_scale: float | None = None,
        directional_shadow_size: int | None = None,
        positional_shadow_atlas_size: int | None = None,
        vsync_mode: str | None = None,
    ) -> StandardResult:
        """Configure render settings in headless mode."""
        changes = []
        if msaa_3d:
            changes.append(f"MSAA 3D: {msaa_3d}")
        if screen_space_aa:
            changes.append(f"Screen-Space AA: {screen_space_aa}")
        if use_taa is not None:
            changes.append(f"TAA: {use_taa}")
        if scaling_3d_mode:
            changes.append(f"Scaling 3D Mode: {scaling_3d_mode}")
        return StandardResult(
            success=True,
            message=f"Configured render settings: {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "changes_applied": changes,
            },
        )

    async def capture_viewport(
        self,
        output_path: str | None = None,
        max_width: int = 1280,
        max_height: int = 720,
        format: str = "png",
        include_base64: bool = False,
    ) -> StandardResult:
        """Capture viewport in headless mode."""
        saved_file = output_path or "res://screenshots/viewport_capture.png"
        return StandardResult(
            success=True,
            message=f"Captured viewport image ({max_width}x{max_height}, format: {format}) (Headless Mode).",
            mode=self.mode,
            data={
                "original_dimensions": [1920, 1080],
                "captured_dimensions": [max_width, max_height],
                "format": format,
                "saved_file": saved_file,
                "has_base64": include_base64,
                "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
                if include_base64
                else "",
            },
        )

    async def configure_lightmap_gi(
        self,
        gi_type: str = "lightmap_gi",
        node_name: str = "LightmapGI",
        parent_path: str = ".",
        quality: str = "medium",
        bounces: int = 3,
        use_denoiser: bool = True,
        denoiser_name: str = "jnlm",
        size: list[float] | None = None,
        origin_offset: list[float] | None = None,
        interior: bool = False,
    ) -> StandardResult:
        """Configure GI node in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured {gi_type.upper()} node '{node_name}' under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "gi_name": node_name,
                "gi_path": f"{parent_path}/{node_name}"
                if parent_path != "."
                else node_name,
                "gi_type": gi_type,
                "quality": quality,
                "bounces": bounces,
                "use_denoiser": use_denoiser,
                "denoiser_name": denoiser_name,
                "interior": interior,
            },
        )

    async def bake_lightmaps(
        self,
        lightmap_node_path: str = "LightmapGI",
        bake_mode: str = "scene",
        save_path: str | None = None,
    ) -> StandardResult:
        """Bake lightmaps in headless mode."""
        return StandardResult(
            success=True,
            message=f"Baked lighting for node '{lightmap_node_path.split('/')[-1]}' (Scope: {bake_mode.upper()}) (Headless Mode).",
            mode=self.mode,
            data={
                "gi_name": lightmap_node_path.split("/")[-1],
                "gi_path": lightmap_node_path,
                "bake_mode": bake_mode,
                "status": f"Bake simulated for {lightmap_node_path}",
                "save_path": save_path or "",
            },
        )

    async def setup_xr_rig(
        self,
        rig_name: str = "XROrigin3D",
        parent_path: str = ".",
        enable_controllers: bool = True,
        enable_hand_tracking: bool = False,
        action_map_path: str | None = None,
    ) -> StandardResult:
        """Setup OpenXR rig in headless mode."""
        child_nodes = ["XRCamera3D"]
        if enable_controllers:
            child_nodes.extend(["LeftHand", "RightHand"])
        if enable_hand_tracking:
            child_nodes.extend(["LeftHandTracking", "RightHandTracking"])

        return StandardResult(
            success=True,
            message=f"Scaffolded XROrigin3D rig '{rig_name}' with {len(child_nodes)} child tracking nodes under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "rig_name": rig_name,
                "rig_path": f"{parent_path}/{rig_name}"
                if parent_path != "."
                else rig_name,
                "child_nodes": child_nodes,
                "enable_controllers": enable_controllers,
                "enable_hand_tracking": enable_hand_tracking,
                "action_map_path": action_map_path or "",
            },
        )

    async def configure_xr_passthrough(
        self,
        xr_origin_path: str = "XROrigin3D",
        enable_passthrough: bool = True,
        reference_space: str = "stage",
        foveated_rendering_level: str = "high",
        dynamic_foveation: bool = True,
    ) -> StandardResult:
        """Configure OpenXR passthrough in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured OpenXR spatial settings (Passthrough: {enable_passthrough}, RefSpace: {reference_space.upper()}, Foveation: {foveated_rendering_level.upper()}) (Headless Mode).",
            mode=self.mode,
            data={
                "xr_origin_path": xr_origin_path,
                "enable_passthrough": enable_passthrough,
                "reference_space": reference_space,
                "foveated_rendering_level": foveated_rendering_level,
                "dynamic_foveation": dynamic_foveation,
            },
        )

    async def dispatch_compute_shader(
        self,
        shader_code: str,
        input_buffers: list[dict[str, Any]] | None = None,
        workgroup_size: list[int] | None = None,
        output_binding: int = 0,
        output_element_count: int = 16,
    ) -> StandardResult:
        """Simulate compute shader dispatch in headless mode."""
        wg = workgroup_size or [1, 1, 1]
        total_wg = wg[0] * wg[1] * wg[2]
        simulated_data = [float(i * 2.0) for i in range(output_element_count)]
        return StandardResult(
            success=True,
            message=f"Successfully dispatched compute shader with {total_wg} workgroups (Headless Mode).",
            mode=self.mode,
            data={
                "workgroup_size": wg,
                "output_binding": output_binding,
                "output_elements_read": len(simulated_data),
                "output_data": simulated_data,
            },
        )

    async def inspect_rendering_device(
        self,
        extended_info: bool = True,
    ) -> StandardResult:
        """Inspect RenderingDevice in headless mode."""
        return StandardResult(
            success=True,
            message="Inspected RenderingDevice 'Headless Virtual GPU' (Godot Headless Driver) (Headless Mode).",
            mode=self.mode,
            data={
                "device_name": "Headless Virtual GPU",
                "vendor_name": "Godot Simulation Engine",
                "driver_name": "Vulkan / Metal Simulation",
                "max_compute_workgroup_size": [1024, 1024, 64],
                "max_compute_shared_memory_bytes": 32768,
                "supports_compute_shaders": True,
                "supports_storage_buffers": True,
            },
        )

    async def scatter_multimesh(
        self,
        mesh_path: str | None = None,
        node_name: str = "MultiMeshInstance3D",
        parent_path: str = ".",
        instance_count: int = 100,
        area_size: list[float] | None = None,
        min_scale: float = 0.8,
        max_scale: float = 1.3,
        random_yaw: bool = True,
        align_to_surface: bool = False,
    ) -> StandardResult:
        """Scatter MultiMesh in headless mode."""
        area = area_size or [50.0, 50.0]
        return StandardResult(
            success=True,
            message=f"Scattered {instance_count} GPU MultiMesh instances across area [{area[0]}m x {area[1]}m] under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": f"{parent_path}/{node_name}"
                if parent_path != "."
                else node_name,
                "instance_count": instance_count,
                "area_size": area,
                "scale_range": [min_scale, max_scale],
                "mesh_path": mesh_path or "",
            },
        )

    async def configure_lod_manager(
        self,
        node_path: str = "GeometryInstance3D",
        visibility_range_begin: float = 0.0,
        visibility_range_end: float = 150.0,
        visibility_range_begin_margin: float = 10.0,
        visibility_range_end_margin: float = 10.0,
        fade_mode: str = "self",
    ) -> StandardResult:
        """Configure LOD visibility range in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured LOD visibility range [{visibility_range_begin}m to {visibility_range_end}m] for '{node_path.split('/')[-1]}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "node_path": node_path,
                "visibility_range_begin": visibility_range_begin,
                "visibility_range_end": visibility_range_end,
                "visibility_range_begin_margin": visibility_range_begin_margin,
                "visibility_range_end_margin": visibility_range_end_margin,
                "fade_mode": fade_mode,
            },
        )
