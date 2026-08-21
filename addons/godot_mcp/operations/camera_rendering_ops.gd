@tool
extends RefCounted

## Operations for Godot Camera Presets, High-Res Viewport Capture & Rendering Pipeline.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _get_scene_root() -> Node:
	if _plugin:
		var ei = _plugin.get_editor_interface()
		if ei:
			return ei.get_edited_scene_root()
	return null

func _find_node(path_str: String, root: Node) -> Node:
	if not root:
		return null
	if path_str == "." or path_str == "" or path_str == root.name or path_str == "/root":
		return root
	if root.has_node(path_str):
		return root.get_node(path_str)
	return null

func configure_camera(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("camera_node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Camera node not found at '%s'." % node_path}

	var changes = []

	if node is Camera3D:
		var proj = params.get("projection")
		if proj != null:
			var p_str = str(proj).to_lower()
			if p_str == "orthogonal" or p_str == "ortho":
				node.projection = Camera3D.PROJECTION_ORTHOGONAL
			elif p_str == "frustum":
				node.projection = Camera3D.PROJECTION_FRUSTUM
			else:
				node.projection = Camera3D.PROJECTION_PERSPECTIVE
			changes.append("Projection: %s" % p_str)

		if params.has("fov") and params["fov"] != null:
			node.fov = float(params["fov"])
			changes.append("FOV: %.1f deg" % node.fov)

		if params.has("size") and params["size"] != null:
			node.size = float(params["size"])
			changes.append("Size: %.2f" % node.size)

		if params.has("near") and params["near"] != null:
			node.near = float(params["near"])
			changes.append("Near: %.2f" % node.near)

		if params.has("far") and params["far"] != null:
			node.far = float(params["far"])
			changes.append("Far: %.1f" % node.far)

		if params.has("current") and params["current"] != null:
			node.current = bool(params["current"])
			changes.append("Current: %s" % str(node.current))

	elif node is Camera2D:
		var zoom_arr = params.get("zoom")
		if zoom_arr != null and zoom_arr is Array and zoom_arr.size() >= 2:
			node.zoom = Vector2(float(zoom_arr[0]), float(zoom_arr[1]))
			changes.append("Zoom: (%0.2f, %0.2f)" % [node.zoom.x, node.zoom.y])

		if params.has("position_smoothing_enabled") and params["position_smoothing_enabled"] != null:
			node.position_smoothing_enabled = bool(params["position_smoothing_enabled"])
			changes.append("Smoothing: %s" % str(node.position_smoothing_enabled))

		if params.has("position_smoothing_speed") and params["position_smoothing_speed"] != null:
			node.position_smoothing_speed = float(params["position_smoothing_speed"])
			changes.append("Smoothing Speed: %.1f" % node.position_smoothing_speed)

		var limits = params.get("limits")
		if limits != null and limits is Dictionary:
			if limits.has("left"):
				node.limit_left = int(limits["left"])
			if limits.has("top"):
				node.limit_top = int(limits["top"])
			if limits.has("right"):
				node.limit_right = int(limits["right"])
			if limits.has("bottom"):
				node.limit_bottom = int(limits["bottom"])
			changes.append("Limits: %s" % str(limits))

	else:
		return {"success": false, "message": "Node '%s' is of class '%s', expected Camera2D or Camera3D." % [node.name, node.get_class()]}

	return {
		"success": true,
		"message": "Configured camera '%s': %s." % [node.name, ", ".join(changes) if changes.size() > 0 else "No changes"],
		"data": {
			"camera_name": node.name,
			"camera_path": str(node.get_path()),
			"class": node.get_class(),
			"changes_applied": changes
		}
	}

func configure_render_settings(params: Dictionary) -> Dictionary:
	var changes = []

	if params.has("msaa_2d") and params["msaa_2d"] != null:
		var v_str = str(params["msaa_2d"]).to_lower()
		var val = 0
		if v_str == "2x": val = 1
		elif v_str == "4x": val = 2
		elif v_str == "8x": val = 3
		ProjectSettings.set_setting("rendering/anti_aliasing/quality/msaa_2d", val)
		changes.append("MSAA 2D: %s" % v_str)

	if params.has("msaa_3d") and params["msaa_3d"] != null:
		var v_str = str(params["msaa_3d"]).to_lower()
		var val = 0
		if v_str == "2x": val = 1
		elif v_str == "4x": val = 2
		elif v_str == "8x": val = 3
		ProjectSettings.set_setting("rendering/anti_aliasing/quality/msaa_3d", val)
		changes.append("MSAA 3D: %s" % v_str)

	if params.has("screen_space_aa") and params["screen_space_aa"] != null:
		var v_str = str(params["screen_space_aa"]).to_lower()
		var val = 1 if v_str == "fxaa" else 0
		ProjectSettings.set_setting("rendering/anti_aliasing/quality/screen_space_aa", val)
		changes.append("Screen-Space AA: %s" % v_str)

	if params.has("use_taa") and params["use_taa"] != null:
		var val = bool(params["use_taa"])
		ProjectSettings.set_setting("rendering/anti_aliasing/quality/use_taa", val)
		changes.append("TAA: %s" % str(val))

	if params.has("scaling_3d_mode") and params["scaling_3d_mode"] != null:
		var v_str = str(params["scaling_3d_mode"]).to_lower()
		var val = 0
		if v_str == "fsr": val = 1
		elif v_str == "fsr2": val = 2
		ProjectSettings.set_setting("rendering/scaling_3d/mode", val)
		changes.append("Scaling 3D Mode: %s" % v_str)

	if params.has("scaling_3d_scale") and params["scaling_3d_scale"] != null:
		var val = clampf(float(params["scaling_3d_scale"]), 0.25, 2.0)
		ProjectSettings.set_setting("rendering/scaling_3d/scale", val)
		changes.append("Scaling 3D Scale: %.2f" % val)

	if params.has("directional_shadow_size") and params["directional_shadow_size"] != null:
		var val = int(params["directional_shadow_size"])
		ProjectSettings.set_setting("rendering/lights_and_shadows/directional_shadow/size", val)
		changes.append("Directional Shadow Size: %d" % val)

	if params.has("positional_shadow_atlas_size") and params["positional_shadow_atlas_size"] != null:
		var val = int(params["positional_shadow_atlas_size"])
		ProjectSettings.set_setting("rendering/lights_and_shadows/positional_shadow/atlas_size", val)
		changes.append("Positional Shadow Atlas Size: %d" % val)

	if params.has("vsync_mode") and params["vsync_mode"] != null:
		var v_str = str(params["vsync_mode"]).to_lower()
		var val = 1
		if v_str == "disabled": val = 0
		elif v_str == "adaptive": val = 2
		elif v_str == "mailbox": val = 3
		ProjectSettings.set_setting("display/window/vsync/vsync_mode", val)
		changes.append("VSync Mode: %s" % v_str)

	ProjectSettings.save()

	return {
		"success": true,
		"message": "Configured render settings: %s." % [", ".join(changes) if changes.size() > 0 else "No modifications"],
		"data": {
			"changes_applied": changes
		}
	}

func capture_viewport(params: Dictionary) -> Dictionary:
	var output_path = params.get("output_path")
	var max_w = int(params.get("max_width", 1280))
	var max_h = int(params.get("max_height", 720))
	var fmt = str(params.get("format", "png")).to_lower()
	var inc_b64 = bool(params.get("include_base64", false))

	var vp: Viewport = null
	if _plugin:
		var ei = _plugin.get_editor_interface()
		if ei:
			vp = ei.get_editor_main_screen()

	if not vp:
		vp = Engine.get_main_loop().get_root() if Engine.get_main_loop() is SceneTree else null

	if not vp:
		return {"success": false, "message": "Failed to access editor viewport for capture."}

	var tex = vp.get_texture()
	if not tex:
		return {"success": false, "message": "No active viewport texture available."}

	var img: Image = tex.get_image()
	if not img:
		return {"success": false, "message": "Failed to extract Image buffer from viewport texture."}

	var orig_w = img.get_width()
	var orig_h = img.get_height()

	if (orig_w > max_w or orig_h > max_h) and max_w > 0 and max_h > 0:
		var aspect = float(orig_w) / float(orig_h)
		var target_w = max_w
		var target_h = int(float(target_w) / aspect)
		if target_h > max_h:
			target_h = max_h
			target_w = int(float(target_h) * aspect)
		img.resize(target_w, target_h, Image.INTERPOLATE_LANCZOS)

	var saved_file = ""
	if output_path != null and str(output_path).strip_edges() != "":
		var sp = str(output_path).strip_edges()
		if fmt == "webp":
			img.save_webp(sp)
		elif fmt == "jpg" or fmt == "jpeg":
			img.save_jpg(sp)
		else:
			img.save_png(sp)
		saved_file = sp

	var b64_str = ""
	if inc_b64:
		var buf = PackedByteArray()
		if fmt == "webp":
			buf = img.save_webp_to_buffer()
		elif fmt == "jpg" or fmt == "jpeg":
			buf = img.save_jpg_to_buffer()
		else:
			buf = img.save_png_to_buffer()
		b64_str = Marshalls.raw_to_base64(buf)

	return {
		"success": true,
		"message": "Captured viewport image (%dx%d, format: %s)." % [img.get_width(), img.get_height(), fmt],
		"data": {
			"original_dimensions": [orig_w, orig_h],
			"captured_dimensions": [img.get_width(), img.get_height()],
			"format": fmt,
			"saved_file": saved_file,
			"has_base64": inc_b64,
			"base64_data": b64_str
		}
	}
