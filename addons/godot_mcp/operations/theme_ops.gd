@tool
extends RefCounted

## Operations for authoring Godot 4 Theme resources and applying Control node style overrides.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _build_stylebox(cfg: Dictionary) -> StyleBoxFlat:
	var sb = StyleBoxFlat.new()

	if cfg.has("bg_color") and cfg["bg_color"] != null:
		sb.bg_color = Color.from_string(str(cfg["bg_color"]), Color.BLACK)

	if cfg.has("border_color") and cfg["border_color"] != null:
		sb.border_color = Color.from_string(str(cfg["border_color"]), Color.WHITE)

	if cfg.has("border_width") and cfg["border_width"] != null:
		var w = int(cfg["border_width"])
		sb.border_width_left = w
		sb.border_width_top = w
		sb.border_width_right = w
		sb.border_width_bottom = w
	elif cfg.has("border_widths") and cfg["border_widths"] is Array and cfg["border_widths"].size() >= 4:
		var bw = cfg["border_widths"]
		sb.border_width_left = int(bw[0])
		sb.border_width_top = int(bw[1])
		sb.border_width_right = int(bw[2])
		sb.border_width_bottom = int(bw[3])

	if cfg.has("corner_radius") and cfg["corner_radius"] != null:
		var r = int(cfg["corner_radius"])
		sb.corner_radius_top_left = r
		sb.corner_radius_top_right = r
		sb.corner_radius_bottom_right = r
		sb.corner_radius_bottom_left = r
	elif cfg.has("corner_radii") and cfg["corner_radii"] is Array and cfg["corner_radii"].size() >= 4:
		var cr = cfg["corner_radii"]
		sb.corner_radius_top_left = int(cr[0])
		sb.corner_radius_top_right = int(cr[1])
		sb.corner_radius_bottom_right = int(cr[2])
		sb.corner_radius_bottom_left = int(cr[3])

	if cfg.has("content_margins") and cfg["content_margins"] is Array and cfg["content_margins"].size() >= 4:
		var cm = cfg["content_margins"]
		sb.content_margin_left = float(cm[0])
		sb.content_margin_top = float(cm[1])
		sb.content_margin_right = float(cm[2])
		sb.content_margin_bottom = float(cm[3])

	if cfg.has("shadow_color") and cfg["shadow_color"] != null:
		sb.shadow_color = Color.from_string(str(cfg["shadow_color"]), Color(0, 0, 0, 0.4))
	if cfg.has("shadow_size") and cfg["shadow_size"] != null:
		sb.shadow_size = int(cfg["shadow_size"])
	if cfg.has("shadow_offset") and cfg["shadow_offset"] is Array and cfg["shadow_offset"].size() >= 2:
		sb.shadow_offset = Vector2(float(cfg["shadow_offset"][0]), float(cfg["shadow_offset"][1]))

	if cfg.has("anti_aliasing"):
		sb.anti_aliasing = bool(cfg["anti_aliasing"])

	return sb

