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
