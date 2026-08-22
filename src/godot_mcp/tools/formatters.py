"""Response formatters converting StandardResult into Markdown or JSON."""

import json

from godot_mcp.models.common import ResponseFormat, StandardResult


def format_result(
    result: StandardResult, response_format: ResponseFormat = ResponseFormat.MARKDOWN
) -> str:
    """Format StandardResult according to the requested response format."""
    if response_format == ResponseFormat.JSON:
        return json.dumps(result.model_dump(), indent=2)

    lines: list[str] = []

    # Header / status
    status_tag = "SUCCESS" if result.success else "FAILED"
    lines.append(f"### Godot Operation [{status_tag}] - Mode: {result.mode.value}")
    lines.append(f"**Message**: {result.message}")

    if result.error_code:
        lines.append(f"**Error Code**: `{result.error_code}`")

    if result.actionable_hint:
        lines.append(f"\n> **Suggestion**: {result.actionable_hint}")

    if result.warnings:
        lines.append("\n**Warnings**:")
        for w in result.warnings:
            lines.append(f"- {w}")

    # Structured Data Render
    if result.data:
        lines.append("\n**Details**:")
        # Special pretty printing for common structures
        if "files" in result.data and isinstance(result.data["files"], list):
            lines.append(f"Total Files: {len(result.data['files'])}")
            for item in result.data["files"][:25]:
                lines.append(
                    f"- `{item.get('path')}` ({item.get('type_name', 'Resource')}, {item.get('size_bytes', 0)} bytes)"
                )
            if len(result.data["files"]) > 25:
                lines.append(f"... and {len(result.data['files']) - 25} more items.")
        elif "settings" in result.data and isinstance(result.data["settings"], dict):
            for k, v in list(result.data["settings"].items())[:30]:
                lines.append(f"- `{k}` = `{v}`")
            if len(result.data["settings"]) > 30:
                lines.append(
                    f"... and {len(result.data['settings']) - 30} more settings."
                )
        elif "nodes" in result.data and isinstance(result.data["nodes"], list):
            for node in result.data["nodes"]:
                warn_text = ""
                node_warns = node.get("warnings", [])
                if node_warns:
                    warn_text = f" [WARNING: {len(node_warns)} issue(s)]"
                lines.append(
                    f"- `{node.get('name')}` (`{node.get('type_name')}`) at `{node.get('node_path')}`{warn_text}"
                )
                if node_warns:
                    for w in node_warns:
                        lines.append(f"  - Warning: {w}")

        elif (
            "material_path" in result.data
            and "material_type" in result.data
            and "shader_path" not in result.data
        ):
            lines.append(f"**Material Resource**: `{result.data.get('material_path')}`")
            lines.append(f"**Material Type**: `{result.data.get('material_type')}`")

            if result.data.get("assigned_to_node"):
                lines.append(
                    f"**Assigned to Node**: `{result.data.get('assigned_to_node')}`"
                )
            if result.data.get("properties_applied"):
                lines.append("\n**Configured Properties**:")
                for k, v in result.data["properties_applied"].items():
                    lines.append(f"- `{k}` = `{v}`")

        elif "import_file" in result.data or "preset_applied" in result.data:
            lines.append(f"**Asset Path**: `{result.data.get('asset_path')}`")
            if result.data.get("preset_applied"):
                lines.append(
                    f"**Preset Applied**: `{result.data.get('preset_applied')}`"
                )
            if result.data.get("import_file"):
                lines.append(
                    f"**Import Configuration**: `{result.data.get('import_file')}`"
                )
            if result.data.get("parameters_updated"):
                lines.append("\n**Updated Import Parameters**:")
                for k, v in result.data["parameters_updated"].items():
                    lines.append(f"- `{k}` = `{v}`")

        elif "vertex_count" in result.data:
            lines.append(
                f"**Collision Node**: `{result.data.get('node_name')}` (`{result.data.get('polygon_type')}`)"
            )
            lines.append(f"**Vertices**: `{result.data.get('vertex_count')} points`")
            if result.data.get("depth") is not None:
                lines.append(f"**Extrusion Depth**: `{result.data.get('depth')}`")
            lines.append(f"**Parent Node**: `{result.data.get('parent_node_path')}`")
            lines.append(f"**Disabled**: `{result.data.get('disabled')}`")

        elif "animation_name" in result.data:
            lines.append(f"**Animation**: `{result.data.get('animation_name')}`")
            lines.append(
                f"**Duration**: `{result.data.get('length')}s` (Step: `{result.data.get('step')}s`, Loop: `{result.data.get('loop_mode')}`)"
            )
            lines.append(
                f"**Tracks**: `{result.data.get('track_count')}` tracks, `{result.data.get('keyframe_count')}` keyframes"
            )
            if result.data.get("attached_to_animation_player"):
                lines.append(
                    f"**Attached to AnimationPlayer**: `{result.data.get('attached_to_animation_player')}`"
                )
            if result.data.get("saved_to_file"):
                lines.append(
                    f"**Saved Resource**: `{result.data.get('saved_to_file')}`"
                )

        elif "painted_count" in result.data:
            lines.append(f"**Target Layer**: `{result.data.get('node_path')}`")
            lines.append(f"**Painted**: `{result.data.get('painted_count')}` cells")
            lines.append(f"**Erased**: `{result.data.get('erased_count')}` cells")
            if result.data.get("used_rect"):
                r = result.data["used_rect"]
                lines.append(
                    f"**Used Bounding Rect**: `[x={r[0]}, y={r[1]}, w={r[2]}, h={r[3]}]`"
                )

        elif "cell_count" in result.data:
            lines.append(f"**Target Layer**: `{result.data.get('node_path')}`")
            lines.append(f"**Total Used Cells**: `{result.data.get('cell_count')}`")
            if result.data.get("used_rect"):
                r = result.data["used_rect"]
                lines.append(
                    f"**Used Bounding Rect**: `[x={r[0]}, y={r[1]}, w={r[2]}, h={r[3]}]`"
                )
            cells_list = result.data.get("cells", [])
            if cells_list:
                lines.append("\n**Sample Cells**:")
                for c in cells_list[:10]:
                    lines.append(
                        f"- Coords `{c['coords']}`: Source `{c['source_id']}`, Atlas `{c['atlas_coords']}`, Alt `{c['alternative_tile']}`"
                    )
                if len(cells_list) > 10:
                    lines.append(f"- *... and {len(cells_list) - 10} more cells*")

        elif "tile_set_attached" in result.data:
            lines.append(
                f"**Layer Name**: `{result.data.get('node_name')}` (`{result.data.get('type_name')}`)"
            )
            lines.append(f"**Parent Node**: `{result.data.get('parent_node_path')}`")
            if result.data.get("tile_set_attached"):
                lines.append(f"**TileSet**: `{result.data.get('tile_set_attached')}`")

        elif "navmesh_attached" in result.data:
            lines.append(
                f"**Navigation Region**: `{result.data.get('node_name')}` (`{result.data.get('type_name')}`)"
            )
            lines.append(f"**Dimension**: `{result.data.get('dimension')}`")
            lines.append(f"**Parent Node**: `{result.data.get('parent_node_path')}`")
            if result.data.get("navmesh_attached"):
                lines.append(
                    f"**NavMesh Resource**: `{result.data.get('navmesh_attached')}`"
                )

        elif "dimension" in result.data and "on_thread" in result.data:
            lines.append(
                f"**Navigation Node**: `{result.data.get('node_name')}` (`{result.data.get('dimension')}`)"
            )
            lines.append(f"**Threaded Baking**: `{result.data.get('on_thread')}`")
            if result.data.get("parameters"):
                lines.append("\n**Baking Parameters**:")
                for k, v in result.data["parameters"].items():
                    lines.append(f"- `{k}` = `{v}`")
            if result.data.get("saved_to_file"):
                lines.append(
                    f"**Saved Resource**: `{result.data.get('saved_to_file')}`"
                )

        elif "symbols" in result.data:
            lines.append(f"**Target File**: `{result.data.get('file_path')}`")
            syms = result.data.get("symbols", [])
            lines.append(f"**Total Symbols**: `{len(syms)}`\n")
            lines.append("| Name | Kind | Line | Signature |")
            lines.append("|---|---|---|---|")
            for s in syms:
                name = s.get("name", "")
                kind = s.get("kind", "")
                line_no = s.get("line", "")
                sig = s.get("signature", "")
                lines.append(f"| `{name}` | {kind} | {line_no} | `{sig}` |")

        elif "definition" in result.data:
            defn = result.data.get("definition")
            lines.append(f"**Symbol**: `{result.data.get('symbol', 'unknown')}`")
            if isinstance(defn, dict):
                lines.append(
                    f"**Declared In**: `{defn.get('file')}` (Line {defn.get('line')})"
                )
                if defn.get("line_content"):
                    lines.append(f"```gdscript\n{defn.get('line_content')}\n```")
            else:
                lines.append(f"**Definition**: `{defn}`")

        elif "references" in result.data:
            refs = result.data.get("references", [])
            lines.append(f"**Symbol**: `{result.data.get('symbol', 'unknown')}`")
            lines.append(f"**Total References**: `{len(refs)}`\n")
            for r in refs:
                if isinstance(r, dict):
                    f = r.get("file", "")
                    l = r.get("line", "")
                    content = r.get("line_content", "")
                    lines.append(f"- `{f}:{l}`: `{content}`")
                else:
                    lines.append(f"- `{r}`")

        elif "hover" in result.data:
            h = result.data.get("hover")
            if isinstance(h, dict):
                lines.append(f"**Symbol**: `{h.get('symbol')}`")
                if h.get("signature"):
                    lines.append(f"\n```gdscript\n{h.get('signature')}\n```")
                if h.get("docstring"):
                    lines.append(f"\n**Documentation**:\n{h.get('docstring')}")
            else:
                lines.append(f"**Hover Info**: {h}")

        elif "modified_files" in result.data:
            lines.append(
                f"**Renamed**: `{result.data.get('old_name')}` -> `{result.data.get('new_name')}`"
            )
            mods = result.data.get("modified_files", [])
            lines.append(f"**Modified Files ({len(mods)})**:")
            for m in mods:
                lines.append(f"- `{m}`")

        elif "category" in result.data and (
            "time" in result.data
            or "render" in result.data
            or "memory" in result.data
            or "objects" in result.data
        ):
            cat = result.data.get("category", "all")
            lines.append(f"**Performance Telemetry** (Filter: `{cat}`)\n")

            if "time" in result.data:
                t = result.data["time"]
                lines.append("### Framerate & Timing")
                lines.append(f"- **FPS**: `{t.get('fps')}`")
                lines.append(
                    f"- **Process Frame Time**: `{t.get('process_time_ms')} ms`"
                )
                lines.append(
                    f"- **Physics Process Time**: `{t.get('physics_process_time_ms')} ms`"
                )
                if t.get("navigation_process_time_ms") is not None:
                    lines.append(
                        f"- **Navigation Process Time**: `{t.get('navigation_process_time_ms')} ms`"
                    )
                lines.append("")

            if "render" in result.data:
                r = result.data["render"]
                lines.append("### Rendering & GPU")
                lines.append(
                    f"- **Draw Calls in Frame**: `{r.get('draw_calls_in_frame')}`"
                )
                lines.append(f"- **Rendered Objects**: `{r.get('objects_in_frame')}`")
                lines.append(
                    f"- **Primitives / Triangles**: `{r.get('primitives_in_frame')}`"
                )
                lines.append(f"- **Total VRAM**: `{r.get('video_mem_mb')} MB`")
                lines.append(f"- **Texture VRAM**: `{r.get('texture_mem_mb')} MB`")
                lines.append(f"- **Buffer VRAM**: `{r.get('buffer_mem_mb')} MB`")
                lines.append("")

            if "memory" in result.data:
                m = result.data["memory"]
                lines.append("### Memory Allocations")
                lines.append(f"- **Static RAM**: `{m.get('static_ram_mb')} MB`")
                lines.append(
                    f"- **Peak Static RAM**: `{m.get('static_ram_peak_mb')} MB`"
                )
                lines.append(f"- **Message Buffer**: `{m.get('message_buffer_kb')} KB`")
                lines.append("")

            if "objects" in result.data:
                o = result.data["objects"]
                lines.append("### Object & Node Tracking")
                lines.append(f"- **Node Count**: `{o.get('node_count')}`")
                lines.append(f"- **Resource Count**: `{o.get('resource_count')}`")
                lines.append(f"- **Object Count**: `{o.get('object_count')}`")
                orphans = o.get("orphan_node_count", 0)
                if orphans > 0:
                    lines.append(
                        f"- **Orphan Nodes**: `{orphans}` *(Warning: Potential memory leak)*"
                    )
                else:
                    lines.append(f"- **Orphan Nodes**: `{orphans}` (Clean)")

                lines.append("")

            if result.data.get("custom"):
                lines.append("### Custom Monitors")
                for k, v in result.data["custom"].items():
                    lines.append(f"- **{k}**: `{v}`")

        elif "save_path" in result.data and (
            "styleboxes_configured" in result.data or "colors_configured" in result.data
        ):
            lines.append(f"**Theme Resource**: `{result.data.get('save_path')}`")
            if result.data.get("base_font_size"):
                lines.append(
                    f"**Base Font Size**: `{result.data.get('base_font_size')} px`"
                )
            if result.data.get("applied_to_node"):
                lines.append(
                    f"**Applied to Node**: `{result.data.get('applied_to_node')}`"
                )
            if result.data.get("colors_configured"):
                lines.append("\n**Colors Configured**:")
                for nt, cols in result.data["colors_configured"].items():
                    col_items = ", ".join(f"`{k}`: {v}" for k, v in cols.items())
                    lines.append(f"- **{nt}**: {col_items}")
            if result.data.get("constants_configured"):
                lines.append("\n**Constants Configured**:")
                for nt, consts in result.data["constants_configured"].items():
                    const_items = ", ".join(f"`{k}`: {v}" for k, v in consts.items())
                    lines.append(f"- **{nt}**: {const_items}")
            if result.data.get("styleboxes_configured"):
                lines.append(
                    f"\n**StyleBoxes Configured**: {', '.join(f'`{s}`' for s in result.data['styleboxes_configured'])}"
                )

        elif "override_type" in result.data and "item_name" in result.data:
            lines.append(f"**Target Node**: `{result.data.get('node_name')}`")
            lines.append(f"**Override Type**: `{result.data.get('override_type')}`")
            lines.append(f"**Item Name**: `{result.data.get('item_name')}`")
            val = result.data.get("value")
            if isinstance(val, dict):
                lines.append("\n**StyleBox Properties**:")
                for k, v in val.items():
                    lines.append(f"- `{k}` = `{v}`")
            else:
                lines.append(f"**Value**: `{val}`")

        elif "buses" in result.data:
            lines.append(
                f"**Audio Buses ({result.data.get('bus_count', len(result.data['buses']))})**:\n"
            )
            lines.append(
                "| Index | Bus Name | Volume (dB) | Linear | Send To | Mute | Solo | Bypass | Effects |"
            )
            lines.append("|---|---|---|---|---|---|---|---|---|")
            for b in result.data["buses"]:
                eff_summary = f"{len(b.get('effects', []))} effects"
                if b.get("effects"):
                    eff_names = ", ".join(
                        e.get("type", "").removeprefix("AudioEffect")
                        for e in b["effects"]
                    )
                    eff_summary = f"`{eff_names}`"
                lines.append(
                    f"| {b.get('index')} | **{b.get('name')}** | `{b.get('volume_db')} dB` | `{b.get('volume_linear')}` | `{b.get('send_to') or 'None'}` | `{b.get('mute')}` | `{b.get('solo')}` | `{b.get('bypass_effects')}` | {eff_summary} |"
                )

        elif "effect_type" in result.data and "bus_name" in result.data:
            lines.append(
                f"**Audio Bus**: `{result.data.get('bus_name')}` (Slot `{result.data.get('effect_index')}`)"
            )
            lines.append(
                f"**Effect**: `{result.data.get('effect_type')}` (Enabled: `{result.data.get('enabled')}`)"
            )
            if result.data.get("properties_set"):
                lines.append("\n**Properties**:")
                for k, v in result.data["properties_set"].items():
                    lines.append(f"- `{k}` = `{v}`")
            if result.data.get("saved_layout_path"):
                lines.append(
                    f"\n**Saved Layout**: `{result.data.get('saved_layout_path')}`"
                )

        elif "bus_name" in result.data and "volume_db" in result.data:
            lines.append(
                f"**Audio Bus**: `{result.data.get('bus_name')}` (Index `{result.data.get('index')}`)"
            )
            lines.append(
                f"- **Volume**: `{result.data.get('volume_db')} dB` (`{result.data.get('volume_linear')}` linear)"
            )
            lines.append(f"- **Send Target**: `{result.data.get('send_to')}`")
            lines.append(
                f"- **Mute**: `{result.data.get('mute')}` | **Solo**: `{result.data.get('solo')}` | **Bypass Effects**: `{result.data.get('bypass_effects')}`"
            )
            if result.data.get("saved_layout_path"):
                lines.append(
                    f"- **Saved Layout**: `{result.data.get('saved_layout_path')}`"
                )

        elif "is_playing" in result.data or "was_playing" in result.data:
            if "is_playing" in result.data:
                playing_str = "PLAYING" if result.data["is_playing"] else "STOPPED"
                lines.append(f"**Play State**: `{playing_str}`")
            if "time_scale" in result.data:
                lines.append(
                    f"**Simulation Speed (Time Scale)**: `{result.data.get('time_scale')}x`"
                )
            if "is_paused" in result.data:
                lines.append(f"**Paused**: `{result.data.get('is_paused')}`")
            if result.data.get("stepped_frames"):
                lines.append(
                    f"**Stepped Frames**: `{result.data.get('stepped_frames')}`"
                )
            if result.data.get("active_editor_scene"):
                lines.append(
                    f"**Active Editor Scene**: `{result.data.get('active_editor_scene')}`"
                )
            if result.data.get("mode"):
                lines.append(f"**Launch Mode**: `{result.data.get('mode')}`")

        elif "has_hit" in result.data:
            hit = result.data.get("has_hit", False)
            lines.append(f"**Hit Status**: `{'HIT' if hit else 'NO INTERSECTION'}`")
            lines.append(f"- **From**: `{result.data.get('from_pos')}`")
            lines.append(f"- **To**: `{result.data.get('to_pos')}`")
            if hit:
                lines.append(
                    f"- **Collider**: `{result.data.get('collider_name')}` (`{result.data.get('collider_path')}`)"
                )
                lines.append(f"- **Hit Position**: `{result.data.get('hit_position')}`")
                lines.append(f"- **Hit Normal**: `{result.data.get('hit_normal')}`")
                lines.append(f"- **Distance**: `{result.data.get('distance')}m`")
                lines.append(f"- **Shape Index**: `{result.data.get('shape_index')}`")

        elif "overlaps" in result.data and "shape_type" in result.data:
            stype = result.data.get("shape_type", "unknown")
            count = result.data.get("overlap_count", 0)
            lines.append(
                f"**Shape Cast ({stype.upper()})**: `{count} overlapping colliders`\n"
            )
            if count > 0:
                lines.append("| Index | Collider Name | Path | Class | Shape Index |")
                lines.append("|---|---|---|---|---|")
                for i, o in enumerate(result.data.get("overlaps", [])):
                    lines.append(
                        f"| {i} | **{o.get('collider_name')}** | `{o.get('collider_path')}` | `{o.get('collider_class')}` | `{o.get('shape_index')}` |"
                    )
            if result.data.get("motion_cast"):
                mc = result.data["motion_cast"]
                lines.append(
                    f"\n**Motion Sweep**: Safe Fraction: `{mc.get('safe_fraction')}`, Unsafe Fraction: `{mc.get('unsafe_fraction')}`"
                )

        elif "linear_velocity" in result.data and "node_name" in result.data:
            lines.append(
                f"**Physics Body**: `{result.data.get('node_name')}` (`{result.data.get('class')}`)"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(
                f"- **Linear Velocity**: `{result.data.get('linear_velocity')} m/s`"
            )
            lines.append(
                f"- **Angular Velocity**: `{result.data.get('angular_velocity')} rad/s`"
            )
            lines.append(
                f"- **Mass**: `{result.data.get('mass')} kg` | **Sleeping**: `{result.data.get('is_sleeping')}`"
            )
            lines.append(
                f"- **Layers / Masks**: Layer `{result.data.get('collision_layer')}` | Mask `{result.data.get('collision_mask')}`"
            )
            if result.data.get("contact_count", 0) > 0:
                lines.append(
                    f"\n**Active Contacts ({result.data.get('contact_count')})**:"
                )
                for c in result.data.get("contacts", []):
                    lines.append(
                        f"- Contact {c.get('index')}: Pos `{c.get('position')}` | Norm `{c.get('normal')}` | Impulse `{c.get('impulse')}`"
                    )

        elif "actions" in result.data:
            lines.append(
                f"**Input Actions ({result.data.get('action_count', len(result.data['actions']))})**:\n"
            )
            lines.append("| Action Name | Deadzone | Events |")
            lines.append("|---|---|---|")
            for a in result.data.get("actions", []):
                ev_strs = []
                for e in a.get("events", []):
                    if e.get("type") == "key":
                        ev_strs.append(
                            f"Key `{e.get('keycode') or e.get('physical_keycode')}`"
                        )
                    elif e.get("type") == "mouse_button":
                        ev_strs.append(f"MouseBtn `{e.get('button_index')}`")
                    elif e.get("type") == "joypad_button":
                        ev_strs.append(f"JoyBtn `{e.get('button_index')}`")
                    elif e.get("type") == "joypad_motion":
                        ev_strs.append(
                            f"Axis `{e.get('axis')}` ({e.get('axis_value')})"
                        )
                ev_summary = ", ".join(ev_strs) if ev_strs else "*None*"
                lines.append(
                    f"| **{a.get('name')}** | `{a.get('deadzone')}` | {ev_summary} |"
                )

        elif "action_name" in result.data and "events_added" in result.data:
            lines.append(
                f"**Action**: `{result.data.get('action_name')}` (Deadzone: `{result.data.get('deadzone')}`)"
            )
            lines.append(
                f"- **Saved to Project Settings**: `{result.data.get('saved_to_project_settings')}`"
            )
            if result.data.get("events_added"):
                lines.append("\n**Events Configured**:")
                for ev in result.data["events_added"]:
                    lines.append(f"- `{ev}`")

        elif "properties_set" in result.data and (
            "saved_path" in result.data or "target_node" in result.data
        ):
            lines.append("**Environment Configuration**:")
            if result.data.get("target_node"):
                lines.append(f"- **Target Node**: `{result.data.get('target_node')}`")
            if result.data.get("saved_path"):
                lines.append(f"- **Saved Path**: `{result.data.get('saved_path')}`")
            lines.append("\n**Properties Updated**:")
            for k, v in result.data.get("properties_set", {}).items():
                lines.append(f"- `{k}` = `{v}`")

        elif "selected_nodes" in result.data:
            nodes_raw = result.data.get("selected_nodes", [])
            count = result.data.get(
                "selection_count",
                result.data.get("selected_count", len(nodes_raw)),
            )
            lines.append(f"**Editor Selection - Selected Nodes ({count})**:\n")

            if nodes_raw and isinstance(nodes_raw[0], dict):
                lines.append("| Node Name | Path | Class | Position | Visible |")
                lines.append("|---|---|---|---|---|")
                for n in nodes_raw:
                    p_str = n.get("position", "-")
                    v_str = str(n.get("visible", "-"))
                    lines.append(
                        f"| **{n.get('name')}** | `{n.get('path')}` | `{n.get('class')}` | {p_str} | {v_str} |"
                    )
            else:
                for n in nodes_raw:
                    lines.append(f"- `{n}`")
            if result.data.get("inspected_node"):
                lines.append(
                    f"\n- **Inspected in Editor**: `{result.data.get('inspected_node')}`"
                )

        elif "source_path" in result.data and "colliders_generated" in result.data:
            lines.append(
                f"**Model Instance**: `{result.data.get('node_name')}` (`{result.data.get('node_class')}`)"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Source**: `{result.data.get('source_path')}`")
            lines.append(
                f"- **Colliders Created**: `{result.data.get('colliders_generated')}`"
            )
            if result.data.get("saved_scene_path"):
                lines.append(
                    f"- **Saved Scene**: `{result.data.get('saved_scene_path')}`"
                )

        elif "signals" in result.data and "signal_count" in result.data:
            lines.append(
                f"**Signals on `{result.data.get('node_name')}` ({result.data.get('node_class')})** - Total: {result.data.get('signal_count')}:\n"
            )
            lines.append("| Signal Name | Arguments |")
            lines.append("|---|---|")
            for s in result.data.get("signals", []):
                args_strs = [
                    f"{arg.get('name')}: {arg.get('type')}"
                    for arg in s.get("arguments", [])
                ]
                arg_summary = ", ".join(args_strs) if args_strs else "*None*"
                lines.append(f"| **{s.get('name')}** | `{arg_summary}` |")

        elif "node_name" in result.data and "node_class" in result.data:
            lines.append(
                f"**Focused Node**: `{result.data.get('node_name')}` (`{result.data.get('node_class')}`)"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")

        elif "model_path" in result.data and "settings_updated" in result.data:
            lines.append(f"**GLTF Import Settings**: `{result.data.get('model_path')}`")
            lines.append(f"- **Reimported**: `{result.data.get('reimported')}`")
            if result.data.get("settings_updated"):
                lines.append("\n**Parameters Updated**:")
                for k, v in result.data["settings_updated"].items():
                    lines.append(f"- `{k}` = `{v}`")

        elif "particle_type" in result.data and "emission_shape" in result.data:
            lines.append(
                f"**Particle System**: `{result.data.get('node_name')}` (Type: `{result.data.get('particle_type')}`)"
            )
            if result.data.get("node_path"):
                lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Emission Shape**: `{result.data.get('emission_shape')}`")
            lines.append(
                f"- **Created New Node**: `{result.data.get('created_new_node')}`"
            )
            if result.data.get("saved_material_path"):
                lines.append(
                    f"- **Saved Material**: `{result.data.get('saved_material_path')}`"
                )

        elif "presets" in result.data:
            lines.append(
                f"**Export Presets ({result.data.get('preset_count', len(result.data['presets']))})**:\n"
            )
            lines.append("| Name | Platform | Export Path | Runnable |")
            lines.append("|---|---|---|---|")
            for p in result.data.get("presets", []):
                lines.append(
                    f"| **{p.get('name')}** | `{p.get('platform')}` | `{p.get('export_path') or '*None*'}` | `{p.get('runnable')}` |"
                )

        elif "preset_name" in result.data and "output_path" in result.data:
            lines.append(f"**Export Build**: `{result.data.get('preset_name')}`")
            lines.append(f"- **Destination**: `{result.data.get('output_path')}`")
            lines.append(f"- **Debug**: `{result.data.get('debug')}`")
            if "returncode" in result.data:
                lines.append(f"- **Return Code**: `{result.data.get('returncode')}`")

        elif "autoloads" in result.data:
            lines.append(
                f"**Autoload Singletons ({result.data.get('autoload_count', len(result.data['autoloads']))})**:\n"
            )
            lines.append("| Name | Resource Path | Singleton | Exists |")
            lines.append("|---|---|---|---|")
            for a in result.data.get("autoloads", []):
                lines.append(
                    f"| **{a.get('name')}** | `{a.get('path')}` | `{a.get('is_singleton')}` | `{a.get('exists', True)}` |"
                )

        elif (
            "outgoing_connections" in result.data
            or "incoming_connections" in result.data
        ):
            lines.append(
                f"**Signal Connection Graph for `{result.data.get('node_path')}`**:\n"
            )
            out_list = result.data.get("outgoing_connections", [])
            in_list = result.data.get("incoming_connections", [])
            if out_list:
                lines.append(f"**Outgoing ({len(out_list)})**:")
                for c in out_list:
                    lines.append(
                        f"- Signal `{c.get('signal_name')}` -> `{c.get('target_node')}.{c.get('method_name')}()` (Flags: `{c.get('flags')}`)"
                    )
            if in_list:
                lines.append(f"\n**Incoming ({len(in_list)})**:")
                for c in in_list:
                    lines.append(
                        f"- From `{c.get('source_node')}` (Signal `{c.get('signal_name')}`) -> `.{c.get('method_name')}()`"
                    )

        elif (
            "source_node" in result.data
            and "signal_name" in result.data
            and "target_node" in result.data
        ):
            status_word = (
                "Connected" if result.data.get("connected", True) else "Disconnected"
            )
            lines.append(f"**Signal {status_word}**:")
            lines.append(f"- **Source Node**: `{result.data.get('source_node')}`")
            lines.append(f"- **Signal**: `{result.data.get('signal_name')}`")
            lines.append(f"- **Target Node**: `{result.data.get('target_node')}`")
            lines.append(
                f"- **Method / Callable**: `.{result.data.get('method_name')}()`"
            )
            if "flags" in result.data:
                lines.append(f"- **Flags**: `{result.data.get('flags')}`")

        elif "expression" in result.data and "result_type" in result.data:
            lines.append(
                f"**Expression Evaluation**: `{result.data.get('expression')}`"
            )
            lines.append(f"- **Result**: `{result.data.get('result')}`")
            lines.append(f"- **Type**: `{result.data.get('result_type')}`")
            if result.data.get("context_node"):
                lines.append(f"- **Context Node**: `{result.data.get('context_node')}`")

        elif "shader_path" in result.data and "shader_type" in result.data:
            lines.append(f"**Custom Shader**: `{result.data.get('shader_path')}`")
            lines.append(f"- **Type**: `{result.data.get('shader_type')}`")
            if result.data.get("material_path"):
                lines.append(
                    f"- **Generated Material**: `{result.data.get('material_path')}`"
                )

        elif "parameter_name" in result.data and "target" in result.data:
            lines.append("**Shader Parameter Updated**:")
            lines.append(f"- **Target**: `{result.data.get('target')}`")
            lines.append(f"- **Parameter**: `{result.data.get('parameter_name')}`")
            lines.append(f"- **Value**: `{result.data.get('value')}`")
            if result.data.get("material_path"):
                lines.append(
                    f"- **Material File**: `{result.data.get('material_path')}`"
                )

        elif "tree_type" in result.data and "anim_player" in result.data:
            lines.append(f"**AnimationTree**: `{result.data.get('node_name')}`")
            if result.data.get("node_path"):
                lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Tree Type**: `{result.data.get('tree_type')}`")
            lines.append(f"- **AnimationPlayer**: `{result.data.get('anim_player')}`")
            lines.append(f"- **Active**: `{result.data.get('active')}`")
            if result.data.get("saved_resource_path"):
                lines.append(
                    f"- **Saved Resource**: `{result.data.get('saved_resource_path')}`"
                )

        elif "translations" in result.data and "loaded_locales" in result.data:
            lines.append(
                f"**Translation Tables ({result.data.get('translation_count', len(result.data['translations']))})**:\n"
            )
            lines.append(
                f"- **Fallback Locale**: `{result.data.get('fallback_locale')}`"
            )
            lines.append(
                f"- **Loaded Locales**: `{', '.join(result.data.get('loaded_locales', []))}`\n"
            )
            lines.append("| Translation File | Exists |")
            lines.append("|---|---|")
            for t in result.data.get("translations", []):
                lines.append(f"| `{t.get('path')}` | `{t.get('exists', True)}` |")

        elif "translation_path" in result.data and "total_translations" in result.data:
            lines.append(
                f"**Translation Registered**: `{result.data.get('translation_path')}`"
            )
            lines.append(
                f"- **Total Configured Translations**: `{result.data.get('total_translations')}`"
            )
            if result.data.get("test_locale_set"):
                lines.append(
                    f"- **Active Test Locale**: `{result.data.get('test_locale_set')}`"
                )

        elif "uid" in result.data and "path" in result.data:
            lines.append(f"**Resource UID**: `{result.data.get('uid')}`")
            lines.append(f"- **Path**: `{result.data.get('path')}`")
            if "numeric_id" in result.data:
                lines.append(f"- **Numeric ID**: `{result.data.get('numeric_id')}`")

        elif "dependencies" in result.data and "dependency_count" in result.data:
            lines.append(
                f"**Dependencies for `{result.data.get('source_path')}` ({result.data.get('dependency_count')})**:\n"
            )
            lines.append("| Dependency | Resolved Path | Type | Exists |")
            lines.append("|---|---|---|---|")
            for d in result.data.get("dependencies", []):
                t_str = "UID" if d.get("is_uid") else "Path"
                lines.append(
                    f"| `{d.get('raw')}` | `{d.get('resolved_path')}` | `{t_str}` | `{d.get('exists', True)}` |"
                )

        elif "plugins" in result.data and "plugin_count" in result.data:
            lines.append(f"**Editor Plugins ({result.data.get('plugin_count')})**:\n")
            lines.append("| Plugin ID | Name | Version | Author | Enabled |")
            lines.append("|---|---|---|---|---|")
            for p in result.data.get("plugins", []):
                lines.append(
                    f"| **{p.get('id')}** | {p.get('name')} | `{p.get('version')}` | {p.get('author')} | `{p.get('enabled')}` |"
                )

        elif "plugin_id" in result.data and "config_path" in result.data:
            state_str = "Enabled" if result.data.get("enabled", True) else "Disabled"
            lines.append(f"**Plugin {state_str}**: `{result.data.get('plugin_id')}`")
            lines.append(f"- **Config**: `{result.data.get('config_path')}`")
            lines.append(f"- **Status**: `{result.data.get('enabled')}`")

        elif "avoidance_layers" in result.data and "vertex_count" in result.data:
            lines.append(
                f"**NavigationObstacle**: `{result.data.get('node_name')}` (3D: `{result.data.get('is_3d')}`)"
            )
            if result.data.get("node_path"):
                lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Radius**: `{result.data.get('radius')}`")
            lines.append(
                f"- **Avoidance Layers**: `{result.data.get('avoidance_layers')}`"
            )
            lines.append(f"- **Polygon Vertices**: `{result.data.get('vertex_count')}`")

        elif "terrain_set" in result.data and "terrain_count" in result.data:
            lines.append(
                f"**TileSet Terrain Set {result.data.get('terrain_set')}**: `{result.data.get('tileset_path')}`"
            )
            lines.append(f"- **Mode**: `{result.data.get('mode')}`")
            lines.append(
                f"- **Configured Terrains**: `{result.data.get('terrain_count')}`"
            )
            if result.data.get("saved_path"):
                lines.append(f"- **Saved Resource**: `{result.data.get('saved_path')}`")

        elif "added_nodes" in result.data and "removed_nodes" in result.data:
            lines.append(
                f"**Scene Diff**: `{result.data.get('base')}` vs `{result.data.get('target')}`\n"
            )
            lines.append(f"- **Added**: {result.data.get('added_count')}")
            lines.append(f"- **Removed**: {result.data.get('removed_count')}")
            lines.append(f"- **Modified**: {result.data.get('modified_count')}\n")

            add_list = result.data.get("added_nodes", [])
            rem_list = result.data.get("removed_nodes", [])
            mod_list = result.data.get("modified_nodes", [])

            if add_list:
                lines.append("**Added Nodes**:")
                for n in add_list:
                    lines.append(f"+ `{n.get('path')}` ({n.get('class')})")
            if rem_list:
                lines.append("\n**Removed Nodes**:")
                for n in rem_list:
                    lines.append(f"- `{n.get('path')}` ({n.get('class')})")
            if mod_list:
                lines.append("\n**Modified Nodes**:")
                for n in mod_list:
                    lines.append(f"* `{n.get('path')}` ({n.get('class')}):")
                    for c in n.get("changes", []):
                        lines.append(
                            f"    - `{c.get('property')}`: `{c.get('base_value')}` -> `{c.get('target_value')}`"
                        )

        elif "has_undo" in result.data and "has_redo" in result.data:
            lines.append(
                f"**Action History**: `{result.data.get('action_name', 'Action')}`"
            )
            lines.append(f"- **Can Undo**: `{result.data.get('has_undo')}`")
            lines.append(f"- **Can Redo**: `{result.data.get('has_redo')}`")

        elif "total_assets" in result.data and "orphan_count" in result.data:
            lines.append(
                f"**Asset Audit Summary** (Total: `{result.data.get('total_assets')}` files)\n"
            )
            lines.append(f"- **Orphan Assets**: {result.data.get('orphan_count')}")
            lines.append(
                f"- **Broken Dependencies**: {result.data.get('broken_count')}\n"
            )

            orphans = result.data.get("orphans", [])
            broken = result.data.get("broken_dependencies", [])

            if orphans:
                lines.append("**Orphan Files (Unreferenced)**:")
                for o in orphans[:20]:
                    lines.append(f"- `{o}`")
                if len(orphans) > 20:
                    lines.append(f"- *... and {len(orphans) - 20} more orphan files*")

            if broken:
                lines.append("\n**Broken Dependency References**:")
                for b in broken[:15]:
                    lines.append(
                        f"- `{b.get('source')}` -> Missing `{b.get('dependency')}` ({b.get('reason')})"
                    )
                if len(broken) > 15:
                    lines.append(
                        f"- *... and {len(broken) - 15} more broken dependencies*"
                    )

        elif "target_count" in result.data and "processed" in result.data:
            dry = result.data.get("dry_run", True)
            q_f = result.data.get("quarantine_folder")
            action_str = (
                "Simulated Orphan Cleanup (Dry Run)"
                if dry
                else ("Orphan Files Quarantined" if q_f else "Orphan Files Deleted")
            )
            lines.append(
                f"**{action_str}** (Count: `{result.data.get('target_count')}`)\n"
            )
            if q_f:
                lines.append(f"- **Quarantine Location**: `{q_f}`\n")
            lines.append("| Target File | Status | Destination |")
            lines.append("|---|---|---|")
            for p in result.data.get("processed", []):
                lines.append(
                    f"| `{p.get('path')}` | `{p.get('status')}` | `{p.get('destination', '-')}` |"
                )

        elif "estimated_vram_kb" in result.data and "format" in result.data:
            lines.append(f"**Texture Diagnostics**: `{result.data.get('path')}`\n")
            lines.append(
                f"- **Resolution**: `{result.data.get('width')}x{result.data.get('height')}`"
            )
            lines.append(f"- **Pixel Format**: `{result.data.get('format')}`")
            lines.append(f"- **Mipmaps**: `{result.data.get('has_mipmaps')}`")
            lines.append(
                f"- **Estimated VRAM**: `~{result.data.get('estimated_vram_kb'):.2f} KB` ({result.data.get('estimated_vram_bytes')} bytes)"
            )

        elif "total_tests" in result.data and "assert_count" in result.data:
            passed = result.data.get("passed", 0)
            failed = result.data.get("failed", 0)
            pending = result.data.get("pending", 0)
            total = result.data.get("total_tests", 0)
            status_tag = (
                "ALL PASSED"
                if failed == 0 and total > 0
                else ("FAILURES DETECTED" if failed > 0 else "NO TESTS")
            )
            lines.append(f"**GUT Test Run [{status_tag}]**:\n")
            lines.append(f"- **Total Tests**: `{total}`")
            lines.append(f"- **Passed**: `{passed}`")
            lines.append(f"- **Failed**: `{failed}`")
            lines.append(f"- **Pending**: `{pending}`")
            lines.append(f"- **Total Assertions**: `{result.data.get('assert_count')}`")
            if result.data.get("test_file"):
                lines.append(f"- **Target File**: `{result.data.get('test_file')}`")
            else:
                lines.append(f"- **Test Directory**: `{result.data.get('test_dir')}`")
            out_lines = result.data.get("output_lines", [])
            if out_lines:
                lines.append("\n**Runner Log Output**:")
                lines.append("```")
                for l in out_lines[:25]:
                    lines.append(str(l))
                if len(out_lines) > 25:
                    lines.append(f"... and {len(out_lines) - 25} more log lines")
                lines.append("```")

        elif "target_script" in result.data and "methods_scaffolded" in result.data:
            lines.append(
                f"**GUT Test Scaffolded**: `{result.data.get('test_file_path')}`\n"
            )
            lines.append(f"- **Target Script**: `{result.data.get('target_script')}`")
            lines.append(
                f"- **Scaffolded Test Methods**: `{result.data.get('methods_scaffolded')}`"
            )
            lines.append(
                f"- **Code Size**: `{result.data.get('code_length')} characters`"
            )

        elif "editor_scale" in result.data and "distraction_free_mode" in result.data:
            lines.append("**Godot Editor Workspace Layout**:\n")
            lines.append(f"- **UI Scale**: `{result.data.get('editor_scale')}x`")
            lines.append(
                f"- **Distraction-Free Mode**: `{result.data.get('distraction_free_mode')}`"
            )
            if result.data.get("edited_scene_root"):
                lines.append(
                    f"- **Active Edited Scene**: `{result.data.get('edited_scene_root')}`"
                )
            scenes = result.data.get("open_scenes", [])
            lines.append(f"- **Open Scene Tabs ({len(scenes)})**:")
            for s in scenes:
                lines.append(f"  - `{s}`")

        elif "changes_applied" in result.data and (
            "main_screen" in result.data
            or "distraction_free_mode" in result.data
            or "active_scene_path" in result.data
        ):
            lines.append("**Updated Editor Workspace Layout**:\n")
            for c in result.data.get("changes_applied", []):
                lines.append(f"- `{c}`")
            if not result.data.get("changes_applied"):
                lines.append("- *No workspace layout modifications requested.*")

        elif "old_parent" in result.data and "new_parent" in result.data:
            lines.append(f"**Reparented Node**: `{result.data.get('node_name')}`\n")
            lines.append(f"- **Previous Parent**: `{result.data.get('old_parent')}`")
            lines.append(f"- **New Parent**: `{result.data.get('new_parent')}`")
            lines.append(f"- **New Path**: `{result.data.get('new_path')}`")
            lines.append(
                f"- **Global Transform Preserved**: `{result.data.get('keep_global_transform')}`"
            )
            lines.append(f"- **Child Index**: `{result.data.get('child_index')}`")

        elif "duplicated_name" in result.data and "source_path" in result.data:
            lines.append(
                f"**Duplicated Node**: `{result.data.get('duplicated_name')}` (`{result.data.get('class')}`)\n"
            )
            lines.append(f"- **Source Node**: `{result.data.get('source_path')}`")
            lines.append(f"- **New Path**: `{result.data.get('duplicated_path')}`")
            lines.append(f"- **Parent Node**: `{result.data.get('parent_path')}`")

        elif "instance_name" in result.data and "scene_path" in result.data:
            lines.append(f"**Instantiated Scene**: `{result.data.get('scene_path')}`\n")
            lines.append(
                f"- **Instance Name**: `{result.data.get('instance_name')}` (`{result.data.get('class')}`)"
            )
            lines.append(f"- **Instance Path**: `{result.data.get('instance_path')}`")
            lines.append(f"- **Parent Node**: `{result.data.get('parent_path')}`")

        elif (
            "owner_path" in result.data
            and "node_path" in result.data
            and "recursive" in result.data
        ):
            lines.append("**Node Owner Updated**:\n")
            lines.append(f"- **Node**: `{result.data.get('node_path')}`")
            lines.append(f"- **New Owner**: `{result.data.get('owner_path')}`")
            lines.append(f"- **Recursive**: `{result.data.get('recursive')}`")

        elif "reloaded_scripts" in result.data:
            lines.append(
                f"**Reloaded {result.data.get('reloaded_count', 0)} Script Resources**:\n"
            )
            for sp in result.data.get("reloaded_scripts", []):
                lines.append(f"- `{sp}`")

        elif "has_script" in result.data and "methods" in result.data:
            lines.append(
                f"**Attached Script Info**: `{result.data.get('node_name')}`\n"
            )
            lines.append(f"- **Script Path**: `{result.data.get('script_path')}`")
            lines.append(f"- **Base Type**: `{result.data.get('base_type')}`")
            lines.append(
                f"- **Methods ({result.data.get('methods_count')})**: `{', '.join(result.data.get('methods', [])) or 'None'}`"
            )
            lines.append(
                f"- **Signals ({result.data.get('signals_count')})**: `{', '.join(result.data.get('signals', [])) or 'None'}`"
            )
            if result.data.get("properties"):
                lines.append("\n**Exported Properties**:")
                for p in result.data.get("properties", []):
                    lines.append(
                        f"- `{p.get('name')}`: default `{p.get('default_value')}`, current `{p.get('current_value')}`"
                    )

        elif "has_script" in result.data and "applied_properties" in result.data:
            lines.append(
                f"**Script Attached to Node**: `{result.data.get('node_name')}`\n"
            )
            lines.append(f"- **Script Path**: `{result.data.get('script_path')}`")
            if result.data.get("applied_properties"):
                lines.append("- **Initial Properties Applied**:")
                for k, v in result.data.get("applied_properties", {}).items():
                    lines.append(f"  - `{k}`: `{v}`")

        elif "camera_name" in result.data and "camera_path" in result.data:
            lines.append(
                f"**Configured Camera**: `{result.data.get('camera_name')}` (`{result.data.get('class')}`)\n"
            )
            lines.append(f"- **Path**: `{result.data.get('camera_path')}`")
            if result.data.get("changes_applied"):
                lines.append("- **Settings Applied**:")
                for c in result.data.get("changes_applied", []):
                    lines.append(f"  - `{c}`")

        elif "captured_dimensions" in result.data and "format" in result.data:
            dims = result.data.get("captured_dimensions", [0, 0])
            orig_dims = result.data.get("original_dimensions", [0, 0])
            lines.append(
                f"**Viewport Captured** ({dims[0]}x{dims[1]}, format: `{result.data.get('format')}`):\n"
            )
            lines.append(f"- **Native Resolution**: {orig_dims[0]}x{orig_dims[1]}")
            lines.append(
                f"- **Saved File**: `{result.data.get('saved_file') or 'None (In-memory)'}`"
            )
            lines.append(
                f"- **Base64 Payload Included**: `{result.data.get('has_base64')}`"
            )
            if result.data.get("has_base64") and result.data.get("base64_data"):
                b64 = result.data.get("base64_data", "")
                lines.append(f"- **Base64 Size**: `{len(b64)} chars`")

        elif "event_type" in result.data and "details" in result.data:
            lines.append(
                f"**Dispatched Input Event**: `{result.data.get('details')}`\n"
            )
            lines.append(f"- **Event Type**: `{result.data.get('event_type')}`")
            lines.append(f"- **Pressed**: `{result.data.get('pressed')}`")

        elif "total_shapes_added" in result.data:
            lines.append(
                f"**Rendered {result.data.get('total_shapes_added')} Debug Shapes**:\n"
            )
            lines.append(f"- **3D Shapes**: `{result.data.get('shapes_3d_count', 0)}`")
            lines.append(f"- **2D Shapes**: `{result.data.get('shapes_2d_count', 0)}`")
            lines.append(
                f"- **Active Overlay Shapes**: `{result.data.get('total_active_shapes', 0)}`"
            )

        elif "shapes_cleared" in result.data and "remaining_active" in result.data:
            lines.append("**Cleared Debug Overlays**:\n")
            lines.append(f"- **Shapes Removed**: `{result.data.get('shapes_cleared')}`")
            lines.append(
                f"- **Remaining Overlays**: `{result.data.get('remaining_active')}`"
            )

        elif "matches_count" in result.data and "elements" in result.data:
            lines.append(
                f"**Matched {result.data.get('matches_count')} Elements** for selector `[{result.data.get('selector_type')}='{result.data.get('query')}']`:\n"
            )
            for el in result.data.get("elements", []):
                lines.append(
                    f"- `{el.get('name')}` (`{el.get('class')}`) -> Path: `{el.get('path')}` (Text: `{el.get('text')}`, Visible: `{el.get('visible')}`)"
                )

        elif (
            "node_name" in result.data
            and "action" in result.data
            and "details" in result.data
        ):
            lines.append(
                f"**Node Interaction Completed**: `{result.data.get('action')}` on `{result.data.get('node_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Details**: `{result.data.get('details')}`")

        elif "condition_type" in result.data and "satisfied" in result.data:
            lines.append(
                f"**Wait Condition Evaluation** [{result.data.get('condition_type')}]:\n"
            )
            lines.append(f"- **Satisfied**: `{result.data.get('satisfied')}`")
            lines.append(f"- **Details**: `{result.data.get('details')}`")
            lines.append(f"- **Actual Value**: `{result.data.get('actual_value')}`")

        elif "all_passed" in result.data and "assertions" in result.data:
            status = "PASSED" if result.data.get("all_passed") else "FAILED"
            lines.append(
                f"**Node State Assertions [{status}]** for `{result.data.get('node_name')}` (`{result.data.get('node_path')}`):\n"
            )
            for a in result.data.get("assertions", []):
                sym = "[PASS]" if a.get("passed") else "[FAIL]"
                lines.append(
                    f"- {sym} `{a.get('property')}`: Expected `{a.get('expected')}`, Actual `{a.get('actual')}`"
                )

        elif "gridmap_name" in result.data and "total_used_cells" in result.data:
            lines.append(
                f"**Configured GridMap**: `{result.data.get('gridmap_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('gridmap_path')}`")
            lines.append(
                f"- **Cells Placed/Updated**: `{result.data.get('cells_set', 0)}`"
            )
            lines.append(
                f"- **Cells Cleared**: `{result.data.get('cells_cleared', 0)}`"
            )
            lines.append(
                f"- **Total Active Cells**: `{result.data.get('total_used_cells', 0)}`"
            )
            if result.data.get("changes_applied"):
                lines.append("- **Changes**:")
                for c in result.data.get("changes_applied", []):
                    lines.append(f"  - `{c}`")

        elif (
            "node_name" in result.data
            and "path_type" in result.data
            and "points_count" in result.data
        ):
            ptype = result.data.get("path_type", "3d").upper()
            lines.append(
                f"**Created {ptype} Curve Path**: `{result.data.get('node_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Control Points**: `{result.data.get('points_count')}`")
            lines.append(f"- **Closed Loop**: `{result.data.get('is_closed')}`")
            lines.append(
                f"- **Attached PathFollow Node**: `{result.data.get('has_path_follow')}`"
            )

        elif "orphan_node_count" in result.data and "leak_status" in result.data:
            status = result.data.get("leak_status", "UNKNOWN")
            lines.append(f"**Orphan Node Memory Leak Audit [{status}]**\n")
            lines.append(
                f"- **Orphan Nodes**: `{result.data.get('orphan_node_count', 0)}`"
            )
            lines.append(
                f"- **Active Tree Nodes**: `{result.data.get('active_node_count', 0)}`"
            )
            lines.append(
                f"- **Total Objects in Memory**: `{result.data.get('total_object_count', 0)}`"
            )
            lines.append(
                f"- **Total Resources**: `{result.data.get('total_resource_count', 0)}`"
            )

        elif (
            "frames_sampled" in result.data
            and "fps" in result.data
            and "total_frame_ms" in result.data
        ):
            lines.append(
                f"**Performance Profiler Trace** ({result.data.get('frames_sampled')} frames sampled)\n"
            )
            lines.append(
                f"- **Framerate**: `{result.data.get('fps', 0.0):.1f} FPS` (`{result.data.get('total_frame_ms', 0.0):.2f} ms/frame`)"
            )
            lines.append(
                f"- **Process Loop**: `{result.data.get('process_time_ms', 0.0):.2f} ms`"
            )
            lines.append(
                f"- **Physics Loop**: `{result.data.get('physics_time_ms', 0.0):.2f} ms`"
            )
            lines.append(
                f"- **Navigation Loop**: `{result.data.get('navigation_time_ms', 0.0):.2f} ms`"
            )
            lines.append(f"- **Draw Calls**: `{result.data.get('draw_calls', 0)}`")
            lines.append(
                f"- **Primitives Rendered**: `{result.data.get('primitives_count', 0)}`"
            )
            lines.append(
                f"- **Static Memory**: `{result.data.get('memory_static_mb', 0.0):.2f} MB` (Peak: `{result.data.get('memory_static_max_mb', 0.0):.2f} MB`)"
            )

        elif "texture_memory_mb" in result.data and "total_vram_mb" in result.data:
            lines.append("**GPU VRAM Memory Telemetry**\n")
            lines.append(
                f"- **Total VRAM Allocated**: `{result.data.get('total_vram_mb', 0.0):.2f} MB`"
            )
            lines.append(
                f"- **Texture Memory**: `{result.data.get('texture_memory_mb', 0.0):.2f} MB`"
            )
            lines.append(
                f"- **Buffer & Vertex Memory**: `{result.data.get('buffer_memory_mb', 0.0):.2f} MB`"
            )

        elif "spawner_name" in result.data and "spawnable_scene_count" in result.data:
            lines.append(
                f"**Configured MultiplayerSpawner**: `{result.data.get('spawner_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('spawner_path')}`")
            lines.append(f"- **Spawn Target Path**: `{result.data.get('spawn_path')}`")
            lines.append(f"- **Spawn Limit**: `{result.data.get('spawn_limit')}`")
            lines.append(
                f"- **Spawnable Scenes**: `{result.data.get('spawnable_scene_count')}`"
            )
            if result.data.get("changes_applied"):
                lines.append("- **Changes**:")
                for c in result.data.get("changes_applied", []):
                    lines.append(f"  - `{c}`")

        elif "synchronizer_name" in result.data and "total_properties" in result.data:
            lines.append(
                f"**Configured MultiplayerSynchronizer**: `{result.data.get('synchronizer_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('synchronizer_path')}`")
            lines.append(f"- **Root Path**: `{result.data.get('root_path')}`")
            lines.append(
                f"- **Replication Interval**: `{result.data.get('replication_interval', 0.0):.3f}s`"
            )
            lines.append(
                f"- **Replicated Properties**: `{result.data.get('total_properties')}`"
            )
            if result.data.get("changes_applied"):
                lines.append("- **Changes**:")
                for c in result.data.get("changes_applied", []):
                    lines.append(f"  - `{c}`")

        elif (
            "latency_ms" in result.data
            and "packet_loss_percent" in result.data
            and "status" in result.data
        ):
            status = result.data.get("status", "NORMAL")
            lines.append(f"**Simulated Network Profile [{status}]**\n")
            lines.append(f"- **Latency**: `{result.data.get('latency_ms')} ms`")
            lines.append(
                f"- **Packet Loss**: `{result.data.get('packet_loss_percent', 0.0):.1f}%`"
            )
            lines.append(f"- **Jitter**: `{result.data.get('jitter_ms')} ms`")
            lines.append(f"- **Offline Mode**: `{result.data.get('offline_mode')}`")

        elif "machine_name" in result.data and "states_count" in result.data:
            lines.append(
                f"**Scaffolded State Machine**: `{result.data.get('machine_name')}`\n"
            )
            lines.append(f"- **Target Directory**: `{result.data.get('target_dir')}`")
            lines.append(f"- **States Generated**: `{result.data.get('states_count')}`")
            lines.append(
                f"- **Node Hierarchy Attached**: `{result.data.get('hierarchy_attached')}`"
            )
            if result.data.get("files_created"):
                lines.append("- **Files Created**:")
                for f in result.data.get("files_created", []):
                    lines.append(f"  - `{f}`")

        elif "dialogue_path" in result.data and "dialogue_nodes_count" in result.data:
            lines.append("**Created Dialogue Tree Resource**\n")
            lines.append(f"- **Path**: `{result.data.get('dialogue_path')}`")
            lines.append(
                f"- **Format**: `{result.data.get('dialogue_format', 'json').upper()}`"
            )
            lines.append(
                f"- **Total Dialogue Nodes**: `{result.data.get('dialogue_nodes_count')}`"
            )

        elif "shape_type" in result.data and "operation" in result.data:
            lines.append(f"**Created CSG Shape**: `{result.data.get('node_name')}`\n")
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(f"- **Type**: `{result.data.get('shape_type', '').upper()}`")
            lines.append(
                f"- **Operation**: `{result.data.get('operation', '').upper()}`"
            )
            lines.append(f"- **Collision**: `{result.data.get('use_collision')}`")
            if result.data.get("position"):
                lines.append(f"- **Position**: `{result.data.get('position')}`")

        elif "mesh_type" in result.data and "mesh_vertex_count" in result.data:
            lines.append(
                f"**Generated Procedural Mesh**: `{result.data.get('node_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('node_path')}`")
            lines.append(
                f"- **Mesh Type**: `{result.data.get('mesh_type', '').upper()}`"
            )
            lines.append(f"- **Vertices**: `{result.data.get('mesh_vertex_count')}`")
            if result.data.get("saved_resource_path"):
                lines.append(
                    f"- **Saved Resource**: `{result.data.get('saved_resource_path')}`"
                )

        elif (
            "skeleton_name" in result.data
            and "bone_count" in result.data
            and "bones" in result.data
        ):
            lines.append(
                f"**Skeleton Hierarchy**: `{result.data.get('skeleton_name')}` ({result.data.get('skeleton_type')})\n"
            )
            lines.append(f"- **Path**: `{result.data.get('skeleton_path')}`")
            lines.append(f"- **Total Bones**: `{result.data.get('bone_count')}`")
            lines.append("- **Bones**:")
            for b in result.data.get("bones", [])[:15]:
                parent_info = (
                    f" (parent: {b['parent_name']})" if b.get("parent_name") else ""
                )
                lines.append(f"  - [{b.get('index')}] `{b.get('name')}`{parent_info}")
            if len(result.data.get("bones", [])) > 15:
                lines.append(
                    f"  - *... and {len(result.data.get('bones', [])) - 15} more bones*"
                )

        elif "attachment_name" in result.data and "bone_name" in result.data:
            lines.append(
                f"**Configured BoneAttachment3D**: `{result.data.get('attachment_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('attachment_path')}`")
            lines.append(f"- **Skeleton**: `{result.data.get('skeleton_name')}`")
            lines.append(
                f"- **Target Bone**: `{result.data.get('bone_name')}` (Index: {result.data.get('bone_index')})"
            )
            if result.data.get("position_offset"):
                lines.append(
                    f"- **Position Offset**: `{result.data.get('position_offset')}`"
                )

        elif (
            "ik_node_name" in result.data
            and "root_bone" in result.data
            and "tip_bone" in result.data
        ):
            lines.append(
                f"**Configured SkeletonIK3D**: `{result.data.get('ik_node_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('ik_node_path')}`")
            lines.append(f"- **Skeleton**: `{result.data.get('skeleton_name')}`")
            lines.append(f"- **Root Bone**: `{result.data.get('root_bone')}`")
            lines.append(f"- **Tip Bone**: `{result.data.get('tip_bone')}`")
            lines.append(f"- **Interpolation**: `{result.data.get('interpolation')}`")
            lines.append(f"- **Magnet Enabled**: `{result.data.get('use_magnet')}`")

        elif "joint_name" in result.data and "joint_type" in result.data:
            lines.append(
                f"**Configured Physics Joint**: `{result.data.get('joint_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('joint_path')}`")
            lines.append(
                f"- **Joint Type**: `{result.data.get('joint_type', '').upper()}`"
            )
            lines.append(f"- **Node A**: `{result.data.get('node_a')}`")
            lines.append(f"- **Node B**: `{result.data.get('node_b')}`")
            if result.data.get("applied_parameters"):
                params_str = ", ".join(
                    str(p) for p in result.data.get("applied_parameters", [])
                )
                lines.append(f"- **Parameters Configured**: `{params_str}`")

        elif "physical_bones_count" in result.data and "physical_bones" in result.data:
            lines.append("**Generated Ragdoll Physical Bones**\n")
            lines.append(f"- **Skeleton**: `{result.data.get('skeleton_name')}`")
            lines.append(
                f"- **Physical Bones Created**: `{result.data.get('physical_bones_count')}`"
            )
            lines.append(
                f"- **Shape Type**: `{result.data.get('shape_type', '').upper()}`"
            )
            lines.append(
                f"- **Mass per Bone**: `{result.data.get('mass_per_bone')} kg`"
            )
            lines.append("- **Bones**:")
            for pb in result.data.get("physical_bones", [])[:10]:
                lines.append(f"  - `{pb}`")
            if len(result.data.get("physical_bones", [])) > 10:
                lines.append(
                    f"  - *... and {len(result.data.get('physical_bones', [])) - 10} more physical bones*"
                )

        elif "gi_name" in result.data and "gi_type" in result.data:
            lines.append(
                f"**Configured Global Illumination**: `{result.data.get('gi_name')}`\n"
            )
            lines.append(f"- **Path**: `{result.data.get('gi_path')}`")
            lines.append(f"- **GI Type**: `{result.data.get('gi_type', '').upper()}`")
            if result.data.get("quality"):
                lines.append(
                    f"- **Quality**: `{result.data.get('quality', '').upper()}`"
                )
            if result.data.get("bounces") is not None:
                lines.append(f"- **Bounces**: `{result.data.get('bounces')}`")
            if result.data.get("use_denoiser") is not None:
                lines.append(
                    f"- **Denoiser**: `{result.data.get('denoiser_name', '').upper()}` (Enabled: `{result.data.get('use_denoiser')}`)"
                )
            if result.data.get("interior") is not None:
                lines.append(
                    f"- **Interior Environment**: `{result.data.get('interior')}`"
                )

        elif "gi_name" in result.data and "bake_mode" in result.data:
            lines.append(f"**Lightmap Bake Summary**: `{result.data.get('gi_name')}`\n")
            lines.append(f"- **Path**: `{result.data.get('gi_path')}`")
            lines.append(f"- **Scope**: `{result.data.get('bake_mode', '').upper()}`")
            lines.append(f"- **Status**: `{result.data.get('status')}`")
            if result.data.get("save_path"):
                lines.append(f"- **Saved Resource**: `{result.data.get('save_path')}`")

        elif "class_name" in result.data:
            c_name = result.data.get("class_name")

            inherits = result.data.get("inherits", "")
            can_inst = result.data.get("is_instantiable", False)
            lines.append(
                f"#### Class `{c_name}` (inherits `{inherits}`, instantiable: `{can_inst}`)"
            )

            if "properties" in result.data:
                props = result.data["properties"]
                lines.append(f"\n**Properties ({len(props)})**:")
                for p in props[:20]:
                    hint_str = (
                        f" [hint: {p['hint_string']}]" if p.get("hint_string") else ""
                    )
                    lines.append(f"- `{p['name']}`: `{p['type']}`{hint_str}")
                if len(props) > 20:
                    lines.append(f"- *... and {len(props) - 20} more properties*")

            if "methods" in result.data:
                methods = result.data["methods"]
                lines.append(f"\n**Methods ({len(methods)})**:")
                for m in methods[:20]:
                    args_str = ", ".join(
                        f"{a['name']}: {a['type']}" for a in m.get("args", [])
                    )
                    ret = m.get("return_type", "void")
                    lines.append(f"- `func {m['name']}({args_str}) -> {ret}`")
                if len(methods) > 20:
                    lines.append(f"- *... and {len(methods) - 20} more methods*")

            if "signals" in result.data:
                signals = result.data["signals"]
                lines.append(f"\n**Signals ({len(signals)})**:")
                for s in signals:
                    args_str = ", ".join(
                        f"{a['name']}: {a['type']}" for a in s.get("args", [])
                    )
                    lines.append(f"- `signal {s['name']}({args_str})`")

            if result.data.get("enums"):
                lines.append(f"\n**Enums ({len(result.data['enums'])})**:")
                for e_name, consts in result.data["enums"].items():
                    consts_str = ", ".join(
                        f"{k} = {v}" for k, v in list(consts.items())[:5]
                    )
                    lines.append(f"- `enum {e_name}`: `{consts_str}`")

            if result.data.get("constants"):
                lines.append(f"\n**Constants ({len(result.data['constants'])})**:")
                for c_name, val in list(result.data["constants"].items())[:15]:
                    lines.append(f"- `{c_name}` = `{val}`")
                if len(result.data["constants"]) > 15:
                    lines.append(
                        f"- *... and {len(result.data['constants']) - 15} more constants*"
                    )

        elif "errors" in result.data and not result.success:
            lines.append("\n**Compilation Errors**:")
            for err in result.data.get("errors", []):
                lines.append(f"- `{err}`")

        else:
            lines.append("```json")
            lines.append(json.dumps(result.data, indent=2))
            lines.append("```")

    return "\n".join(lines)
