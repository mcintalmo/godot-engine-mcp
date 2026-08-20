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

        elif "material_path" in result.data:
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
