@tool
class_name ProjectOperations
extends RefCounted

var _plugin: Node

func _init(plugin: Node = null) -> void:
	_plugin = plugin


func get_version(params: Dictionary = {}) -> Dictionary:
	var v_info = Engine.get_version_info()
	var active_scene: Variant = null
	if _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei and ei.get_edited_scene_root():
			active_scene = ei.get_edited_scene_root().scene_file_path

	return {
		"success": true,
		"version_string": "%d.%d.%d.%s" % [v_info.major, v_info.minor, v_info.patch, v_info.status],
		"major": v_info.major,
		"minor": v_info.minor,
		"patch": v_info.patch,
		"status": v_info.status,
		"build": v_info.build,
		"mode": "live_editor",
		"active_scene": active_scene
	}


func get_project_settings(params: Dictionary) -> Dictionary:
	var section_filter = params.get("section", "")
	var settings = {}

	for prop in ProjectSettings.get_property_list():
		var name: String = prop.name
		if section_filter == "" or name.begins_with(section_filter):
			settings[name] = ProjectSettings.get_setting(name)

	return {
		"success": true,
		"settings": settings,
		"count": settings.size()
	}

func set_project_setting(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "")
	var val: Variant = params.get("value")
	if name == "":
		return {"success": false, "message": "Setting name cannot be empty."}

	ProjectSettings.set_setting(name, val)
	ProjectSettings.save()

	return {
		"success": true,
		"message": "Set project setting '%s' to '%s'" % [name, str(val)],
		"name": name,
		"value": val
	}

func restart_editor(params: Dictionary) -> Dictionary:
	if _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei and ei.has_method("restart_editor"):
			var save = bool(params.get("save", true))
			ei.restart_editor(save)
			return {"success": true, "message": "Editor restart initiated."}
	return {"success": false, "message": "EditorInterface is not available to restart editor."}

