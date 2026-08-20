@tool
extends RefCounted

## Operations for managing Godot 4 AudioServer buses, volume levels, routing, and effects.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_audio_layout(params: Dictionary) -> Dictionary:
	var include_effects: bool = params.get("include_effects", true)
	var buses: Array[Dictionary] = []

	for i in range(AudioServer.bus_count):
		var b_name = AudioServer.get_bus_name(i)
		var vol_db = AudioServer.get_bus_volume_db(i)
		var vol_linear = db_to_linear(vol_db)
		var send_target = AudioServer.get_bus_send(i)
		var is_muted = AudioServer.is_bus_mute(i)
		var is_solo = AudioServer.is_bus_solo(i)
		var is_bypass = AudioServer.is_bus_bypassing_effects(i)

		var bus_info: Dictionary = {
			"index": i,
			"name": b_name,
			"volume_db": round(vol_db * 100.0) / 100.0,
			"volume_linear": round(vol_linear * 100.0) / 100.0,
			"send_to": send_target,
			"mute": is_muted,
			"solo": is_solo,
			"bypass_effects": is_bypass,
			"effect_count": AudioServer.get_bus_effect_count(i)
		}

		if include_effects:
			var effect_list: Array[Dictionary] = []
			for e in range(AudioServer.get_bus_effect_count(i)):
				var eff = AudioServer.get_bus_effect(i, e)
				if eff:
					effect_list.append({
						"index": e,
						"type": eff.get_class(),
						"resource_name": eff.resource_name if eff.resource_name != "" else eff.get_class(),
						"enabled": AudioServer.is_bus_effect_enabled(i, e)
					})
			bus_info["effects"] = effect_list

		buses.append(bus_info)

	return {
		"success": true,
		"message": "Found %d audio buses in layout." % buses.size(),
		"data": {
			"bus_count": buses.size(),
			"buses": buses
		}
	}

func configure_audio_bus(params: Dictionary) -> Dictionary:
	var bus_name: String = params.get("bus_name", "")
	if bus_name == "":
		return {"success": false, "message": "bus_name parameter cannot be empty."}

	var create_if_missing: bool = params.get("create_if_missing", true)
	var idx = AudioServer.get_bus_index(bus_name)
	var was_created = false

	if idx == -1:
		if not create_if_missing:
			return {"success": false, "message": "Audio bus '%s' not found and create_if_missing is false." % bus_name}
		idx = AudioServer.bus_count
		AudioServer.add_bus(idx)
		AudioServer.set_bus_name(idx, bus_name)
		was_created = true

	if params.has("volume_db") and params["volume_db"] != null:
		AudioServer.set_bus_volume_db(idx, float(params["volume_db"]))
	elif params.has("volume_linear") and params["volume_linear"] != null:
		var lin = maxf(float(params["volume_linear"]), 0.0001)
		AudioServer.set_bus_volume_db(idx, linear_to_db(lin))

	if params.has("send_to_bus") and params["send_to_bus"] != null and str(params["send_to_bus"]) != "":
		var send_name = str(params["send_to_bus"])
		if AudioServer.get_bus_index(send_name) != -1 or send_name == "Master":
			AudioServer.set_bus_send(idx, send_name)

	if params.has("mute") and params["mute"] != null:
		AudioServer.set_bus_mute(idx, bool(params["mute"]))

	if params.has("solo") and params["solo"] != null:
		AudioServer.set_bus_solo(idx, bool(params["solo"]))

	if params.has("bypass_effects") and params["bypass_effects"] != null:
		AudioServer.set_bus_bypass_effects(idx, bool(params["bypass_effects"]))

	var save_path: String = params.get("save_layout_path", "")
	var saved_file = null
	if save_path != "":
		var dir_path = save_path.get_base_dir()
		if dir_path != "" and dir_path != "res://":
			if not DirAccess.dir_exists_absolute(dir_path):
				DirAccess.make_dir_recursive_absolute(dir_path)
		var layout = AudioServer.generate_bus_layout()
		var err = ResourceSaver.save(layout, save_path)
		if err == OK:
			saved_file = save_path

	var action_word = "Created" if was_created else "Configured"
	return {
		"success": true,
		"message": "%s audio bus '%s' (Index: %d, Volume: %.1f dB, Send: '%s')." % [
			action_word,
			bus_name,
			idx,
			AudioServer.get_bus_volume_db(idx),
			AudioServer.get_bus_send(idx)
		],
		"data": {
			"bus_name": bus_name,
			"index": idx,
			"was_created": was_created,
			"volume_db": round(AudioServer.get_bus_volume_db(idx) * 100.0) / 100.0,
			"volume_linear": round(db_to_linear(AudioServer.get_bus_volume_db(idx)) * 100.0) / 100.0,
			"send_to": AudioServer.get_bus_send(idx),
			"mute": AudioServer.is_bus_mute(idx),
			"solo": AudioServer.is_bus_solo(idx),
			"bypass_effects": AudioServer.is_bus_bypassing_effects(idx),
			"saved_layout_path": saved_file
		}
	}

func set_bus_effect(params: Dictionary) -> Dictionary:
	var bus_name: String = params.get("bus_name", "")
	if bus_name == "":
		return {"success": false, "message": "bus_name parameter cannot be empty."}

	var idx = AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return {"success": false, "message": "Audio bus '%s' not found." % bus_name}

	var effect_type: String = params.get("effect_type", "")
	if effect_type == "":
		return {"success": false, "message": "effect_type parameter cannot be empty."}

	if not ClassDB.class_exists(effect_type) or not ClassDB.is_parent_class(effect_type, "AudioEffect"):
		return {"success": false, "message": "Class '%s' is not a valid AudioEffect." % effect_type}

	var effect: AudioEffect = ClassDB.instantiate(effect_type) as AudioEffect
	if not effect:
		return {"success": false, "message": "Failed to instantiate AudioEffect of type '%s'." % effect_type}

	var properties: Dictionary = params.get("properties", {})
	for prop in properties.keys():
		effect.set(str(prop), properties[prop])

	var enabled: bool = params.get("enabled", true)
	var effect_index = params.get("effect_index")

	var actual_index = -1
	if effect_index != null and int(effect_index) >= 0 and int(effect_index) < AudioServer.get_bus_effect_count(idx):
		actual_index = int(effect_index)
		AudioServer.remove_bus_effect(idx, actual_index)
		AudioServer.add_bus_effect(idx, effect, actual_index)
	else:
		actual_index = AudioServer.get_bus_effect_count(idx)
		AudioServer.add_bus_effect(idx, effect)

	AudioServer.set_bus_effect_enabled(idx, actual_index, enabled)

	var save_path: String = params.get("save_layout_path", "")
	var saved_file = null
	if save_path != "":
		var dir_path = save_path.get_base_dir()
		if dir_path != "" and dir_path != "res://":
			if not DirAccess.dir_exists_absolute(dir_path):
				DirAccess.make_dir_recursive_absolute(dir_path)
		var layout = AudioServer.generate_bus_layout()
		var err = ResourceSaver.save(layout, save_path)
		if err == OK:
			saved_file = save_path

	return {
		"success": true,
		"message": "Configured effect '%s' at slot %d on bus '%s'." % [effect_type, actual_index, bus_name],
		"data": {
			"bus_name": bus_name,
			"bus_index": idx,
			"effect_type": effect_type,
			"effect_index": actual_index,
			"enabled": enabled,
			"properties_set": properties,
			"saved_layout_path": saved_file
		}
	}
