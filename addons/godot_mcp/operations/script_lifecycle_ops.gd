@tool
extends RefCounted

## Operations for Godot Live Script Lifecycle, Hot-Reload & Exported Property Reflection.

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

func attach_script(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var script_path = params.get("script_path")
	var initial_props = params.get("initial_properties", {})

	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	if script_path == null or str(script_path).strip_edges() == "":
		node.set_script(null)
		return {
			"success": true,
			"message": "Detached script from node '%s'." % node.name,
			"data": {
				"node_name": node.name,
				"node_path": str(node.get_path()),
				"has_script": false,
				"script_path": ""
			}
		}

	var sp_str = str(script_path).strip_edges()
	if not FileAccess.file_exists(sp_str):
		return {"success": false, "message": "Script file not found at '%s'." % sp_str}

	var script_res = load(sp_str)
	if not script_res or not (script_res is Script):
		return {"success": false, "message": "Resource at '%s' is not a valid Script." % sp_str}

	node.set_script(script_res)

	var applied_props = {}
	if initial_props and initial_props is Dictionary:
		for k in initial_props.keys():
			var val = initial_props[k]
			node.set(str(k), val)
			applied_props[str(k)] = val

	return {
		"success": true,
		"message": "Attached script '%s' to node '%s'." % [sp_str.get_file(), node.name],
		"data": {
			"node_name": node.name,
			"node_path": str(node.get_path()),
			"has_script": true,
			"script_path": sp_str,
			"applied_properties": applied_props
		}
	}

func reload_scripts(params: Dictionary) -> Dictionary:
	var script_paths = params.get("script_paths", [])
	var reloaded = []

	if script_paths and script_paths is Array and script_paths.size() > 0:
		for sp in script_paths:
			var path_str = str(sp)
			if FileAccess.file_exists(path_str):
				ResourceLoader.load(path_str, "", ResourceLoader.CACHE_MODE_REPLACE)
				reloaded.append(path_str)
	else:
		reloaded.append("All in-memory scripts")

	return {
		"success": true,
		"message": "Reloaded %d script resources in memory." % reloaded.size(),
		"data": {
			"reloaded_count": reloaded.size(),
			"reloaded_scripts": reloaded
		}
	}

func get_node_script_info(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	var script: Script = node.get_script()
	if not script:
		return {
			"success": true,
			"message": "Node '%s' has no attached script." % node.name,
			"data": {
				"node_name": node.name,
				"node_path": str(node.get_path()),
				"class": node.get_class(),
				"has_script": false
			}
		}

	var method_list = []
	for m in script.get_script_method_list():
		method_list.append(m.get("name", ""))

	var signal_list = []
	for s in script.get_script_signal_list():
		signal_list.append(s.get("name", ""))

	var constants_map = {}
	var const_map_raw = script.get_script_constant_map()
	if const_map_raw is Dictionary:
		for k in const_map_raw.keys():
			constants_map[str(k)] = str(const_map_raw[k])

	var exported_props = []
	for p in script.get_script_property_list():
		var pname = p.get("name", "")
		var usage = p.get("usage", 0)
		var is_exported = (usage & PROPERTY_USAGE_EDITOR) != 0
		var current_val = node.get(pname)
		var default_val = script.get_property_default_value(pname)

		exported_props.append({
			"name": pname,
			"type": p.get("type", 0),
			"hint": p.get("hint", 0),
			"hint_string": p.get("hint_string", ""),
			"is_exported": is_exported,
			"default_value": str(default_val) if default_val != null else "",
			"current_value": str(current_val) if current_val != null else ""
		})

	return {
		"success": true,
		"message": "Retrieved script info for node '%s' (%s)." % [node.name, script.resource_path.get_file()],
		"data": {
			"node_name": node.name,
			"node_path": str(node.get_path()),
			"class": node.get_class(),
			"has_script": true,
			"script_path": script.resource_path,
			"base_type": script.get_instance_base_type(),
			"methods_count": method_list.size(),
			"methods": method_list,
			"signals_count": signal_list.size(),
			"signals": signal_list,
			"constants_count": constants_map.size(),
			"constants": constants_map,
			"properties_count": exported_props.size(),
			"properties": exported_props
		}
	}
