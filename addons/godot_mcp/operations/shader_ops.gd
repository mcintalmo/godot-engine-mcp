@tool
extends RefCounted

## Operations for Godot Shader code generation, ShaderMaterial creation, and uniform inspection/tweaking.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func create_shader(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path == "":
		return {"success": false, "message": "path cannot be empty."}

	var shader_type: String = params.get("shader_type", "spatial")
	var code_param = params.get("code")
	var code: String = ""

	if code_param != null and str(code_param) != "":
		code = str(code_param)
	else:
		match shader_type:
			"canvas_item":
				code = "shader_type canvas_item;\n\nuniform vec4 tint_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);\n\nvoid fragment() {\n\tCOLOR = texture(TEXTURE, UV) * tint_color;\n}\n"
			"particles":
				code = "shader_type particles;\n\nvoid start() {\n}\n\nvoid process() {\n}\n"
			"fog":
				code = "shader_type fog;\n\nvoid fog() {\n\tDENSITY = 0.1;\n}\n"
			_: # spatial
				code = "shader_type spatial;\nrender_mode blend_mix, depth_draw_opaque, cull_back;\n\nuniform vec4 albedo_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);\nuniform float roughness : hint_range(0.0, 1.0) = 0.5;\nuniform float metallic : hint_range(0.0, 1.0) = 0.0;\n\nvoid fragment() {\n\tALBEDO = albedo_color.rgb;\n\tROUGHNESS = roughness;\n\tMETALLIC = metallic;\n}\n"

	var f = FileAccess.open(path, FileAccess.WRITE)
	if not f:
		return {"success": false, "message": "Failed to open '%s' for writing (Error: %d)." % [path, FileAccess.get_open_error()]}
	f.store_string(code)
	f.close()

	var shader_res = load(path)
	var mat_path: String = ""

	if bool(params.get("create_material", true)):
		var mat_dest = params.get("material_save_path")
		if mat_dest != null and str(mat_dest) != "":
			mat_path = str(mat_dest)
		else:
			mat_path = path.get_basename() + "_mat.tres"

		var mat = ShaderMaterial.new()
		mat.shader = shader_res if shader_res is Shader else load(path)
		var err = ResourceSaver.save(mat, mat_path)
		if err != OK:
			return {"success": false, "message": "Shader saved to '%s' but failed to save ShaderMaterial to '%s' (Error: %d)." % [path, mat_path, err]}

	if _plugin:
		var fs = _plugin.get_editor_interface().get_resource_filesystem()
		if fs:
			fs.scan()

	return {
		"success": true,
		"message": "Created shader '%s' (%s)." % [path, shader_type],
		"data": {
			"shader_path": path,
			"shader_type": shader_type,
			"material_path": mat_path if mat_path != "" else null
		}
	}

func set_shader_param(params: Dictionary) -> Dictionary:
	var param_name: String = params.get("parameter_name", "")
	if param_name == "":
		return {"success": false, "message": "parameter_name cannot be empty."}

	var raw_val = params.get("value")
	var val = _parse_variant_value(raw_val)

	var mat: ShaderMaterial = null
	var target_desc: String = ""

	var node_path: String = params.get("node_path", "")
	if node_path != "":
		var root: Node = null
		if _plugin:
			root = _plugin.get_editor_interface().get_edited_scene_root()
		if not root:
			return {"success": false, "message": "No active scene open in editor."}
		var target = root.get_node_or_null(node_path)
		if not target:
			return {"success": false, "message": "Node not found at '%s'." % node_path}

		if target is CanvasItem:
			if target.material is ShaderMaterial:
				mat = target.material
		elif target is GeometryInstance3D:
			if target.material_override is ShaderMaterial:
				mat = target.material_override
			elif target.get_surface_override_material(0) is ShaderMaterial:
				mat = target.get_surface_override_material(0)
		target_desc = "Node '%s'" % target.name

	if not mat:
		var mat_path: String = params.get("material_path", "")
		if mat_path != "":
			var res = load(mat_path)
			if res is ShaderMaterial:
				mat = res
				target_desc = "Material '%s'" % mat_path

	if not mat:
		return {"success": false, "message": "Could not find a valid ShaderMaterial on target node or material path."}

	mat.set_shader_parameter(param_name, val)

	var saved_res_path = mat.resource_path
	if saved_res_path != "":
		ResourceSaver.save(mat, saved_res_path)

	return {
		"success": true,
		"message": "Set shader parameter '%s' = %s on %s." % [param_name, str(val), target_desc],
		"data": {
			"parameter_name": param_name,
			"value": val,
			"target": target_desc,
			"material_path": saved_res_path if saved_res_path != "" else null
		}
	}

func _parse_variant_value(val: Variant) -> Variant:
	if val is Array:
		var arr: Array = val
		if arr.size() == 2:
			return Vector2(float(arr[0]), float(arr[1]))
		elif arr.size() == 3:
			return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
		elif arr.size() == 4:
			return Vector4(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
	elif val is String and str(val).begins_with("#"):
		return Color(str(val))
	return val
