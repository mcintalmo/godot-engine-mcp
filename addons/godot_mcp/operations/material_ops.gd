@tool
extends RefCounted

## Operations for creating, configuring, and assigning Godot materials and shaders.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _coerce_value(val: Variant) -> Variant:
	if typeof(val) == TYPE_ARRAY:
		var arr = val as Array
		if arr.size() == 4:
			return Color(arr[0], arr[1], arr[2], arr[3])
		elif arr.size() == 3:
			return Vector3(arr[0], arr[1], arr[2])
		elif arr.size() == 2:
			return Vector2(arr[0], arr[1])
	elif typeof(val) == TYPE_STRING:
		var s = val as String
		if s.begins_with("res://") and ResourceLoader.exists(s):
			return load(s)
	return val

func create_material(params: Dictionary) -> Dictionary:
	var material_path: String = params.get("material_path", "")
	var material_type: String = params.get("material_type", "StandardMaterial3D")
	var properties: Dictionary = params.get("properties", {})
	var shader_path: String = params.get("shader_path", "")
	var shader_code: String = params.get("shader_code", "")
	var assign_to_node_path: String = params.get("assign_to_node_path", "")

	if material_path == "":
		return {"success": false, "message": "material_path parameter cannot be empty."}

	# 1. Instantiate the material
	var mat: Material = null
	match material_type:
		"ShaderMaterial":
			var sm = ShaderMaterial.new()
			if shader_path != "" and ResourceLoader.exists(shader_path):
				sm.shader = load(shader_path)
			elif shader_code != "":
				var shader = Shader.new()
				shader.code = shader_code
				sm.shader = shader
			mat = sm
		"CanvasItemMaterial":
			mat = CanvasItemMaterial.new()
		"ORMMaterial3D":
			mat = ORMMaterial3D.new()
		"StandardMaterial3D", _:
			mat = StandardMaterial3D.new()

	if not mat:
		return {
			"success": false,
			"message": "Failed to instantiate material of type '%s'." % material_type
		}

	# 2. Apply properties
	var applied_props: Dictionary = {}
	for k in properties.keys():
		var val = _coerce_value(properties[k])
		if material_type == "ShaderMaterial" and mat is ShaderMaterial:
			(mat as ShaderMaterial).set_shader_parameter(k, val)
			applied_props[k] = str(val)
		else:
			mat.set(k, val)
			applied_props[k] = str(val)

	# 3. Ensure parent directory exists and save resource
	var dir_path = material_path.get_base_dir()
	if dir_path != "" and dir_path != "res://":
		if not DirAccess.dir_exists_absolute(dir_path):
			DirAccess.make_dir_recursive_absolute(dir_path)

	var save_err = ResourceSaver.save(mat, material_path)
	if save_err != OK:
		return {
			"success": false,
			"message": "Failed to save material to '%s' (Error code: %d)." % [material_path, save_err]
		}

	var assigned_node: String = ""
	# 4. Optionally assign to a scene node
	if assign_to_node_path != "" and _plugin:
		var editor_interface = _plugin.get_editor_interface()
		var edited_root = editor_interface.get_edited_scene_root()
		if edited_root:
			var target_node = edited_root.get_node_or_null(NodePath(assign_to_node_path))
			if not target_node and assign_to_node_path == ".":
				target_node = edited_root

			if target_node:
				if target_node is GeometryInstance3D:
					(target_node as GeometryInstance3D).material_override = mat
					assigned_node = target_node.name
				elif target_node is CanvasItem:

					(target_node as CanvasItem).material = mat
					assigned_node = target_node.name
				elif target_node.has_method("set_material"):
					target_node.set_material(mat)
					assigned_node = target_node.name

	return {
		"success": true,
		"message": "Created material '%s' of type '%s'." % [material_path, material_type],
		"data": {
			"material_path": material_path,
			"material_type": material_type,
			"properties_applied": applied_props,
			"assigned_to_node": assigned_node
		}
	}
