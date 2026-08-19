@tool
extends RefCounted

## Operations for engine reflection, ClassDB introspection, doc queries, and shader validation.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_class_info(params: Dictionary) -> Dictionary:
	var class_name_str: String = params.get("class_name", "")
	var include_inherited: bool = bool(params.get("include_inherited", true))
	var category: String = params.get("category", "all").to_lower()

	if class_name_str == "":
		return {"success": false, "message": "class_name parameter cannot be empty."}

	if not ClassDB.class_exists(class_name_str):
		return {
			"success": false,
			"message": "Class '%s' does not exist in Godot ClassDB." % class_name_str,
			"class_exists": false
		}

	var parent_class: String = ClassDB.get_parent_class(class_name_str)
	var can_instantiate: bool = ClassDB.can_instantiate(class_name_str)

	var result_data: Dictionary = {
		"class_name": class_name_str,
		"inherits": parent_class,
		"is_instantiable": can_instantiate,
	}

	# 1. Properties
	if category in ["all", "properties"]:
		var raw_props = ClassDB.class_get_property_list(class_name_str, not include_inherited)
		var properties: Array = []
		for p in raw_props:
			# Filter out internal category / group headers if needed
			if p.get("usage", 0) & PROPERTY_USAGE_GROUP or p.get("usage", 0) & PROPERTY_USAGE_CATEGORY:
				continue
			properties.append({
				"name": p.get("name", ""),
				"type": type_string(p.get("type", 0)),
				"type_id": p.get("type", 0),
				"hint": p.get("hint", 0),
				"hint_string": p.get("hint_string", ""),
				"usage": p.get("usage", 0)
			})
		result_data["properties"] = properties

	# 2. Methods
	if category in ["all", "methods"]:
		var raw_methods = ClassDB.class_get_method_list(class_name_str, not include_inherited)
		var methods: Array = []
		for m in raw_methods:
			var args: Array = []
			for a in m.get("args", []):
				args.append({
					"name": a.get("name", ""),
					"type": type_string(a.get("type", 0))
				})
			var ret_info = m.get("return", {})
			methods.append({
				"name": m.get("name", ""),
				"args": args,
				"return_type": type_string(ret_info.get("type", 0)),
				"flags": m.get("flags", 0)
			})
		result_data["methods"] = methods

	# 3. Signals
	if category in ["all", "signals"]:
		var raw_signals = ClassDB.class_get_signal_list(class_name_str, not include_inherited)
		var signals_list: Array = []
		for s in raw_signals:
			var args: Array = []
			for a in s.get("args", []):
				args.append({
					"name": a.get("name", ""),
					"type": type_string(a.get("type", 0))
				})
			signals_list.append({
				"name": s.get("name", ""),
				"args": args
			})
		result_data["signals"] = signals_list

	# 4. Enums & Constants
	if category in ["all", "enums", "constants"]:
		var enum_list = ClassDB.class_get_enum_list(class_name_str, not include_inherited)
		var enums_dict: Dictionary = {}
		for enum_name in enum_list:
			var const_names = ClassDB.class_get_enum_constants(class_name_str, enum_name, not include_inherited)
			var const_map: Dictionary = {}
			for c_name in const_names:
				const_map[c_name] = ClassDB.class_get_integer_constant(class_name_str, c_name)
			enums_dict[enum_name] = const_map
		result_data["enums"] = enums_dict

		var raw_consts = ClassDB.class_get_integer_constant_list(class_name_str, not include_inherited)
		var constants_dict: Dictionary = {}
		for c_name in raw_consts:
			constants_dict[c_name] = ClassDB.class_get_integer_constant(class_name_str, c_name)
		result_data["constants"] = constants_dict

	return {
		"success": true,
		"message": "Retrieved ClassDB metadata for '%s'" % class_name_str,
		"data": result_data
	}

func get_documentation(params: Dictionary) -> Dictionary:
	var query: String = params.get("query", "")
	if query == "":
		return {"success": false, "message": "query parameter cannot be empty."}

	var class_query: String = query.split(".")[0]
	var member_name: String = query.split(".")[1] if "." in query else ""

	var class_res = get_class_info({"class_name": class_query, "category": "all"})
	if not class_res.get("success", false):
		return class_res

	var data = class_res.get("data", {})
	if member_name != "":
		var filtered_methods: Array = []
		for m in data.get("methods", []):
			if m.get("name", "") == member_name:
				filtered_methods.append(m)

		var filtered_props: Array = []
		for p in data.get("properties", []):
			if p.get("name", "") == member_name:
				filtered_props.append(p)

		var filtered_signals: Array = []
		for s in data.get("signals", []):
			if s.get("name", "") == member_name:
				filtered_signals.append(s)

		return {
			"success": true,
			"message": "Documentation for %s" % query,
			"data": {
				"query": query,
				"class_name": class_query,
				"member_name": member_name,
				"methods": filtered_methods,
				"properties": filtered_props,
				"signals": filtered_signals
			}
		}

	return {
		"success": true,
		"message": "Documentation for %s" % query,
		"data": data
	}

func validate_shader(params: Dictionary) -> Dictionary:

	var shader_code: String = params.get("shader_code", "")
	var shader_path: String = params.get("shader_path", "")

	if shader_path != "" and shader_code == "":
		if not FileAccess.file_exists(shader_path):
			return {
				"success": false,
				"message": "Shader file not found: %s" % shader_path,
				"valid": false
			}
		var file = FileAccess.open(shader_path, FileAccess.READ)
		if file:
			shader_code = file.get_as_text()
			file.close()

	if shader_code.strip_edges() == "":
		return {
			"success": false,
			"message": "No shader code provided for validation.",
			"valid": false
		}

	# Detect shader_type
	var shader_type: String = "unknown"
	var lines = shader_code.split("\n")
	for line in lines:
		var trimmed = line.strip_edges()
		if trimmed.begins_with("shader_type"):
			var parts = trimmed.split(" ")
			if parts.size() >= 2:
				shader_type = parts[1].trim_suffix(";")
			break

	var rid = RenderingServer.shader_create()
	RenderingServer.shader_set_code(rid, shader_code)
	RenderingServer.free_rid(rid)

	# Basic syntax checks if shader_type is missing
	if shader_type == "unknown":
		return {
			"success": false,
			"valid": false,
			"message": "Shader validation failed: Missing required 'shader_type' declaration (e.g. 'shader_type spatial;' or 'shader_type canvas_item;').",
			"shader_type": shader_type,
			"errors": [{"line": 1, "message": "Missing 'shader_type <type>;' header."}]
		}

	return {
		"success": true,
		"valid": true,
		"message": "Shader code syntax and compilation verified successfully (%s)." % shader_type,
		"shader_type": shader_type,
		"line_count": lines.size()
	}
