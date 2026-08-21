@tool
extends RefCounted

## Operations for Godot Editor SceneTree selection and Inspector inspection focus.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_selected_nodes(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not available."}

	var sel = _plugin.get_editor_interface().get_selection()
	if not sel:
		return {"success": false, "message": "EditorSelection not accessible."}

	var include_props = bool(params.get("include_properties", true))
	var nodes = sel.get_selected_nodes()
	var result_list: Array = []

	for n in nodes:
		if is_instance_valid(n) and n is Node:
			var item = {
				"name": n.name,
				"path": str(n.get_path()),
				"class": n.get_class()
			}
			if include_props:
				if "position" in n:
					item["position"] = str(n.position)
				if "visible" in n:
					item["visible"] = n.visible
				if n.get_script():
					item["script"] = n.get_script().resource_path
			result_list.append(item)

	return {
		"success": true,
		"message": "Found %d selected nodes in editor." % result_list.size(),
		"data": {
			"selection_count": result_list.size(),
			"selected_nodes": result_list
		}
	}

func set_selected_nodes(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not available."}

	var root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var sel = _plugin.get_editor_interface().get_selection()
	if not sel:
		return {"success": false, "message": "EditorSelection not accessible."}

	var clear_prev = bool(params.get("clear_previous", true))
	if clear_prev:
		sel.clear()

	var paths = params.get("node_paths", [])
	var matched: Array = []
	var primary_node: Node = null

	for p in paths:
		var target: Node = null
		if str(p).begins_with("/root/"):
			target = root.get_tree().root.get_node_or_null(str(p))
		else:
			target = root.get_node_or_null(str(p))
			if not target:
				target = root.find_child(str(p), true, false)

		if target and is_instance_valid(target):
			sel.add_node(target)
			matched.append({
				"name": target.name,
				"path": str(target.get_path()),
				"class": target.get_class()
			})
			if not primary_node:
				primary_node = target

	var inspect = bool(params.get("inspect_primary", true))
	if inspect and primary_node:
		_plugin.get_editor_interface().edit_node(primary_node)

	return {
		"success": true,
		"message": "Selected %d nodes in editor (primary inspected: %s)." % [matched.size(), primary_node.name if primary_node else "None"],
		"data": {
			"selected_count": matched.size(),
			"selected_nodes": matched,
			"inspected_node": primary_node.name if primary_node else null
		}
	}
