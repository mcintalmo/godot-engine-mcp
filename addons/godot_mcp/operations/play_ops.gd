@tool
extends RefCounted

## Operations for Godot Play Mode, pause state, time scale, and frame stepping.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func play_scene(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var mode: String = params.get("mode", "main").to_lower()

	match mode:
		"main":
			editor_interface.play_main_scene()
			return {
				"success": true,
				"message": "Playing project main scene.",
				"data": {"mode": "main", "is_playing": true}
			}
		"current":
			editor_interface.play_current_scene()
			var edited_root = editor_interface.get_edited_scene_root()
			var scene_name = edited_root.name if edited_root else "current"
			return {
				"success": true,
				"message": "Playing current active scene tab ('%s')." % scene_name,
				"data": {"mode": "current", "scene_name": scene_name, "is_playing": true}
			}
		"custom":
			var custom_path: String = params.get("custom_scene_path", "")
			if custom_path == "":
				return {"success": false, "message": "custom_scene_path cannot be empty when mode is 'custom'."}
			editor_interface.play_custom_scene(custom_path)
			return {
				"success": true,
				"message": "Playing custom scene '%s'." % custom_path,
				"data": {"mode": "custom", "custom_scene_path": custom_path, "is_playing": true}
			}
		_:
			return {"success": false, "message": "Unknown play mode: '%s'." % mode}

func stop_scene(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var was_playing = editor_interface.is_playing_scene()
	editor_interface.stop_playing_scene()

	return {
		"success": true,
		"message": "Stopped scene playback." if was_playing else "Scene playback was not running.",
		"data": {"was_playing": was_playing, "is_playing": false}
	}

func get_play_state(params: Dictionary) -> Dictionary:
	var is_playing = false
	var active_scene = ""

	if _plugin:
		var editor_interface = _plugin.get_editor_interface()
		is_playing = editor_interface.is_playing_scene()
		var edited_root = editor_interface.get_edited_scene_root()
		if edited_root:
			active_scene = edited_root.scene_file_path if edited_root.scene_file_path != "" else edited_root.name

	var is_paused = _plugin.get_tree().paused if _plugin else false
	var time_scale = Engine.time_scale

	return {
		"success": true,
		"message": "Play State: %s (Time Scale: %.2fx, Paused: %s)" % [
			"PLAYING" if is_playing else "STOPPED",
			time_scale,
			"TRUE" if is_paused else "FALSE"
		],
		"data": {
			"is_playing": is_playing,
			"is_paused": is_paused,
			"time_scale": time_scale,
			"active_editor_scene": active_scene
		}
	}

func set_play_state(params: Dictionary) -> Dictionary:
	var applied_changes: Array[String] = []

	if params.has("time_scale") and params["time_scale"] != null:
		var ts = maxf(float(params["time_scale"]), 0.0)
		Engine.time_scale = ts
		applied_changes.append("time_scale = %.2fx" % ts)

	if params.has("pause") and params["pause"] != null and _plugin:
		var p = bool(params["pause"])
		_plugin.get_tree().paused = p
		applied_changes.append("paused = %s" % ("true" if p else "false"))

	var stepped = null
	if params.has("step_frames") and params["step_frames"] != null and _plugin:
		var count = int(params["step_frames"])
		if count > 0:
			_step_frames_coroutine(count)
			stepped = count
			applied_changes.append("stepped %d frames" % count)

	return {
		"success": true,
		"message": "Updated play state (%s)." % (", ".join(applied_changes) if applied_changes.size() > 0 else "no changes"),
		"data": {
			"is_paused": _plugin.get_tree().paused if _plugin else false,
			"time_scale": Engine.time_scale,
			"stepped_frames": stepped
		}
	}

func _step_frames_coroutine(frames: int) -> void:
	if not _plugin:
		return
	var tree = _plugin.get_tree()
	tree.paused = false
	for i in range(frames):
		await tree.physics_frame
	tree.paused = true
