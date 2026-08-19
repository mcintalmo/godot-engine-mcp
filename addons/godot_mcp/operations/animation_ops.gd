@tool
extends RefCounted

## Operations for creating, modifying, and assigning Animation resources and AnimationPlayer tracks.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _coerce_val(val: Variant) -> Variant:
	if typeof(val) == TYPE_ARRAY:
		var arr = val as Array
		if arr.size() == 4:
			return Color(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
		elif arr.size() == 3:
			return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
		elif arr.size() == 2:
			return Vector2(float(arr[0]), float(arr[1]))
	return val

func _get_track_type_enum(type_str: String) -> int:
	match type_str.to_lower():
		"position_3d":
			return Animation.TYPE_POSITION_3D
		"rotation_3d":
			return Animation.TYPE_ROTATION_3D
		"scale_3d":
			return Animation.TYPE_SCALE_3D
		"blend_shape":
			return Animation.TYPE_BLEND_SHAPE
		"method":
			return Animation.TYPE_METHOD
		"bezier":
			return Animation.TYPE_BEZIER
		"audio":
			return Animation.TYPE_AUDIO
		"animation":
			return Animation.TYPE_ANIMATION
		"value", _:
			return Animation.TYPE_VALUE

func _get_loop_mode_enum(loop_str: String) -> int:
	match loop_str.to_lower():
		"linear":
			return Animation.LOOP_LINEAR
		"pingpong":
			return Animation.LOOP_PINGPONG
		"none", _:
			return Animation.LOOP_NONE

func _get_interpolation_enum(interp_str: String) -> int:
	match interp_str.to_lower():
		"nearest":
			return Animation.INTERPOLATION_NEAREST
		"cubic":
			return Animation.INTERPOLATION_CUBIC
		"linear", _:
			return Animation.INTERPOLATION_LINEAR

func create_animation(params: Dictionary) -> Dictionary:
	var animation_name: String = params.get("animation_name", "new_animation")
	var length: float = float(params.get("length", 1.0))
	var loop_mode: String = params.get("loop_mode", "none")
	var step: float = float(params.get("step", 0.1))
	var tracks: Array = params.get("tracks", [])
	var anim_player_path: String = params.get("animation_player_path", "")
	var save_path: String = params.get("save_path", "")

	if animation_name == "":
		return {"success": false, "message": "animation_name parameter cannot be empty."}

	# 1. Instantiate and configure Animation resource
	var anim: Animation = Animation.new()
	anim.length = length
	anim.loop_mode = _get_loop_mode_enum(loop_mode)
	anim.step = step

	var track_count: int = 0
	var keyframe_count: int = 0

	# 2. Add tracks and keyframes
	for t in tracks:
		if typeof(t) != TYPE_DICTIONARY:
			continue
		var t_dict = t as Dictionary
		var t_type_str = t_dict.get("track_type", "value")
		var t_type_int = _get_track_type_enum(t_type_str)
		var t_path = t_dict.get("node_path", "")
		var t_interp = _get_interpolation_enum(t_dict.get("interpolation", "linear"))
		var keyframes = t_dict.get("keyframes", [])

		if t_path == "":
			continue

		var track_idx = anim.add_track(t_type_int)
		anim.track_set_path(track_idx, NodePath(t_path))
		anim.track_set_interpolation_type(track_idx, t_interp)

		if t_type_int == Animation.TYPE_VALUE:
			var upd_mode = t_dict.get("update_mode", "continuous")
			if upd_mode == "discrete":
				anim.value_track_set_update_mode(track_idx, Animation.UPDATE_DISCRETE)
			elif upd_mode == "capture":
				anim.value_track_set_update_mode(track_idx, Animation.UPDATE_CAPTURE)
			else:
				anim.value_track_set_update_mode(track_idx, Animation.UPDATE_CONTINUOUS)

		for k in keyframes:
			if typeof(k) != TYPE_DICTIONARY:
				continue
			var k_dict = k as Dictionary
			var k_time = float(k_dict.get("time", 0.0))
			var k_trans = float(k_dict.get("transition", 1.0))
			var raw_val = k_dict.get("value", null)

			if t_type_int == Animation.TYPE_METHOD:
				var m_name: String = ""
				var m_args: Array = []
				if typeof(raw_val) == TYPE_DICTIONARY:
					m_name = (raw_val as Dictionary).get("method", "")
					m_args = (raw_val as Dictionary).get("args", [])
				elif typeof(raw_val) == TYPE_STRING:
					m_name = raw_val as String
				if m_name != "":
					anim.method_track_insert_key(track_idx, k_time, m_name, m_args)
					keyframe_count += 1
			elif t_type_int == Animation.TYPE_POSITION_3D:
				var coerced_v3 = _coerce_val(raw_val)
				if coerced_v3 is Vector3:
					anim.position_track_insert_key(track_idx, k_time, coerced_v3)
					keyframe_count += 1
			elif t_type_int == Animation.TYPE_SCALE_3D:
				var coerced_s3 = _coerce_val(raw_val)
				if coerced_s3 is Vector3:
					anim.scale_track_insert_key(track_idx, k_time, coerced_s3)
					keyframe_count += 1
			elif t_type_int == Animation.TYPE_ROTATION_3D:
				if typeof(raw_val) == TYPE_ARRAY and (raw_val as Array).size() == 4:
					var a = raw_val as Array
					var q = Quaternion(float(a[0]), float(a[1]), float(a[2]), float(a[3]))
					anim.rotation_track_insert_key(track_idx, k_time, q)
					keyframe_count += 1
			else:
				# Default value track
				var coerced_val = _coerce_val(raw_val)
				anim.track_insert_key(track_idx, k_time, coerced_val, k_trans)
				keyframe_count += 1

		track_count += 1

	# 3. Optionally attach to in-scene AnimationPlayer
	var attached_to_player: String = ""
	if anim_player_path != "" and _plugin:
		var editor_interface = _plugin.get_editor_interface()
		var edited_root = editor_interface.get_edited_scene_root()
		if edited_root:
			var target_node = edited_root.get_node_or_null(NodePath(anim_player_path))
			if target_node and target_node is AnimationPlayer:
				var anim_player = target_node as AnimationPlayer
				var library: AnimationLibrary = null
				if anim_player.has_animation_library(""):
					library = anim_player.get_animation_library("")
				else:
					library = AnimationLibrary.new()
					anim_player.add_animation_library("", library)

				var undo_redo = _plugin.get_undo_redo()
				if undo_redo:
					undo_redo.create_action("Add Animation '%s'" % animation_name)
					undo_redo.add_do_method(library, "add_animation", animation_name, anim)
					undo_redo.add_undo_method(library, "remove_animation", animation_name)
					undo_redo.commit_action()
				else:
					library.add_animation(animation_name, anim)
				attached_to_player = anim_player.name

	# 4. Optionally save to .tres resource file
	var saved_to_file: String = ""
	if save_path != "":
		var dir_path = save_path.get_base_dir()
		if dir_path != "" and dir_path != "res://":
			if not DirAccess.dir_exists_absolute(dir_path):
				DirAccess.make_dir_recursive_absolute(dir_path)

		var save_err = ResourceSaver.save(anim, save_path)
		if save_err != OK:
			return {
				"success": false,
				"message": "Failed to save animation to '%s' (Error code: %d)." % [save_path, save_err]
			}
		saved_to_file = save_path

	return {
		"success": true,
		"message": "Created animation '%s' (duration: %.2fs, tracks: %d, keyframes: %d)." % [
			animation_name, length, track_count, keyframe_count
		],
		"data": {
			"animation_name": animation_name,
			"length": length,
			"loop_mode": loop_mode,
			"step": step,
			"track_count": track_count,
			"keyframe_count": keyframe_count,
			"attached_to_animation_player": attached_to_player,
			"saved_to_file": saved_to_file
		}
	}
