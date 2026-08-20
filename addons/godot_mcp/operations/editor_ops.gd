@tool
extends RefCounted

## Operations for Godot Editor selection, node focus in Inspector, and 2D/3D workspace transitions.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func set_editor_selection(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin not initialized."}

	var root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_paths: Array = params.get("node_paths", [])
	var clear_prev: bool = bool(params.get("clear_previous", true))
	var selection = _plugin.get_editor_interface().get_selection()

	if clear_prev:
		selection.clear()

	var selected_nodes: Array[String] = []
	for p in node_paths:
		var target = root.get_node_or_null(str(p))
		if target:
			selection.add_node(target)
			selected_nodes.append(str(target.get_path()))

	return {
		"success": true,
		"message": "Selected %d nodes in the Scene Tree dock." % selected_nodes.size(),
		"data": {
			"selected_count": selected_nodes.size(),
			"selected_nodes": selected_nodes
		}
	}

func focus_node(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin not initialized."}

	var root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_path: String = params.get("node_path", "")
	var target = root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at path '%s'." % node_path}

	var editor_interface = _plugin.get_editor_interface()
	editor_interface.edit_node(target)

	var main_screen = params.get("main_screen")
	if main_screen and str(main_screen) != "":
		editor_interface.set_main_screen_editor(str(main_screen))
	elif target is Node3D:
		editor_interface.set_main_screen_editor("3D")
	elif target is CanvasItem:
		editor_interface.set_main_screen_editor("2D")

	return {
		"success": true,
		"message": "Focused node '%s' (%s) in Inspector and viewport." % [target.name, target.get_class()],
		"data": {
			"node_name": target.name,
			"node_path": str(target.get_path()),
			"node_class": target.get_class()
		}
	}