func create_theme(params: Dictionary) -> Dictionary:
	var save_path: String = params.get("save_path", "")
	if save_path == "":
		return {"success": false, "message": "save_path parameter cannot be empty."}

	var theme = Theme.new()

	var base_font_path: String = params.get("base_font_path", "")
	if base_font_path != "" and ResourceLoader.exists(base_font_path):
		var font_res = load(base_font_path)
		if font_res is Font:
			theme.default_font = font_res

	if params.has("base_font_size") and params["base_font_size"] != null:
		theme.default_font_size = int(params["base_font_size"])

	var colors: Dictionary = params.get("colors", {})
	for node_type in colors.keys():
		var type_colors: Dictionary = colors[node_type]
		for item_name in type_colors.keys():
			var col_str = str(type_colors[item_name])
			theme.set_color(str(item_name), str(node_type), Color.from_string(col_str, Color.WHITE))

	var constants: Dictionary = params.get("constants", {})
	for node_type in constants.keys():
		var type_consts: Dictionary = constants[node_type]
		for item_name in type_consts.keys():
			theme.set_constant(str(item_name), str(node_type), int(type_consts[item_name]))

	var styleboxes: Dictionary = params.get("styleboxes", {})
	for node_type in styleboxes.keys():
		var type_boxes: Dictionary = styleboxes[node_type]
		for item_name in type_boxes.keys():
			var sb_cfg: Dictionary = type_boxes[item_name]
			var sb = _build_stylebox(sb_cfg)
			theme.set_stylebox(str(item_name), str(node_type), sb)

	# Ensure target directory exists
	var dir_path = save_path.get_base_dir()
	if dir_path != "" and dir_path != "res://":
		if not DirAccess.dir_exists_absolute(dir_path):
			DirAccess.make_dir_recursive_absolute(dir_path)

	var err = ResourceSaver.save(theme, save_path)
	if err != OK:
		return {
			"success": false,
			"message": "Failed to save Theme resource to '%s', error: %d" % [save_path, err]
		}

	var applied_to: String = ""
	var apply_node_path: String = params.get("apply_to_node_path", "")
	if apply_node_path != "" and _plugin:
		var editor_interface = _plugin.get_editor_interface()
		var edited_root = editor_interface.get_edited_scene_root()
		if edited_root:
			var target = edited_root.get_node_or_null(NodePath(apply_node_path))
			if not target and (apply_node_path == "." or apply_node_path == ""):
				target = edited_root
			if target is Control:
				var undo_redo = _plugin.get_undo_redo()
				if undo_redo:
					undo_redo.create_action("Apply Theme to '%s'" % target.name)
					undo_redo.add_do_property(target, "theme", theme)
					undo_redo.add_undo_property(target, "theme", target.theme)
					undo_redo.commit_action()
				else:
					target.theme = theme
				applied_to = target.name

	return {
		"success": true,
		"message": "Created and saved Theme resource to '%s'." % save_path,
		"data": {
			"save_path": save_path,
			"base_font_size": theme.default_font_size if theme.default_font_size > 0 else null,
			"colors_configured": colors,
			"constants_configured": constants,
			"styleboxes_configured": styleboxes.keys(),
			"applied_to_node": applied_to if applied_to != "" else null

		}
	}

func apply_theme_override(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	var override_type: String = params.get("override_type", "stylebox").to_lower()
	var item_name: String = params.get("item_name", "")
	var value = params.get("value")

	if node_path == "" or item_name == "":
		return {"success": false, "message": "node_path and item_name cannot be empty."}

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var target = edited_root.get_node_or_null(NodePath(node_path))
	if not target and (node_path == "." or node_path == ""):
		target = edited_root

	if not target:
		return {"success": false, "message": "Node '%s' not found." % node_path}

	if not (target is Control):
		return {"success": false, "message": "Target node '%s' is a %s (must be Control to apply theme overrides)." % [target.name, target.get_class()]}

	var control_node = target as Control
	var applied_desc: String = ""

	match override_type:
		"stylebox":
			var sb: StyleBoxFlat
			if value is Dictionary:
				sb = _build_stylebox(value)
			else:
				sb = StyleBoxFlat.new()
			control_node.add_theme_stylebox_override(item_name, sb)
			applied_desc = "StyleBoxFlat override"
		"color":
			var col = Color.from_string(str(value), Color.WHITE)
			control_node.add_theme_color_override(item_name, col)
			applied_desc = "Color override '%s'" % str(col)
		"constant":
			var val_int = int(value)
			control_node.add_theme_constant_override(item_name, val_int)
			applied_desc = "Constant override %d" % val_int
		"font_size":
			var size_int = int(value)
			control_node.add_theme_font_size_override(item_name, size_int)
			applied_desc = "Font size override %d px" % size_int
		"font":
			if ResourceLoader.exists(str(value)):
				var f = load(str(value))
				control_node.add_theme_font_override(item_name, f)
				applied_desc = "Font override '%s'" % str(value)
		_:
			return {"success": false, "message": "Unsupported override_type: '%s'." % override_type}

	return {
		"success": true,
		"message": "Applied %s '%s' on Control '%s'." % [applied_desc, item_name, control_node.name],
		"data": {
			"node_name": control_node.name,
			"override_type": override_type,
			"item_name": item_name,
			"value": value
		}
	}
