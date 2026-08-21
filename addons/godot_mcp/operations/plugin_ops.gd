@tool
extends RefCounted

## Operations for Godot Editor Plugin / Addon discovery and dynamic activation.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_plugins(params: Dictionary) -> Dictionary:
	var enabled_only = bool(params.get("enabled_only", false))
	var plugins: Array = []
	var enabled_list = ProjectSettings.get_setting("editor_plugins/enabled", PackedStringArray())

	var dir = DirAccess.open("res://addons")
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if dir.current_is_dir() and not file_name.begins_with("."):
				var cfg_path = "res://addons/" + file_name + "/plugin.cfg"
				if FileAccess.file_exists(cfg_path):
					var cfg = ConfigFile.new()
					var err = cfg.load(cfg_path)
					var p_name = cfg.get_value("plugin", "name", file_name)
					var desc = cfg.get_value("plugin", "description", "")
					var author = cfg.get_value("plugin", "author", "")
					var ver = cfg.get_value("plugin", "version", "")
					var script_rel = cfg.get_value("plugin", "script", "")
					var script_path = "res://addons/" + file_name + "/" + script_rel if script_rel != "" else ""

					var is_enabled = false
					if _plugin and _plugin.get_editor_interface():
						is_enabled = _plugin.get_editor_interface().is_plugin_enabled(file_name)
					else:
						for item in enabled_list:
							if str(item) == cfg_path or str(item) == file_name:
								is_enabled = true
								break

					if not enabled_only or is_enabled:
						plugins.append({
							"id": file_name,
							"name": p_name,
							"description": desc,
							"author": author,
							"version": ver,
							"script_path": script_path,
							"config_path": cfg_path,
							"enabled": is_enabled
						})
			file_name = dir.get_next()
		dir.list_dir_end()

	return {
		"success": true,
		"message": "Found %d editor plugins in res://addons/." % plugins.size(),
		"data": {
			"plugin_count": plugins.size(),
			"plugins": plugins
		}
	}

func set_plugin_status(params: Dictionary) -> Dictionary:
	var plugin_name: String = params.get("plugin_name", "")
	if plugin_name == "":
		return {"success": false, "message": "plugin_name cannot be empty."}

	var enabled = bool(params.get("enabled", true))
	var cfg_path = "res://addons/" + plugin_name + "/plugin.cfg"

	if not FileAccess.file_exists(cfg_path):
		return {"success": false, "message": "Plugin configuration not found at '%s'." % cfg_path}

	if _plugin and _plugin.get_editor_interface():
		_plugin.get_editor_interface().set_plugin_enabled(plugin_name, enabled)

	# Update project.godot setting for persistence
	var setting_key = "editor_plugins/enabled"
	var existing = ProjectSettings.get_setting(setting_key, PackedStringArray())
	var updated_arr: Array = []
	for item in existing:
		var s = str(item)
		if s != cfg_path and s != plugin_name:
			updated_arr.append(s)

	if enabled:
		updated_arr.append(cfg_path)

	ProjectSettings.set_setting(setting_key, PackedStringArray(updated_arr))
	ProjectSettings.save()

	var state_str = "Enabled" if enabled else "Disabled"
	return {
		"success": true,
		"message": "%s editor plugin '%s'." % [state_str, plugin_name],
		"data": {
			"plugin_id": plugin_name,
			"config_path": cfg_path,
			"enabled": enabled
		}
	}
