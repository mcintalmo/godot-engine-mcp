@tool
extends RefCounted

## Operations for Godot Editor Workspace Layout and Screen Control.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_editor_layout(params: Dictionary) -> Dictionary:
	var include_scenes = bool(params.get("include_open_scenes", True))
	var editor_scale = 1.0
	var df_mode = false
	var open_scenes: Array = []
	var edited_root_path = ""

	if _plugin:
		var ei = _plugin.get_editor_interface()
		if ei:
			editor_scale = ei.get_editor_scale()
			df_mode = ei.is_distraction_free_mode_enabled()
			if include_scenes:
				open_scenes = ei.get_open_scenes()
			var root = ei.get_edited_scene_root()
			if root:
				edited_root_path = root.scene_file_path if root.scene_file_path != "" else root.name

	return {
		"success": true,
		"message": "Editor layout retrieved (Scale: %.2fx, Distraction-Free: %s, Open Scenes: %d)." % [editor_scale, str(df_mode), open_scenes.size()],
		"data": {
			"editor_scale": editor_scale,
			"distraction_free_mode": df_mode,
			"edited_scene_root": edited_root_path,
			"open_scenes_count": open_scenes.size(),
			"open_scenes": open_scenes
		}
	}

func set_editor_layout(params: Dictionary) -> Dictionary:
	var main_screen = params.get("main_screen")
	var df_mode = params.get("distraction_free_mode")
	var scene_path = params.get("active_scene_path")

	var changes: Array = []

	if _plugin:
		var ei = _plugin.get_editor_interface()
		if ei:
			if main_screen != null and str(main_screen) != "":
				var scr_str = str(main_screen)
				ei.set_main_screen_editor(scr_str)
				changes.append("Main Screen: %s" % scr_str)

			if df_mode != null:
				ei.set_distraction_free_mode(bool(df_mode))
				changes.append("Distraction-Free: %s" % str(df_mode))

			if scene_path != null and str(scene_path) != "":
				ei.open_scene_from_path(str(scene_path))
				changes.append("Opened Scene: %s" % str(scene_path))

	var msg = "Updated editor layout: %s." % (", ".join(changes) if changes.size() > 0 else "No modifications")
	return {
		"success": true,
		"message": msg,
		"data": {
			"main_screen": main_screen,
			"distraction_free_mode": df_mode,
			"active_scene_path": scene_path,
			"changes_applied": changes
		}
	}
