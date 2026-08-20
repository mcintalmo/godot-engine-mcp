@tool
extends RefCounted

## Operations for Godot export preset inspection.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_export_presets(params: Dictionary) -> Dictionary:
	var cfg_path = "res://export_presets.cfg"
	if not FileAccess.file_exists(cfg_path):
		return {
			"success": true,
			"message": "No export_presets.cfg found in project root.",
			"data": {"preset_count": 0, "presets": []}
		}

	var config = ConfigFile.new()
	var err = config.load(cfg_path)
	if err != OK:
		return {"success": false, "message": "Failed to parse export_presets.cfg (Error: %d)." % err}

	var presets: Array = []
	for section in config.get_sections():
		if section.begins_with("preset."):
			var pname = config.get_value(section, "name", "")
			var platform = config.get_value(section, "platform", "")
			var export_path = config.get_value(section, "export_path", "")
			var runnable = config.get_value(section, "runnable", true)

			presets.append({
				"preset_id": section,
				"name": pname,
				"platform": platform,
				"export_path": export_path,
				"runnable": runnable
			})

	return {
		"success": true,
		"message": "Found %d export presets in export_presets.cfg." % presets.size(),
		"data": {"preset_count": presets.size(), "presets": presets}
	}
