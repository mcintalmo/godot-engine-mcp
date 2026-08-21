@tool
extends RefCounted

## Operations for Godot Scene Hierarchy Mutations and Packed Scene Instantiation.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _get_scene_root() -> Node:
	if _plugin:
		var ei = _plugin.get_editor_interface()
		if ei:
			return ei.get_edited_scene_root()
	return null

func _find_node(path_str: String, root: Node) -> Node:
	if not root:
		return null
	if path_str == "." or path_str == "" or path_str == root.name or path_str == "/root":
		return root
	if root.has_node(path_str):
		return root.get_node(path_str)
	return null

func _set_owner_recursive(node: Node, owner_node: Node) -> void:
	if node != owner_node:
		node.owner = owner_node
	for c in node.get_children():
		_set_owner_recursive(c, owner_node)

func reparent_node(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var parent_path = str(params.get("new_parent_path", "."))
	var keep_transform = bool(params.get("keep_global_transform", true))
	var new_index = params.get("new_index")

	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	if node == root:
		return {"success": false, "message": "Cannot reparent the root node of the scene."}

	var new_parent = _find_node(parent_path, root)
	if not new_parent:
		return {"success": false, "message": "Target parent node not found at '%s'." % parent_path}

	var old_parent_path = str(node.get_parent().get_path()) if node.get_parent() else ""
	node.reparent(new_parent, keep_transform)

	if new_index != null:
		new_parent.move_child(node, int(new_index))

	_set_owner_recursive(node, root)

	return {
		"success": true,
		"message": "Reparented node '%s' to '%s'." % [node.name, new_parent.name],
		"data": {
			"node_name": node.name,
			"old_parent": old_parent_path,
			"new_parent": str(new_parent.get_path()),
			"new_path": str(node.get_path()),
			"keep_global_transform": keep_transform,
			"child_index": node.get_index()
		}
	}

func duplicate_node(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var new_name = params.get("new_name")
	var target_parent_path = params.get("target_parent_path")
	var dup_signals = bool(params.get("duplicate_signals", false))
	var dup_groups = bool(params.get("duplicate_groups", true))
	var dup_scripts = bool(params.get("duplicate_scripts", true))

	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	var flags = 0
	if dup_signals:
		flags |= 1 # DUPLICATE_SIGNALS
	if dup_groups:
		flags |= 2 # DUPLICATE_GROUPS
	if dup_scripts:
		flags |= 4 # DUPLICATE_SCRIPTS
	flags |= 8 # DUPLICATE_USE_INSTANTIATION

	var dup = node.duplicate(flags)
	if not dup:
		return {"success": false, "message": "Failed to duplicate node '%s'." % node_path}

	if new_name != null and str(new_name) != "":
		dup.name = str(new_name)

	var parent = node.get_parent()
	if target_parent_path != null and str(target_parent_path) != "":
		var custom_parent = _find_node(str(target_parent_path), root)
		if custom_parent:
			parent = custom_parent

	if not parent:
		parent = root

	parent.add_child(dup)
	_set_owner_recursive(dup, root)

	return {
		"success": true,
		"message": "Duplicated node '%s' as '%s' under '%s'." % [node.name, dup.name, parent.name],
		"data": {
			"source_path": node_path,
			"duplicated_name": dup.name,
			"duplicated_path": str(dup.get_path()),
			"parent_path": str(parent.get_path()),
			"class": dup.get_class()
		}
	}

func instantiate_scene(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var scene_path = str(params.get("scene_path", ""))
	var parent_path = str(params.get("parent_node_path", "."))
	var inst_name = params.get("instance_name")
	var pos_array = params.get("position")

	if not FileAccess.file_exists(scene_path):
		return {"success": false, "message": "Scene file not found at '%s'." % scene_path}

	var packed: PackedScene = load(scene_path)
	if not packed or not (packed is PackedScene):
		return {"success": false, "message": "Failed to load PackedScene at '%s'." % scene_path}

	var instance = packed.instantiate()
	if not instance:
		return {"success": false, "message": "Failed to instantiate scene from '%s'." % scene_path}

	if inst_name != null and str(inst_name) != "":
		instance.name = str(inst_name)

	if pos_array != null and pos_array is Array:
		if instance is Node3D and pos_array.size() >= 3:
			instance.position = Vector3(float(pos_array[0]), float(pos_array[1]), float(pos_array[2]))
		elif instance is Node2D and pos_array.size() >= 2:
			instance.position = Vector2(float(pos_array[0]), float(pos_array[1]))
		elif instance is Control and pos_array.size() >= 2:
			instance.position = Vector2(float(pos_array[0]), float(pos_array[1]))

	var parent = _find_node(parent_path, root)
	if not parent:
		parent = root

	parent.add_child(instance)
	_set_owner_recursive(instance, root)

	return {
		"success": true,
		"message": "Instantiated scene '%s' as node '%s' under '%s'." % [scene_path.get_file(), instance.name, parent.name],
		"data": {
			"scene_path": scene_path,
			"instance_name": instance.name,
			"instance_path": str(instance.get_path()),
			"parent_path": str(parent.get_path()),
			"class": instance.get_class()
		}
	}

func set_node_owner(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var owner_path = str(params.get("owner_node_path", "."))
	var recursive = bool(params.get("recursive", true))

	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	var owner_node = _find_node(owner_path, root)
	if not owner_node:
		return {"success": false, "message": "Owner node not found at '%s'." % owner_path}

	if recursive:
		_set_owner_recursive(node, owner_node)
	else:
		node.owner = owner_node

	return {
		"success": true,
		"message": "Set owner of node '%s' to '%s' (Recursive: %s)." % [node.name, owner_node.name, str(recursive)],
		"data": {
			"node_path": str(node.get_path()),
			"owner_path": str(owner_node.get_path()),
			"recursive": recursive
		}
	}

