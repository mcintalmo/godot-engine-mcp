@tool
extends RefCounted

## Operations for querying real-time Godot engine performance metrics and telemetry.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_metrics(params: Dictionary) -> Dictionary:
	var category: String = params.get("category", "all").to_lower()
	var include_custom: bool = bool(params.get("include_custom_monitors", true))

	var data: Dictionary = {}

	if category == "all" or category == "time":
		data["time"] = {
			"fps": round(Performance.get_monitor(Performance.TIME_FPS)),
			"process_time_ms": round(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0 * 100.0) / 100.0,
			"physics_process_time_ms": round(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0 * 100.0) / 100.0,
			"navigation_process_time_ms": round(Performance.get_monitor(Performance.TIME_NAVIGATION_PROCESS) * 1000.0 * 100.0) / 100.0
		}

	if category == "all" or category == "render":
		var vram_bytes = Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
		var tex_bytes = Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)
		var buf_bytes = Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)
		data["render"] = {
			"draw_calls_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
			"objects_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
			"primitives_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
			"video_mem_mb": round(vram_bytes / (1024.0 * 1024.0) * 100.0) / 100.0,
			"texture_mem_mb": round(tex_bytes / (1024.0 * 1024.0) * 100.0) / 100.0,
			"buffer_mem_mb": round(buf_bytes / (1024.0 * 1024.0) * 100.0) / 100.0
		}

	if category == "all" or category == "memory":
		var static_bytes = Performance.get_monitor(Performance.MEMORY_STATIC)
		var max_static_bytes = Performance.get_monitor(Performance.MEMORY_STATIC_MAX)
		var msg_bytes = Performance.get_monitor(Performance.MEMORY_MESSAGE_BUFFER_MAX)
		data["memory"] = {
			"static_ram_mb": round(static_bytes / (1024.0 * 1024.0) * 100.0) / 100.0,
			"static_ram_peak_mb": round(max_static_bytes / (1024.0 * 1024.0) * 100.0) / 100.0,
			"message_buffer_kb": round(msg_bytes / 1024.0 * 100.0) / 100.0
		}

	if category == "all" or category == "objects":
		var orphans = int(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT))
		data["objects"] = {
			"node_count": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
			"resource_count": int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),
			"object_count": int(Performance.get_monitor(Performance.OBJECT_COUNT)),
			"orphan_node_count": orphans
		}

	if include_custom:
		var custom_monitors: Dictionary = {}
		if Performance.has_method("get_custom_monitor_names"):
			var names = Performance.get_custom_monitor_names()
			for n in names:
				custom_monitors[str(n)] = Performance.get_custom_monitor(n)
		if custom_monitors.size() > 0:
			data["custom"] = custom_monitors

	data["category"] = category

	var fps_val = round(Performance.get_monitor(Performance.TIME_FPS))
	var orphan_val = int(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT))

	var msg = "Engine Telemetry: %d FPS, %d Draw Calls" % [
		fps_val,
		int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	]
	if orphan_val > 0:
		msg += " (Warning: %d orphan nodes detected)" % orphan_val

	return {
		"success": true,
		"message": msg,
		"data": data
	}

func get_performance_metrics(params: Dictionary = {}) -> Dictionary:
	return get_metrics(params)

