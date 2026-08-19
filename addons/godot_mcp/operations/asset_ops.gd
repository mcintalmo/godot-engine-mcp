@tool
extends RefCounted

## Operations for asset reimporting, import preset configuration, and collision polygon authoring.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _get_preset_params(preset: String) -> Dictionary:
	match preset.to_lower():
		"pixel_art_2d":
			return {
				"compress/mode": 0,
				"mipmaps/generate": false,
				"roughness/mode": 0,
				"process/fix_alpha_border": true
			}
		"high_quality_3d":
			return {
				"compress/mode": 2,
				"mipmaps/generate": true,
				"compress/high_quality": true
			}
		"uncompressed_audio":
			return {
				"compress/mode": 0
			}
		_:
			return {}

func reimport_asset(params: Dictionary) -> Dictionary:
	var asset_path: String = params.get("asset_path", "")
	var preset: String = params.get("preset", "")
	var custom_params: Dictionary = params.get("custom_params", {})

	if asset_path == "":
		return {"success": false, "message": "asset_path parameter cannot be empty."}

	if not FileAccess.file_exists(asset_path):
		return {
			"success": false,
			"message": "Asset file not found on disk: %s" % asset_path
		}

	var import_file_path: String = asset_path + ".import"
	var config: ConfigFile = ConfigFile.new()
	var load_err = config.load(import_file_path)

	# Apply preset if specified
	var applied_params: Dictionary = {}
	if preset != "":
		var preset_dict = _get_preset_params(preset)
		for k in preset_dict.keys():
			config.set_value("params", k, preset_dict[k])
			applied_params[k] = preset_dict[k]

	# Apply custom parameters
	for k in custom_params.keys():
		config.set_value("params", k, custom_params[k])
		applied_params[k] = custom_params[k]

	# Save updated .import file if changes were applied
	if applied_params.size() > 0:
		var save_err = config.save(import_file_path)
		if save_err != OK:
			return {
				"success": false,
				"message": "Failed to update .import file at '%s' (Error code: %d)." % [import_file_path, save_err]
			}

	# Trigger editor filesystem reimport
	var reimported: bool = false
	if _plugin:
		var editor_interface = _plugin.get_editor_interface()
		var filesystem = editor_interface.get_resource_filesystem()
		if filesystem:
			var files_to_reimport = PackedStringArray([asset_path])
			filesystem.reimport_files(files_to_reimport)
			reimported = true

	return {
		"success": true,
		"message": "Reimported asset '%s'%s." % [asset_path, " with preset '%s'" % preset if preset != "" else ""],
		"data": {
			"asset_path": asset_path,
			"preset_applied": preset,
			"parameters_updated": applied_params,
			"reimported_in_editor": reimported
		}
	}

func create_collision_polygon(params: Dictionary) -> Dictionary:
	var raw_points: Array = params.get("points", [])
	var polygon_type: String = params.get("polygon_type", "2D").to_upper()
	var parent_node_path: String = params.get("parent_node_path", ".")
	var node_name: String = params.get("node_name", "CollisionPolygon")
	var depth: float = float(params.get("depth", 1.0))
	var is_disabled: bool = bool(params.get("disabled", false))

	if raw_points.size() < 3:
		return {
			"success": false,
			"message": "A collision polygon requires at least 3 vertex points (got %d)." % raw_points.size()
		}

	var vec2_array: PackedVector2Array = PackedVector2Array()
	for pt in raw_points:
		if typeof(pt) == TYPE_ARRAY and (pt as Array).size() >= 2:
			var arr = pt as Array
			vec2_array.append(Vector2(float(arr[0]), float(arr[1])))
		else:
			return {
				"success": false,
				"message": "Invalid point format in points list. Expected [x, y] coordinates."
			}

	var created_node: Node = null
	if polygon_type == "3D":
		var cp3d = CollisionPolygon3D.new()
		cp3d.polygon = vec2_array
		cp3d.depth = depth
		cp3d.disabled = is_disabled
		created_node = cp3d
	else:
		var cp2d = CollisionPolygon2D.new()
		cp2d.polygon = vec2_array
		cp2d.disabled = is_disabled
		created_node = cp2d

	created_node.name = node_name

	if _plugin:
		var editor_interface = _plugin.get_editor_interface()
		var edited_root = editor_interface.get_edited_scene_root()
		if not edited_root:
			return {
				"success": false,
				"message": "No active scene open in Godot Editor. Create or open a scene first."
			}

		var parent_node = edited_root.get_node_or_null(NodePath(parent_node_path))
		if not parent_node and (parent_node_path == "." or parent_node_path == ""):
			parent_node = edited_root

		if not parent_node:
			return {
				"success": false,
				"message": "Parent node '%s' not found in active scene." % parent_node_path
			}

		var undo_redo = _plugin.get_undo_redo()
		if undo_redo:
			undo_redo.create_action("Add Collision Polygon '%s'" % node_name)
			undo_redo.add_do_method(parent_node, "add_child", created_node)
			undo_redo.add_do_method(created_node, "set_owner", edited_root)
			undo_redo.add_do_reference(created_node)
			undo_redo.add_undo_method(parent_node, "remove_child", created_node)
			undo_redo.commit_action()
		else:
			parent_node.add_child(created_node)
			created_node.owner = edited_root

	return {
		"success": true,
		"message": "Created %s collision polygon '%s' with %d vertices." % [polygon_type, node_name, vec2_array.size()],
		"data": {
			"node_name": node_name,
			"polygon_type": polygon_type,
			"vertex_count": vec2_array.size(),
			"depth": depth if polygon_type == "3D" else null,
			"parent_node_path": parent_node_path,
			"disabled": is_disabled
		}
	}
