@tool
extends RefCounted

## Operations for Godot Autoload singleton management in project.godot.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_autoloads(params: Dictionary) -> Dictionary:
	var autoloads: Array = []
	var cfg_path = "res://project.godot"
	var config = ConfigFile.new()
	var err = config.load(cfg_path)
	if err != OK:
		return {"success": false, "message": "Failed to load project.godot (Error: %d)." % err}

	if config.has_section("autoload"):
		for key in config.get_section_keys("autoload"):
			var raw_val = str(config.get_value("autoload", key, ""))
			var is_singleton = raw_val.begins_with("*")
			var res_path = raw_val.trim_prefix("*")

			autoloads.append({
				"name": key,
				"path": res_path,
				"is_singleton": is_singleton,
				"exists": ResourceLoader.exists(res_path) or FileAccess.file_exists(res_path)
			})

	return {
		"success": true,
		"message": "Found %d autoload singletons in project.godot." % autoloads.size(),
		"data": {
			"autoload_count": autoloads.size(),
			"autoloads": autoloads
		}
	}

func set_autoload(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "")
	if name == "":
		return {"success": false, "message": "name cannot be empty."}

	var remove: bool = bool(params.get("remove", false))
	var setting_key = "autoload/" + name

	if remove:
		if ProjectSettings.has_setting(setting_key):
			ProjectSettings.set_setting(setting_key, null)
			ProjectSettings.save()
			if _plugin:
				_plugin.remove_autoload_singleton(name)
			return {
				"success": true,
				"message": "Removed autoload singleton '%s'." % name,
				"data": {"name": name, "removed": true}
			}
		else:
			return {"success": false, "message": "Autoload '%s' does not exist." % name}

	var path: String = params.get("path", "")
	if path == "":
		return {"success": false, "message": "path cannot be empty when adding or updating an autoload."}

	var is_singleton: bool = bool(params.get("is_singleton", true))
	var prefix = "*" if is_singleton else ""
	var full_val = prefix + path

	ProjectSettings.set_setting(setting_key, full_val)
	ProjectSettings.save()

	if _plugin and is_singleton:
		if ResourceLoader.exists(path):
			_plugin.add_autoload_singleton(name, path)

	return {
		"success": true,
		"message": "Configured autoload '%s' -> '%s' (Singleton: %s)." % [name, path, str(is_singleton)],
		"data": {
			"name": name,
			"path": path,
			"is_singleton": is_singleton,
			"setting_key": setting_key
		}
	}
