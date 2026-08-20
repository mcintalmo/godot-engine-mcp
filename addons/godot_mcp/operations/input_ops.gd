@tool
extends RefCounted

## Operations for Godot InputMap querying, action creation, event binding, and project.godot persistence.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_input_actions(params: Dictionary) -> Dictionary:
	var prefix: String = params.get("filter_prefix", "")
	var actions: Array = []

	var all_actions = InputMap.get_actions()
	for a_name_val in all_actions:
		var a_name = str(a_name_val)
		if prefix != "" and not a_name.begins_with(prefix):
			continue

		var deadzone = InputMap.action_get_deadzone(a_name)
		var event_list: Array = []
		var events = InputMap.action_get_events(a_name)

		for ev in events:
			if ev is InputEventKey:
				event_list.append({
					"type": "key",
					"keycode": OS.get_keycode_string(ev.keycode) if ev.keycode != 0 else OS.get_keycode_string(ev.physical_keycode),
					"physical_keycode": OS.get_keycode_string(ev.physical_keycode),
					"unicode": char(ev.unicode) if ev.unicode != 0 else ""
				})
			elif ev is InputEventMouseButton:
				event_list.append({
					"type": "mouse_button",
					"button_index": ev.button_index
				})
			elif ev is InputEventJoypadButton:
				event_list.append({
					"type": "joypad_button",
					"button_index": ev.button_index
				})
			elif ev is InputEventJoypadMotion:
				event_list.append({
					"type": "joypad_motion",
					"axis": ev.axis,
					"axis_value": ev.axis_value
				})

		actions.append({
			"name": a_name,
			"deadzone": deadzone,
			"event_count": event_list.size(),
			"events": event_list
		})

	return {
		"success": true,
		"message": "Found %d input actions." % actions.size(),
		"data": {"action_count": actions.size(), "actions": actions}
	}

func configure_input_action(params: Dictionary) -> Dictionary:
	var action_name: String = params.get("action_name", "")
	if action_name == "":
		return {"success": false, "message": "action_name cannot be empty."}

	var deadzone: float = float(params.get("deadzone", 0.5))
	var replace_existing: bool = bool(params.get("replace_existing", true))
	var save_settings: bool = bool(params.get("save_to_project_settings", true))
	var event_configs: Array = params.get("events", [])

	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name, deadzone)
	else:
		if replace_existing:
			InputMap.action_erase_events(action_name)
		InputMap.action_set_deadzone(action_name, deadzone)

	var added_events: Array = []
	for cfg in event_configs:
		var ev_type = str(cfg.get("type", "key")).to_lower()
		var new_event: InputEvent = null

		match ev_type:
			"key":
				var key_ev = InputEventKey.new()
				var key_str = str(cfg.get("keycode", cfg.get("physical_keycode", "Space"))).removeprefix("Key.").to_upper()
				var kc = OS.find_keycode_from_string(key_str)
				key_ev.physical_keycode = kc if kc != KEY_NONE else KEY_SPACE
				new_event = key_ev
				added_events.append("Key:%s" % key_str)
			"mouse_button":
				var mb_ev = InputEventMouseButton.new()
				mb_ev.button_index = int(cfg.get("button_index", MOUSE_BUTTON_LEFT))
				new_event = mb_ev
				added_events.append("MouseButton:%d" % mb_ev.button_index)
			"joypad_button":
				var jb_ev = InputEventJoypadButton.new()
				jb_ev.button_index = int(cfg.get("button_index", JOY_BUTTON_A))
				new_event = jb_ev
				added_events.append("JoyButton:%d" % jb_ev.button_index)
			"joypad_motion":
				var jm_ev = InputEventJoypadMotion.new()
				jm_ev.axis = int(cfg.get("axis", JOY_AXIS_LEFT_X))
				jm_ev.axis_value = float(cfg.get("axis_value", 1.0))
				new_event = jm_ev
				added_events.append("JoyMotion:Axis%d(%.1f)" % [jm_ev.axis, jm_ev.axis_value])

		if new_event:
			InputMap.action_add_event(action_name, new_event)

	if save_settings:
		var setting_events: Array = []
		for ev in InputMap.action_get_events(action_name):
			setting_events.append(ev)
		ProjectSettings.set_setting("input/" + action_name, {
			"deadzone": deadzone,
			"events": setting_events
		})
		ProjectSettings.save()

	return {
		"success": true,
		"message": "Configured input action '%s' with %d events (Deadzone: %.2f)." % [action_name, added_events.size(), deadzone],
		"data": {
			"action_name": action_name,
			"deadzone": deadzone,
			"events_added": added_events,
			"saved_to_project_settings": save_settings
		}
	}
