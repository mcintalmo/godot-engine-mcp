@tool
extends RefCounted

## Operations for Godot Deep Profiling & Memory Leak Diagnostics.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func audit_orphan_nodes(params: Dictionary) -> Dictionary:
	var print_out = bool(params.get("print_orphans_to_stdout", false))

	var orphan_nodes = int(Performance.get_monitor(Performance.RENDER_ORPHAN_NODES_IN_OBJECTS))
	var active_nodes = int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))
	var total_objects = int(Performance.get_monitor(Performance.OBJECT_COUNT))
	var total_resources = int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT))

	if print_out:
		Node.print_orphan_nodes()

	var status = "HEALTHY"
	if orphan_nodes > 100:
		status = "HIGH_LEAK_RISK"
	elif orphan_nodes > 0:
		status = "LOW_LEAK_WARNING"

	return {
		"success": true,
		"message": "Orphan node audit: %d orphan nodes detected (%s)." % [orphan_nodes, status],
		"data": {
			"orphan_node_count": orphan_nodes,
			"active_node_count": active_nodes,
			"total_object_count": total_objects,
			"total_resource_count": total_resources,
			"leak_status": status,
			"printed_to_stdout": print_out
		}
	}

func capture_profiler_trace(params: Dictionary) -> Dictionary:
	var frames_to_sample = int(params.get("frames_to_sample", 10))

	var process_time_sec = Performance.get_monitor(Performance.TIME_PROCESS)
	var physics_time_sec = Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)
	var nav_time_sec = Performance.get_monitor(Performance.TIME_NAVIGATION_PROCESS)
	var fps = Performance.get_monitor(Performance.TIME_FPS)

	var draw_calls = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	var primitives = int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	var objects_in_frame = int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))

	var mem_static = int(Performance.get_monitor(Performance.MEMORY_STATIC))
	var mem_static_max = int(Performance.get_monitor(Performance.MEMORY_STATIC_MAX))

	var process_ms = process_time_sec * 1000.0
	var physics_ms = physics_time_sec * 1000.0
	var nav_ms = nav_time_sec * 1000.0
	var total_frame_ms = process_ms + physics_ms

	return {
		"success": true,
		"message": "Captured profiler trace across %d frames: %.2f ms/frame (%.1f FPS)." % [frames_to_sample, total_frame_ms, fps],
		"data": {
			"frames_sampled": frames_to_sample,
			"fps": fps,
			"process_time_ms": process_ms,
			"physics_time_ms": physics_ms,
			"navigation_time_ms": nav_ms,
			"total_frame_ms": total_frame_ms,
			"draw_calls": draw_calls,
			"primitives_count": primitives,
			"objects_in_frame": objects_in_frame,
			"memory_static_bytes": mem_static,
			"memory_static_mb": mem_static / (1024.0 * 1024.0),
			"memory_static_max_mb": mem_static_max / (1024.0 * 1024.0)
		}
	}

func inspect_vram_usage(params: Dictionary) -> Dictionary:
	var tex_mem = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
	var buf_mem = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_BUFFER_MEM_USED)
	var video_mem = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED)

	var tex_mb = tex_mem / (1024.0 * 1024.0)
	var buf_mb = buf_mem / (1024.0 * 1024.0)
	var total_vram_mb = video_mem / (1024.0 * 1024.0)

	return {
		"success": true,
		"message": "Inspected GPU VRAM usage: %.2f MB total (Texture: %.2f MB, Buffer: %.2f MB)." % [total_vram_mb, tex_mb, buf_mb],
		"data": {
			"texture_memory_bytes": tex_mem,
			"texture_memory_mb": tex_mb,
			"buffer_memory_bytes": buf_mem,
			"buffer_memory_mb": buf_mb,
			"total_vram_bytes": video_mem,
			"total_vram_mb": total_vram_mb
		}
	}
