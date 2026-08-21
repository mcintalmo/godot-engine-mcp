@tool
extends RefCounted

## Operations for Godot Scene Tree and .tscn structural and property diffing.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func diff_scene(params: Dictionary) -> Dictionary:
	var live_root: Node = null
	if _plugin:
		live_root = _plugin.get_editor_interface().get_edited_scene_root()

	var disk_scene_path: String = params.get("scene_path", "")
	var target_scene_path: String = params.get("target_scene_path", "")

	var base_node: Node = null
	var target_node: Node = null
	var base_label: String = ""
	var target_label: String = ""
	var must_free_base: bool = false
	var must_free_target: bool = false

	if target_scene_path != "":
		if not FileAccess.file_exists(disk_scene_path) or not FileAccess.file_exists(target_scene_path):
			return {"success": false, "message": "One or both scene files do not exist."}
		var base_packed = load(disk_scene_path)
		var target_packed = load(target_scene_path)
		if not (base_packed is PackedScene) or not (target_packed is PackedScene):
			return {"success": false, "message": "One or both files are not valid PackedScenes."}
		base_node = base_packed.instantiate()
		target_node = target_packed.instantiate()
		base_label = disk_scene_path
		target_label = target_scene_path
		must_free_base = true
		must_free_target = true
	else:
		if not live_root:
			return {"success": false, "message": "No active scene open in editor to diff against."}
		target_node = live_root
		target_label = "Live Scene in Editor"

		var p = disk_scene_path if disk_scene_path != "" else live_root.scene_file_path
		if p == "" or not FileAccess.file_exists(p):
			return {"success": false, "message": "No saved scene file path found on disk to compare with."}
		var base_packed = load(p)
		if not (base_packed is PackedScene):
			return {"success": false, "message": "Failed to load saved PackedScene '%s'." % p}
		base_node = base_packed.instantiate()
		base_label = p
		must_free_base = true

	var base_map = _build_node_map(base_node, "")
	var target_map = _build_node_map(target_node, "")

	var added_nodes: Array = []
	var removed_nodes: Array = []
	var modified_nodes: Array = []

	for path in target_map:
		if not base_map.has(path):
			added_nodes.append({
				"path": path,
				"class": target_map[path].get("class", "Node")
			})
		else:
			var diffs = _compare_node_props(base_map[path], target_map[path])
			if diffs.size() > 0:
				modified_nodes.append({
					"path": path,
					"class": target_map[path].get("class", "Node"),
					"changes": diffs
				})

	for path in base_map:
		if not target_map.has(path):
			removed_nodes.append({
				"path": path,
				"class": base_map[path].get("class", "Node")
			})

	if must_free_base and is_instance_valid(base_node):
		base_node.free()
	if must_free_target and is_instance_valid(target_node):
		target_node.free()

	return {
		"success": true,
		"message": "Scene Diff: %d added, %d removed, %d modified nodes." % [added_nodes.size(), removed_nodes.size(), modified_nodes.size()],
		"data": {
			"base": base_label,
			"target": target_label,
			"added_count": added_nodes.size(),
			"removed_count": removed_nodes.size(),
			"modified_count": modified_nodes.size(),
			"added_nodes": added_nodes,
			"removed_nodes": removed_nodes,
			"modified_nodes": modified_nodes
		}
	}

func _build_node_map(node: Node, current_path: String) -> Dictionary:
	var map: Dictionary = {}
	if not node:
		return map

	var node_p = current_path + "/" + node.name if current_path != "" else node.name
	var props = {
		"class": node.get_class(),
		"visible": node.visible if "visible" in node else null,
		"position": str(node.position) if "position" in node else null,
		"rotation": str(node.rotation) if "rotation" in node else null,
		"scale": str(node.scale) if "scale" in node else null,
		"script": node.get_script().resource_path if node.get_script() else null
	}
	map[node_p] = props

	for child in node.get_children():
		var child_map = _build_node_map(child, node_p)
		for k in child_map:
			map[k] = child_map[k]

	return map

func _compare_node_props(base_p: Dictionary, target_p: Dictionary) -> Array:
	var changes: Array = []
	for k in ["class", "visible", "position", "rotation", "scale", "script"]:
		var b_val = base_p.get(k)
		var t_val = target_p.get(k)
		if b_val != t_val and b_val != null and t_val != null:
			changes.append({
				"property": k,
				"base_value": b_val,
				"target_value": t_val
			})
	return changes
