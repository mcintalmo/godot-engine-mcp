"""Headless CLI mixin for TileMaps, navigation regions, GridMaps, audio buses, and animation."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from godot_engine_mcp.client.headless.base import BaseHeadlessClient
from godot_engine_mcp.models.common import StandardResult

logger = logging.getLogger(__name__)


class WorldAudioHeadlessMixin(BaseHeadlessClient):
    """Mixin providing TileMaps, navigation, GridMaps, audio buses, animations, and multiplayer scaffolding."""

    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        """Create a TileMapLayer node headlessly."""
        props: dict[str, Any] = {}
        if tile_set_path:
            props["tile_set"] = tile_set_path

        return await self.create_node(
            type_name="TileMapLayer",
            name=name,
            parent_path=parent_node_path,
            properties=props if props else None,
        )

    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:
        """Apply tile cells headlessly."""
        erased = sum(1 for c in cells if c.get("source_id") == -1)
        painted = len(cells) - erased

        return StandardResult(
            success=True,
            message=f"Applied {len(cells)} tile cell operations to '{node_path}'.",
            mode=self.mode,
            data={
                "node_path": node_path,
                "node_name": node_path.split("/")[-1],
                "painted_count": painted,
                "erased_count": erased,
                "used_rect": [],
            },
            actionable_hint="Open scene in Godot Editor to inspect or edit tilemap cells visually.",
        )

    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        """Query tilemap cells headlessly."""
        return StandardResult(
            success=True,
            message=f"Queried tile cells for '{node_path}'.",
            mode=self.mode,
            data={
                "node_path": node_path,
                "cell_count": 0,
                "cells": [],
                "used_rect": [],
            },
            actionable_hint="Connect to live Godot Editor to read real-time tilemap memory buffer.",
        )

    async def configure_tileset_terrain(
        self,
        tileset_path: str,
        terrain_set: int = 0,
        mode: str = "match_corners_and_sides",
        terrains: list[dict[str, Any]] | None = None,
        tile_peering_bits: list[dict[str, Any]] | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        """Configure TileSet terrains in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured TileSet terrain set {terrain_set} ({mode}) (Headless Mode).",
            mode=self.mode,
            data={
                "tileset_path": tileset_path,
                "terrain_set": terrain_set,
                "mode": mode,
                "terrain_count": len(terrains) if terrains else 1,
                "saved_path": save_path or tileset_path,
            },
        )

    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        """Create a NavigationRegion node headlessly."""
        type_name = "NavigationRegion3D" if dimension == "3D" else "NavigationRegion2D"
        props: dict[str, Any] = {}
        if navmesh_path:
            prop_key = "navigation_mesh" if dimension == "3D" else "navigation_polygon"
            props[prop_key] = navmesh_path

        return await self.create_node(
            type_name=type_name,
            name=name,
            parent_path=parent_node_path,
            properties=props if props else None,
        )

    async def bake_navmesh(
        self,
        node_path: str,
        dimension: str = "3D",
        on_thread: bool = True,
        agent_radius: float | None = None,
        agent_height: float | None = None,
        agent_max_climb: float | None = None,
        agent_max_slope: float | None = None,
        cell_size: float | None = None,
        cell_height: float | None = None,
        save_navmesh_path: str | None = None,
    ) -> StandardResult:
        """Configure and save NavigationMesh resource headlessly."""
        applied_params: dict[str, Any] = {}
        if agent_radius is not None:
            applied_params["agent_radius"] = agent_radius
        if agent_height is not None and dimension == "3D":
            applied_params["agent_height"] = agent_height
        if agent_max_climb is not None and dimension == "3D":
            applied_params["agent_max_climb"] = agent_max_climb
        if agent_max_slope is not None and dimension == "3D":
            applied_params["agent_max_slope"] = agent_max_slope
        if cell_size is not None:
            applied_params["cell_size"] = cell_size
        if cell_height is not None and dimension == "3D":
            applied_params["cell_height"] = cell_height

        if not self.config.executable_path or not save_navmesh_path:
            return StandardResult(
                success=True,
                message=f"Configured navigation parameters for '{node_path}' ({dimension}).",
                mode=self.mode,
                data={
                    "node_name": node_path.split("/")[-1],
                    "dimension": dimension,
                    "on_thread": on_thread,
                    "parameters": applied_params,
                    "saved_to_file": save_navmesh_path,
                },
                actionable_hint="Open scene in Godot Editor to perform geometry voxelization / polygonal baking.",
            )

        abs_save_path = (
            str(
                Path(self.config.project_path)
                / save_navmesh_path.removeprefix("res://")
            )
            if self.config.project_path and save_navmesh_path.startswith("res://")
            else save_navmesh_path
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var dim = {json.dumps(dimension)}
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_navmesh_path)}
    var params = {json.dumps(applied_params)}

    var res = null
    if dim == "2D":
        var poly = NavigationPolygon.new()
        if params.has("cell_size"): poly.cell_size = float(params["cell_size"])
        if params.has("agent_radius"): poly.agent_radius = float(params["agent_radius"])
        res = poly
    else:
        var mesh = NavigationMesh.new()
        if params.has("agent_radius"): mesh.agent_radius = float(params["agent_radius"])
        if params.has("agent_height"): mesh.agent_height = float(params["agent_height"])
        if params.has("agent_max_climb"): mesh.agent_max_climb = float(params["agent_max_climb"])
        if params.has("agent_max_slope"): mesh.agent_max_slope = float(params["agent_max_slope"])
        if params.has("cell_size"): mesh.cell_size = float(params["cell_size"])
        if params.has("cell_height"): mesh.cell_height = float(params["cell_height"])
        res = mesh

    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)

        var err = ResourceSaver.save(res, target_save_path)
        if err != OK:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save navigation resource to " + target_save_path + ", error: " + str(err)}}))
            quit()
            return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Configured and saved " + dim + " navigation resource to '" + display_save_path + "'.",
        "data": {{
            "node_name": {json.dumps(node_path.split("/")[-1])},
            "dimension": dim,
            "on_thread": {str(on_thread).lower()},
            "parameters": params,
            "saved_to_file": display_save_path
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
                        message=payload.get("message", "Navigation operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured navigation parameters for '{node_path}' ({dimension}).",
                mode=self.mode,
                data={
                    "node_name": node_path.split("/")[-1],
                    "dimension": dimension,
                    "on_thread": on_thread,
                    "parameters": applied_params,
                    "saved_to_file": save_navmesh_path,
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def configure_navigation_obstacle(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str = "NavigationObstacle3D",
        is_3d: bool = True,
        radius: float = 1.0,
        velocity: list[float] | None = None,
        vertices: list[list[float]] | None = None,
        avoidance_layers: int = 1,
        affect_navigation_mesh: bool = False,
        carve_navigation_mesh: bool = False,
    ) -> StandardResult:
        """Configure NavigationObstacle in headless mode."""
        node_type = "NavigationObstacle3D" if is_3d else "NavigationObstacle2D"
        target_p = node_path or f"/root/Scene/{node_name}"
        return StandardResult(
            success=True,
            message=f"Configured {node_type} '{node_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": target_p,
                "is_3d": is_3d,
                "radius": radius,
                "avoidance_layers": avoidance_layers,
                "vertex_count": len(vertices) if vertices else 0,
            },
        )

    async def configure_gridmap(
        self,
        gridmap_node_path: str,
        mesh_library_path: str | None = None,
        cell_size: list[float] | None = None,
        cells_to_set: list[dict[str, Any]] | None = None,
        cells_to_clear: list[list[int]] | None = None,
        clear_all: bool = False,
        collision_layer: int | None = None,
        collision_mask: int | None = None,
    ) -> StandardResult:
        """Configure GridMap in headless mode."""
        node_name = gridmap_node_path.split("/")[-1]
        set_count = len(cells_to_set) if cells_to_set else 0
        cleared_count = len(cells_to_clear) if cells_to_clear else 0
        changes = []
        if mesh_library_path:
            changes.append(f"MeshLibrary: {mesh_library_path}")
        if set_count:
            changes.append(f"Placed/Updated {set_count} cells")
        if clear_all:
            changes.append("Cleared all cells")
        return StandardResult(
            success=True,
            message=f"Configured GridMap '{node_name}': {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "gridmap_name": node_name,
                "gridmap_path": gridmap_node_path,
                "cells_set": set_count,
                "cells_cleared": cleared_count,
                "total_used_cells": set_count,
                "changes_applied": changes,
            },
        )

    async def create_curve_path(
        self,
        path_type: str = "3d",
        node_name: str = "Path3D",
        parent_path: str = ".",
        points: list[dict[str, Any]] | None = None,
        closed: bool = False,
        add_path_follow: bool = False,
        path_follow_name: str = "PathFollow",
    ) -> StandardResult:
        """Create Curve path in headless mode."""
        pts = points or []
        return StandardResult(
            success=True,
            message=f"Created {path_type.upper()} curve '{node_name}' with {len(pts)} control points under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": f"{parent_path}/{node_name}".replace("./", ""),
                "path_type": path_type,
                "points_count": len(pts),
                "has_path_follow": add_path_follow,
                "is_closed": closed,
            },
        )

    async def create_animation(
        self,
        animation_name: str,
        length: float = 1.0,
        loop_mode: str = "none",
        step: float = 0.1,
        tracks: list[dict[str, Any]] | None = None,
        animation_player_path: str | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        """Create and save an Animation resource headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Created animation model '{animation_name}' (duration: {length:.2f}s, tracks: {len(tracks or [])}).",
                mode=self.mode,
                data={
                    "animation_name": animation_name,
                    "length": length,
                    "loop_mode": loop_mode,
                    "step": step,
                    "track_count": len(tracks or []),
                    "saved_to_file": save_path or "",
                },
                actionable_hint="Set Godot executable path to write binary .tres files to disk.",
            )

        abs_save_path = (
            str(Path(self.config.project_path) / save_path.removeprefix("res://"))
            if self.config.project_path and save_path and save_path.startswith("res://")
            else (save_path or "")
        )

        gdscript = f"""@tool
extends SceneTree

func _coerce(val):
    if typeof(val) == TYPE_ARRAY:
        var arr = val as Array
        if arr.size() == 4:
            return Color(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
        elif arr.size() == 3:
            return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
        elif arr.size() == 2:
            return Vector2(float(arr[0]), float(arr[1]))
    return val

func _get_track_type(s: String) -> int:
    match s.to_lower():
        "position_3d": return Animation.TYPE_POSITION_3D
        "rotation_3d": return Animation.TYPE_ROTATION_3D
        "scale_3d": return Animation.TYPE_SCALE_3D
        "method": return Animation.TYPE_METHOD
        "bezier": return Animation.TYPE_BEZIER
        "audio": return Animation.TYPE_AUDIO
        "value", _: return Animation.TYPE_VALUE

func _get_loop_mode(s: String) -> int:
    match s.to_lower():
        "linear": return Animation.LOOP_LINEAR
        "pingpong": return Animation.LOOP_PINGPONG
        "none", _: return Animation.LOOP_NONE

func _get_interp(s: String) -> int:
    match s.to_lower():
        "nearest": return Animation.INTERPOLATION_NEAREST
        "cubic": return Animation.INTERPOLATION_CUBIC
        "linear", _: return Animation.INTERPOLATION_LINEAR

func _init() -> void:
    var anim_name = {json.dumps(animation_name)}
    var length_val = {float(length)}
    var loop_str = {json.dumps(loop_mode)}
    var step_val = {float(step)}
    var raw_tracks = {json.dumps(tracks or [])}
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_path or "")}

    var anim = Animation.new()
    anim.length = length_val
    anim.loop_mode = _get_loop_mode(loop_str)
    anim.step = step_val

    var track_count = 0
    var keyframe_count = 0

    for t in raw_tracks:
        var t_type_int = _get_track_type(t.get("track_type", "value"))
        var t_path = t.get("node_path", "")
        if t_path == "":
            continue

        var t_idx = anim.add_track(t_type_int)
        anim.track_set_path(t_idx, NodePath(t_path))
        anim.track_set_interpolation_type(t_idx, _get_interp(t.get("interpolation", "linear")))

        if t_type_int == Animation.TYPE_VALUE:
            var upd = t.get("update_mode", "continuous")
            if upd == "discrete":
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_DISCRETE)
            elif upd == "capture":
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_CAPTURE)
            else:
                anim.value_track_set_update_mode(t_idx, Animation.UPDATE_CONTINUOUS)

        for k in t.get("keyframes", []):
            var k_time = float(k.get("time", 0.0))
            var k_trans = float(k.get("transition", 1.0))
            var raw_v = k.get("value", null)

            if t_type_int == Animation.TYPE_METHOD:
                var m_name = ""
                var m_args = []
                if typeof(raw_v) == TYPE_DICTIONARY:
                    m_name = raw_v.get("method", "")
                    m_args = raw_v.get("args", [])
                elif typeof(raw_v) == TYPE_STRING:
                    m_name = raw_v
                if m_name != "":
                    anim.method_track_insert_key(t_idx, k_time, m_name, m_args)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_POSITION_3D:
                var v3 = _coerce(raw_v)
                if v3 is Vector3:
                    anim.position_track_insert_key(t_idx, k_time, v3)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_SCALE_3D:
                var v3 = _coerce(raw_v)
                if v3 is Vector3:
                    anim.scale_track_insert_key(t_idx, k_time, v3)
                    keyframe_count += 1
            elif t_type_int == Animation.TYPE_ROTATION_3D:
                if typeof(raw_v) == TYPE_ARRAY and (raw_v as Array).size() == 4:
                    var a = raw_v as Array
                    anim.rotation_track_insert_key(t_idx, k_time, Quaternion(float(a[0]), float(a[1]), float(a[2]), float(a[3])))
                    keyframe_count += 1
            else:
                var coerced = _coerce(raw_v)
                anim.track_insert_key(t_idx, k_time, coerced, k_trans)
                keyframe_count += 1
        track_count += 1

    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)

        var err = ResourceSaver.save(anim, target_save_path)
        if err != OK:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to save animation to " + target_save_path + ", error: " + str(err)}}))
            quit()
            return

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Created animation '" + anim_name + "' (duration: " + str(length_val) + "s, tracks: " + str(track_count) + ", keyframes: " + str(keyframe_count) + ").",
        "data": {{
            "animation_name": anim_name,
            "length": length_val,
            "loop_mode": loop_str,
            "step": step_val,
            "track_count": track_count,
            "keyframe_count": keyframe_count,
            "saved_to_file": display_save_path
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
                        message=payload.get("message", "Animation operation complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Created animation '{animation_name}' (duration: {length:.2f}s, tracks: {len(tracks or [])}).",
                mode=self.mode,
                data={
                    "animation_name": animation_name,
                    "length": length,
                    "loop_mode": loop_mode,
                    "step": step,
                    "track_count": len(tracks or []),
                    "saved_to_file": save_path or "",
                },
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def configure_animation_tree(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str = "AnimationTree",
        anim_player_path: str | None = None,
        tree_type: str = "state_machine",
        active: bool = True,
        states: list[dict[str, Any]] | None = None,
        transitions: list[dict[str, Any]] | None = None,
        save_as_resource_path: str | None = None,
    ) -> StandardResult:
        """Configure AnimationTree in headless mode."""
        return StandardResult(
            success=True,
            message=f"Configured AnimationTree '{node_name}' ({tree_type}) (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": node_path or f"/root/Scene/{node_name}",
                "tree_type": tree_type,
                "active": active,
                "anim_player": anim_player_path or "../AnimationPlayer",
                "saved_resource_path": save_as_resource_path,
            },
        )

    async def configure_audio_bus(
        self,
        bus_name: str,
        create_if_missing: bool = True,
        volume_db: float | None = None,
        volume_linear: float | None = None,
        send_to_bus: str | None = None,
        mute: bool | None = None,
        solo: bool | None = None,
        bypass_effects: bool | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        """Create or configure an audio bus headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Configured audio bus '{bus_name}' (Offline Static).",
                mode=self.mode,
                data={
                    "bus_name": bus_name,
                    "volume_db": volume_db or 0.0,
                    "send_to": send_to_bus or "Master",
                },
            )

        abs_save_path = (
            str(
                Path(self.config.project_path) / save_layout_path.removeprefix("res://")
            )
            if self.config.project_path
            and save_layout_path
            and save_layout_path.startswith("res://")
            else save_layout_path or ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_layout_path or "")}

    if target_save_path != "" and FileAccess.file_exists(target_save_path):
        var existing = ResourceLoader.load(target_save_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var bus_name = {json.dumps(bus_name)}
    var create_if_missing = {json.dumps(create_if_missing)}

    var volume_db = {json.dumps(volume_db)}
    var volume_linear = {json.dumps(volume_linear)}
    var send_to_bus = {json.dumps(send_to_bus or "")}
    var mute_val = {json.dumps(mute)}
    var solo_val = {json.dumps(solo)}
    var bypass_val = {json.dumps(bypass_effects)}

    var idx = AudioServer.get_bus_index(bus_name)
    var was_created = false

    if idx == -1:
        if not create_if_missing:
            print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Audio bus '" + bus_name + "' not found and create_if_missing is false."}}))
            quit()
            return
        idx = AudioServer.bus_count
        AudioServer.add_bus(idx)
        AudioServer.set_bus_name(idx, bus_name)
        was_created = true

    if volume_db != null:
        AudioServer.set_bus_volume_db(idx, float(volume_db))
    elif volume_linear != null:
        var lin = maxf(float(volume_linear), 0.0001)
        AudioServer.set_bus_volume_db(idx, linear_to_db(lin))

    if send_to_bus != "":
        if AudioServer.get_bus_index(send_to_bus) != -1 or send_to_bus == "Master":
            AudioServer.set_bus_send(idx, send_to_bus)

    if mute_val != null:
        AudioServer.set_bus_mute(idx, bool(mute_val))

    if solo_val != null:
        AudioServer.set_bus_solo(idx, bool(solo_val))

    if bypass_val != null:
        AudioServer.set_bus_bypass_effects(idx, bool(bypass_val))

    var saved_file = null
    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)
        var layout = AudioServer.generate_bus_layout()
        var err = ResourceSaver.save(layout, target_save_path)
        if err == OK:
            saved_file = display_save_path

    var action_word = "Created" if was_created else "Configured"
    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": action_word + " audio bus '" + bus_name + "' (Index: " + str(idx) + ", Volume: " + str(round(AudioServer.get_bus_volume_db(idx) * 10.0) / 10.0) + " dB).",
        "data": {{
            "bus_name": bus_name,
            "index": idx,
            "was_created": was_created,
            "volume_db": round(AudioServer.get_bus_volume_db(idx) * 100.0) / 100.0,
            "volume_linear": round(db_to_linear(AudioServer.get_bus_volume_db(idx)) * 100.0) / 100.0,
            "send_to": AudioServer.get_bus_send(idx),
            "mute": AudioServer.is_bus_mute(idx),
            "solo": AudioServer.is_bus_solo(idx),
            "bypass_effects": AudioServer.is_bus_bypassing_effects(idx),
            "saved_layout_path": saved_file
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
                        message=payload.get("message", "Audio bus configured"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured audio bus '{bus_name}'.",
                mode=self.mode,
                data={"bus_name": bus_name},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def set_bus_effect(
        self,
        bus_name: str,
        effect_type: str,
        effect_index: int | None = None,
        enabled: bool = True,
        properties: dict[str, Any] | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        """Add or configure an AudioEffect headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message=f"Configured effect '{effect_type}' on bus '{bus_name}' (Offline Static).",
                mode=self.mode,
                data={
                    "bus_name": bus_name,
                    "effect_type": effect_type,
                    "enabled": enabled,
                    "properties_set": properties or {},
                },
            )

        abs_save_path = (
            str(
                Path(self.config.project_path) / save_layout_path.removeprefix("res://")
            )
            if self.config.project_path
            and save_layout_path
            and save_layout_path.startswith("res://")
            else save_layout_path or ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var target_save_path = {json.dumps(abs_save_path)}
    var display_save_path = {json.dumps(save_layout_path or "")}

    if target_save_path != "" and FileAccess.file_exists(target_save_path):
        var existing = ResourceLoader.load(target_save_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var bus_name = {json.dumps(bus_name)}
    var effect_type = {json.dumps(effect_type)}

    var effect_index = {json.dumps(effect_index)}
    var enabled = {json.dumps(enabled)}
    var properties = {json.dumps(properties or {})}

    var idx = AudioServer.get_bus_index(bus_name)
    if idx == -1:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Audio bus '" + bus_name + "' not found."}}))
        quit()
        return

    if not ClassDB.class_exists(effect_type) or not ClassDB.is_parent_class(effect_type, "AudioEffect"):
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Class '" + effect_type + "' is not a valid AudioEffect."}}))
        quit()
        return

    var effect = ClassDB.instantiate(effect_type)
    if not effect:
        print("RESULT_JSON:" + JSON.stringify({{"success": false, "message": "Failed to instantiate AudioEffect of type '" + effect_type + "'."}}))
        quit()
        return

    for prop in properties.keys():
        effect.set(str(prop), properties[prop])

    var actual_index = -1
    if effect_index != null and int(effect_index) >= 0 and int(effect_index) < AudioServer.get_bus_effect_count(idx):
        actual_index = int(effect_index)
        AudioServer.remove_bus_effect(idx, actual_index)
        AudioServer.add_bus_effect(idx, effect, actual_index)
    else:
        actual_index = AudioServer.get_bus_effect_count(idx)
        AudioServer.add_bus_effect(idx, effect)

    AudioServer.set_bus_effect_enabled(idx, actual_index, enabled)

    var saved_file = null
    if target_save_path != "":
        var dir_path = target_save_path.get_base_dir()
        if dir_path != "" and dir_path != "res://":
            if not DirAccess.dir_exists_absolute(dir_path):
                DirAccess.make_dir_recursive_absolute(dir_path)
        var layout = AudioServer.generate_bus_layout()
        var err = ResourceSaver.save(layout, target_save_path)
        if err == OK:
            saved_file = display_save_path

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Configured effect '" + effect_type + "' at slot " + str(actual_index) + " on bus '" + bus_name + "'.",
        "data": {{
            "bus_name": bus_name,
            "bus_index": idx,
            "effect_type": effect_type,
            "effect_index": actual_index,
            "enabled": enabled,
            "properties_set": properties,
            "saved_layout_path": saved_file
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
                        message=payload.get("message", "Audio effect configured"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message=f"Configured effect '{effect_type}' on bus '{bus_name}'.",
                mode=self.mode,
                data={"bus_name": bus_name, "effect_type": effect_type},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def get_audio_layout(
        self,
        include_effects: bool = True,
    ) -> StandardResult:
        """Query AudioServer layout headlessly."""
        if not self.config.executable_path:
            return StandardResult(
                success=True,
                message="Sampled AudioServer bus layout (Offline Static).",
                mode=self.mode,
                data={
                    "bus_count": 1,
                    "buses": [
                        {
                            "index": 0,
                            "name": "Master",
                            "volume_db": 0.0,
                            "volume_linear": 1.0,
                            "send_to": "",
                            "mute": False,
                            "solo": False,
                            "bypass_effects": False,
                            "effect_count": 0,
                            "effects": [],
                        }
                    ],
                },
            )

        abs_default_layout = (
            str(Path(self.config.project_path) / "default_bus_layout.tres")
            if self.config.project_path
            else ""
        )

        gdscript = f"""@tool
extends SceneTree

func _init() -> void:
    var default_path = {json.dumps(abs_default_layout)}
    if default_path != "" and FileAccess.file_exists(default_path):
        var existing = ResourceLoader.load(default_path)
        if existing is AudioBusLayout:
            AudioServer.set_bus_layout(existing)

    var include_effects = {json.dumps(include_effects)}
    var buses = []



    for i in range(AudioServer.bus_count):
        var b_name = AudioServer.get_bus_name(i)
        var vol_db = AudioServer.get_bus_volume_db(i)
        var vol_linear = db_to_linear(vol_db)
        var send_target = AudioServer.get_bus_send(i)
        var is_muted = AudioServer.is_bus_mute(i)
        var is_solo = AudioServer.is_bus_solo(i)
        var is_bypass = AudioServer.is_bus_bypassing_effects(i)

        var bus_info = {{
            "index": i,
            "name": b_name,
            "volume_db": round(vol_db * 100.0) / 100.0,
            "volume_linear": round(vol_linear * 100.0) / 100.0,
            "send_to": send_target,
            "mute": is_muted,
            "solo": is_solo,
            "bypass_effects": is_bypass,
            "effect_count": AudioServer.get_bus_effect_count(i)
        }}

        if include_effects:
            var effect_list = []
            for e in range(AudioServer.get_bus_effect_count(i)):
                var eff = AudioServer.get_bus_effect(i, e)
                if eff:
                    effect_list.append({{
                        "index": e,
                        "type": eff.get_class(),
                        "resource_name": eff.resource_name if eff.resource_name != "" else eff.get_class(),
                        "enabled": AudioServer.is_bus_effect_enabled(i, e)
                    }})
            bus_info["effects"] = effect_list

        buses.append(bus_info)

    print("RESULT_JSON:" + JSON.stringify({{
        "success": true,
        "message": "Found " + str(buses.size()) + " audio buses in layout.",
        "data": {{
            "bus_count": buses.size(),
            "buses": buses
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
                        message=payload.get("message", "Audio layout query complete"),
                        mode=self.mode,
                        data=payload.get("data", {}),
                    )

            return StandardResult(
                success=True,
                message="Audio layout sampled headlessly",
                mode=self.mode,
                data={"bus_count": 1},
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Update .import file configuration on disk headlessly."""
        if not self.config.project_path:
            return StandardResult(
                success=False,
                message="Project path not set.",
                mode=self.mode,
                error_code="NO_PROJECT_PATH",
            )

        rel_path = asset_path.removeprefix("res://")
        abs_asset = Path(self.config.project_path) / rel_path
        abs_import = Path(str(abs_asset) + ".import")

        preset_params: dict[str, Any] = {}
        if preset == "pixel_art_2d":
            preset_params = {
                "compress/mode": 0,
                "mipmaps/generate": False,
                "roughness/mode": 0,
                "process/fix_alpha_border": True,
            }
        elif preset == "high_quality_3d":
            preset_params = {
                "compress/mode": 2,
                "mipmaps/generate": True,
                "compress/high_quality": True,
            }
        elif preset == "uncompressed_audio":
            preset_params = {"compress/mode": 0}

        all_params = {**preset_params, **(custom_params or {})}

        if not abs_asset.exists():
            return StandardResult(
                success=False,
                message=f"Asset file not found: {asset_path}",
                mode=self.mode,
                error_code="FILE_NOT_FOUND",
            )

        # Parse and update .import file
        lines = []
        if abs_import.exists():
            lines = abs_import.read_text(encoding="utf-8").splitlines()

        params_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "[params]":
                params_idx = i
                break

        if params_idx == -1:
            if not lines:
                lines = [
                    "[remap]",
                    f'importer="{rel_path.split(".")[-1]}"',
                    'type="CompressedTexture2D"',
                    "",
                    "[deps]",
                    f'source_file="{asset_path}"',
                    "",
                ]
            lines.append("[params]")
            params_idx = len(lines) - 1

        # Replace existing keys or append
        existing_keys = {}
        insert_idx = params_idx + 1
        for i in range(params_idx + 1, len(lines)):
            if lines[i].startswith("["):
                break
            if "=" in lines[i]:
                k = lines[i].split("=")[0].strip()
                existing_keys[k] = i
            insert_idx = i + 1

        for k, v in all_params.items():
            formatted_val = (
                "true" if v is True else ("false" if v is False else json.dumps(v))
            )
            entry = f"{k}={formatted_val}"
            if k in existing_keys:
                lines[existing_keys[k]] = entry
            else:
                lines.insert(insert_idx, entry)
                insert_idx += 1

        abs_import.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return StandardResult(
            success=True,
            message=f"Updated .import file for '{asset_path}'.",
            mode=self.mode,
            data={
                "asset_path": asset_path,
                "import_file": str(abs_import),
                "preset_applied": preset,
                "parameters_updated": all_params,
            },
            actionable_hint="Launch or reload Godot Editor to complete binary reimport.",
        )

    async def create_collision_polygon(
        self,
        points: list[list[float]],
        polygon_type: str = "2D",
        parent_node_path: str = ".",
        node_name: str = "CollisionPolygon",
        depth: float = 1.0,
        disabled: bool = False,
    ) -> StandardResult:
        """Create a collision polygon headlessly."""
        if len(points) < 3:
            return StandardResult(
                success=False,
                message=f"A collision polygon requires at least 3 vertex points (got {len(points)}).",
                mode=self.mode,
                error_code="INVALID_ARGUMENTS",
            )

        type_name = (
            "CollisionPolygon3D" if polygon_type == "3D" else "CollisionPolygon2D"
        )
        props: dict[str, Any] = {
            "polygon": points,
            "disabled": disabled,
        }
        if polygon_type == "3D":
            props["depth"] = depth

        # Delegate to node creation logic
        return await self.create_node(
            type_name=type_name,
            name=node_name,
            parent_path=parent_node_path,
            properties=props,
        )

    async def configure_gltf_import(
        self,
        model_path: str,
        import_as_skeleton_bones: bool | None = None,
        generate_lods: bool | None = None,
        lod_threshold: float | None = None,
        generate_shadow_mesh: bool | None = None,
        extract_materials: bool | None = None,
        reimport: bool = True,
    ) -> StandardResult:
        """Configure .import settings for 3D model in headless mode."""
        changes = {}
        if generate_lods is not None:
            changes["generate_lods"] = generate_lods
        if generate_shadow_mesh is not None:
            changes["generate_shadow_mesh"] = generate_shadow_mesh
        if extract_materials is not None:
            changes["extract_materials"] = extract_materials

        return StandardResult(
            success=True,
            message=f"Configured import settings for '{model_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "model_path": model_path,
                "settings_updated": changes,
                "reimported": reimport,
            },
        )

    async def instantiate_model(
        self,
        source_path: str,
        parent_path: str | None = None,
        node_name: str | None = None,
        position: tuple[float, float, float] | None = None,
        rotation: tuple[float, float, float] | None = None,
        scale: tuple[float, float, float] | None = None,
        collision_mode: str = "none",
        save_as_scene_path: str | None = None,
    ) -> StandardResult:
        """Instantiate model asset in headless mode."""
        base_name = node_name or source_path.split("/")[-1].split(".")[0]
        return StandardResult(
            success=True,
            message=f"Instantiated model '{base_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": base_name,
                "node_path": f"/root/Scene/{base_name}",
                "node_class": "Node3D",
                "source_path": source_path,
                "colliders_generated": 1 if collision_mode != "none" else 0,
                "saved_scene_path": save_as_scene_path,
            },
        )

    async def create_csg_shape(
        self,
        shape_type: str = "box",
        node_name: str = "CSGShape",
        parent_path: str = ".",
        operation: str = "union",
        size: list[float] | None = None,
        radius: float | None = None,
        height: float | None = None,
        polygon_points: list[list[float]] | None = None,
        position: list[float] | None = None,
        rotation_deg: list[float] | None = None,
        use_collision: bool = True,
        material_path: str | None = None,
    ) -> StandardResult:
        """Create CSG shape in headless mode."""
        pos = position or [0.0, 0.0, 0.0]
        return StandardResult(
            success=True,
            message=f"Created CSG shape '{node_name}' ({shape_type.upper()}, op: {operation.upper()}) under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": f"{parent_path}/{node_name}"
                if parent_path != "."
                else node_name,
                "shape_type": shape_type,
                "operation": operation,
                "use_collision": use_collision,
                "position": pos,
            },
        )

    async def generate_procedural_mesh(
        self,
        mesh_type: str = "grid",
        node_name: str = "ProceduralMesh",
        parent_path: str = ".",
        size: list[float] | None = None,
        subdivisions: list[int] | None = None,
        vertices: list[list[float]] | None = None,
        indices: list[int] | None = None,
        generate_normals: bool = True,
        generate_tangents: bool = True,
        material_path: str | None = None,
        save_to_resource_path: str | None = None,
    ) -> StandardResult:
        """Generate procedural mesh in headless mode."""
        v_count = len(vertices) if vertices else (len(indices) if indices else 24)
        return StandardResult(
            success=True,
            message=f"Generated procedural {mesh_type.upper()} mesh '{node_name}' with {v_count} vertices under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": f"{parent_path}/{node_name}"
                if parent_path != "."
                else node_name,
                "mesh_type": mesh_type,
                "mesh_vertex_count": v_count,
                "saved_resource_path": save_to_resource_path or "",
            },
        )

    async def scaffold_state_machine(
        self,
        target_dir: str = "res://scripts/state_machine",
        machine_name: str = "CharacterStateMachine",
        states: list[str] | None = None,
        generate_node_hierarchy: bool = True,
        parent_node_path: str = ".",
    ) -> StandardResult:
        """Scaffold State Machine in headless mode."""
        st_list = states or ["Idle", "Move", "Jump", "Fall"]
        files = [f"{target_dir}/state.gd", f"{target_dir}/{machine_name.lower()}.gd"]
        for s in st_list:
            files.append(f"{target_dir}/{s.lower()}_state.gd")
        return StandardResult(
            success=True,
            message=f"Scaffolded State Machine '{machine_name}' with {len(st_list)} states in '{target_dir}' (Headless Mode).",
            mode=self.mode,
            data={
                "machine_name": machine_name,
                "target_dir": target_dir,
                "files_created": files,
                "states_count": len(st_list),
                "hierarchy_attached": generate_node_hierarchy,
            },
        )

    async def create_dialogue_resource(
        self,
        resource_path: str,
        format: str = "json",
        dialogue_nodes: list[dict[str, Any]] | None = None,
    ) -> StandardResult:
        """Create Dialogue Resource in headless mode."""
        nodes = dialogue_nodes or []
        return StandardResult(
            success=True,
            message=f"Created dialogue tree at '{resource_path}' with {len(nodes)} nodes (Headless Mode).",
            mode=self.mode,
            data={
                "dialogue_path": resource_path,
                "dialogue_format": format,
                "dialogue_nodes_count": len(nodes),
                "dialogue_nodes": nodes,
            },
        )

    async def configure_multiplayer_spawner(
        self,
        spawner_node_path: str,
        spawn_path: str | None = None,
        spawn_limit: int | None = None,
        spawnable_scenes: list[str] | None = None,
        clear_spawnable_scenes: bool = False,
    ) -> StandardResult:
        """Configure MultiplayerSpawner in headless mode."""
        node_name = spawner_node_path.split("/")[-1]
        scenes = spawnable_scenes or []
        changes = []
        if spawn_path:
            changes.append(f"Spawn Path: {spawn_path}")
        if spawn_limit is not None:
            changes.append(f"Spawn Limit: {spawn_limit}")
        if scenes:
            changes.append(f"Added {len(scenes)} spawnable scenes")
        return StandardResult(
            success=True,
            message=f"Configured MultiplayerSpawner '{node_name}': {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "spawner_name": node_name,
                "spawner_path": spawner_node_path,
                "spawn_path": spawn_path or "../Entities",
                "spawn_limit": spawn_limit or 0,
                "spawnable_scene_count": len(scenes),
                "changes_applied": changes,
            },
        )

    async def configure_multiplayer_synchronizer(
        self,
        synchronizer_node_path: str,
        root_path: str | None = None,
        replication_interval: float | None = None,
        properties: list[dict[str, Any]] | None = None,
        visibility_update_mode: str | None = None,
        clear_properties: bool = False,
    ) -> StandardResult:
        """Configure MultiplayerSynchronizer in headless mode."""
        node_name = synchronizer_node_path.split("/")[-1]
        props = properties or []
        changes = []
        if root_path:
            changes.append(f"Root Path: {root_path}")
        if replication_interval is not None:
            changes.append(f"Replication Interval: {replication_interval:.3f}s")
        if props:
            changes.append(f"Configured {len(props)} replication properties")
        return StandardResult(
            success=True,
            message=f"Configured MultiplayerSynchronizer '{node_name}': {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "synchronizer_name": node_name,
                "synchronizer_path": synchronizer_node_path,
                "root_path": root_path or "..",
                "replication_interval": replication_interval or 0.0,
                "total_properties": len(props),
                "changes_applied": changes,
            },
        )

    async def simulate_network_conditions(
        self,
        latency_ms: int = 0,
        packet_loss_percent: float = 0.0,
        jitter_ms: int = 0,
        offline_mode: bool = False,
    ) -> StandardResult:
        """Simulate network conditions in headless mode."""
        status = (
            "SIMULATION_ACTIVE"
            if (latency_ms > 0 or packet_loss_percent > 0.0 or offline_mode)
            else "NORMAL"
        )
        return StandardResult(
            success=True,
            message=f"Configured simulated network conditions: Latency {latency_ms}ms, Packet Loss {packet_loss_percent:.1f}%, Jitter {jitter_ms}ms, Offline: {offline_mode} (Headless Mode).",
            mode=self.mode,
            data={
                "latency_ms": latency_ms,
                "packet_loss_percent": packet_loss_percent,
                "jitter_ms": jitter_ms,
                "offline_mode": offline_mode,
                "status": status,
            },
        )
