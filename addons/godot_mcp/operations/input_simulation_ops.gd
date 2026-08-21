@tool
extends RefCounted

## Operations for Godot Interactive Runtime Input Simulation & Debug Drawing.

var _plugin: EditorPlugin
var _active_debug_shapes: Array[Dictionary] = []

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func simulate_input(params: Dictionary) -> Dictionary:
	var etype = str(params.get("event_type", "action")).to_lower()
	var pressed = bool(params.get("pressed", true))
	var strength = float(params.get("strength", 1.0))
	var event: InputEvent = null
	var details = ""

	if etype == "action":
		var act = str(params.get("action", ""))
		if act == "":
			return {"success": false, "message": "Action name is required for 'action' event type."}
		var iea = InputEventAction.new()
		iea.action = act
		iea.pressed = pressed
		iea.strength = strength
		event = iea
		details = "Action '%s' (Pressed: %s, Strength: %.2f)" % [act, str(pressed), strength]

	elif etype == "key":
		var key_str = str(params.get("key", ""))
		if key_str == "":
			return {"success": false, "message": "Key name is required for 'key' event type."}
		var iek = InputEventKey.new()
		var kc = OS.find_keycode_from_string(key_str)
		if kc == KEY_NONE and key_str.length() == 1:
			kc = key_str.unicode_at(0)
		iek.keycode = kc
		iek.pressed = pressed
		event = iek
		details = "Key '%s' (Keycode: %d, Pressed: %s)" % [key_str, int(kc), str(pressed)]

	elif etype == "mouse_button":
		var btn = int(params.get("button_index", 1))
		var iemb = InputEventMouseButton.new()
		iemb.button_index = btn
		iemb.pressed = pressed
		var pos_arr = params.get("position")
		if pos_arr != null and pos_arr is Array and pos_arr.size() >= 2:
			iemb.position = Vector2(float(pos_arr[0]), float(pos_arr[1]))
			iemb.global_position = iemb.position
		event = iemb
		details = "Mouse Button %d (Pressed: %s, Pos: %s)" % [btn, str(pressed), str(iemb.position)]

	elif etype == "mouse_motion":
		var iemm = InputEventMouseMotion.new()
		var pos_arr = params.get("position")
		if pos_arr != null and pos_arr is Array and pos_arr.size() >= 2:
			iemm.position = Vector2(float(pos_arr[0]), float(pos_arr[1]))
			iemm.global_position = iemm.position
		var rel_arr = params.get("relative")
		if rel_arr != null and rel_arr is Array and rel_arr.size() >= 2:
			iemm.relative = Vector2(float(rel_arr[0]), float(rel_arr[1]))
		event = iemm
		details = "Mouse Motion (Pos: %s, Relative: %s)" % [str(iemm.position), str(iemm.relative)]

	else:
		return {"success": false, "message": "Unsupported event type '%s'." % etype}

	if event:
		Input.parse_input_event(event)

	return {
		"success": true,
		"message": "Dispatched simulated input event: %s." % details,
		"data": {
			"event_type": etype,
			"details": details,
			"pressed": pressed
		}
	}

func draw_debug_shapes(params: Dictionary) -> Dictionary:
	var shapes = params.get("shapes", [])
	if not (shapes is Array) or shapes.size() == 0:
		return {"success": false, "message": "No debug shapes provided."}

	var count_3d = 0
	var count_2d = 0
	var now = Time.get_ticks_msec()

	for s in shapes:
		if s is Dictionary:
			var stype = str(s.get("shape_type", "line_3d")).to_lower()
			var dur = float(s.get("duration", 5.0))
			var shape_entry = {
				"type": stype,
				"data": s,
				"expiry": now + int(dur * 1000.0)
			}
			_active_debug_shapes.append(shape_entry)
			if "3d" in stype:
				count_3d += 1
			else:
				count_2d += 1

	return {
		"success": true,
		"message": "Added %d debug shapes (%d 3D, %d 2D) to active viewport overlays." % [shapes.size(), count_3d, count_2d],
		"data": {
			"total_shapes_added": shapes.size(),
			"shapes_3d_count": count_3d,
			"shapes_2d_count": count_2d,
			"total_active_shapes": _active_debug_shapes.size()
		}
	}

func clear_debug_shapes(params: Dictionary) -> Dictionary:
	var cat = params.get("category")
	var prev_count = _active_debug_shapes.size()

	if cat != null and str(cat).strip_edges() != "":
		var cat_str = str(cat).to_lower()
		var filtered: Array[Dictionary] = []
		for s in _active_debug_shapes:
			if not (cat_str in str(s.get("type", ""))):
				filtered.append(s)
		_active_debug_shapes = filtered
	else:
		_active_debug_shapes.clear()

	var removed = prev_count - _active_debug_shapes.size()

	return {
		"success": true,
		"message": "Cleared %d debug shapes from overlays." % removed,
		"data": {
			"shapes_cleared": removed,
			"remaining_active": _active_debug_shapes.size()
		}
	}
