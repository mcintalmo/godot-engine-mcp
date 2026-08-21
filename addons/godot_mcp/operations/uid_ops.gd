@tool
extends RefCounted

## Operations for Godot Resource UIDs, UID-to-Path resolution, and scene/resource dependency graphs.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_uid(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path == "":
		return {"success": false, "message": "path cannot be empty."}

	var numeric_id = ResourceLoader.get_resource_uid(path)
	if numeric_id == ResourceUID.INVALID_ID:
		return {"success": false, "message": "No valid UID found for resource '%s'." % path}

	var uid_str = ResourceUID.id_to_text(numeric_id)
	return {
		"success": true,
		"message": "Resource '%s' has UID '%s'." % [path, uid_str],
		"data": {
			"path": path,
			"uid": uid_str,
			"numeric_id": numeric_id
		}
	}

func resolve_uid(params: Dictionary) -> Dictionary:
	var uid_str: String = params.get("uid", "")
	if uid_str == "":
		return {"success": false, "message": "uid cannot be empty."}

	var numeric_id = ResourceUID.text_to_id(uid_str)
	if numeric_id == ResourceUID.INVALID_ID:
		return {"success": false, "message": "Invalid UID string '%s'." % uid_str}

	if not ResourceUID.has_id(numeric_id):
		return {"success": false, "message": "UID '%s' is not registered in the project's UID cache." % uid_str}

	var resolved_path = ResourceUID.get_id_path(numeric_id)
	return {
		"success": true,
		"message": "Resolved UID '%s' to '%s'." % [uid_str, resolved_path],
		"data": {
			"uid": uid_str,
			"path": resolved_path,
			"numeric_id": numeric_id
		}
	}

func get_dependencies(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path == "":
		return {"success": false, "message": "path cannot be empty."}

	var raw_deps = ResourceLoader.get_dependencies(path)
	var dep_list: Array = []

	for dep in raw_deps:
		var dep_str = str(dep)
		var resolved = dep_str
		var is_uid = dep_str.begins_with("uid://")
		if is_uid:
			var id = ResourceUID.text_to_id(dep_str)
			if id != ResourceUID.INVALID_ID and ResourceUID.has_id(id):
				resolved = ResourceUID.get_id_path(id)

		dep_list.append({
			"raw": dep_str,
			"resolved_path": resolved,
			"is_uid": is_uid,
			"exists": FileAccess.file_exists(resolved) or ResourceLoader.exists(resolved)
		})

	return {
		"success": true,
		"message": "Found %d dependencies for '%s'." % [dep_list.size(), path],
		"data": {
			"source_path": path,
			"dependency_count": dep_list.size(),
			"dependencies": dep_list
		}
	}
