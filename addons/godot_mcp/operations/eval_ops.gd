@tool
extends RefCounted

## Operations for safe GDScript Expression runtime evaluation against scene nodes or global scope.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func evaluate_expression(params: Dictionary) -> Dictionary:
	var expr_str: String = params.get("expression", "")
	if expr_str == "":
		return {"success": false, "message": "expression cannot be empty."}

	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	var target_node: Object = root
	var node_path: String = params.get("node_path", "")
	if node_path != "" and root:
		var n = root.get_node_or_null(node_path)
		if n:
			target_node = n

	var input_vars: Dictionary = params.get("input_variables", {})
	var var_names: PackedStringArray = PackedStringArray()
	var var_values: Array = []

	for k in input_vars.keys():
		var_names.append(str(k))
		var_values.append(input_vars[k])

	var expr = Expression.new()
	var parse_err = expr.parse(expr_str, var_names)
	if parse_err != OK:
		return {
			"success": false,
			"message": "Failed to parse expression '%s' (Error: %s)." % [expr_str, expr.get_error_text()],
			"error_code": "PARSE_ERROR"
		}

	var eval_result = expr.execute(var_values, target_node, false)
	if expr.has_execute_failed():
		return {
			"success": false,
			"message": "Execution failed for '%s' (Error: %s)." % [expr_str, expr.get_error_text()],
			"error_code": "EXEC_ERROR"
		}

	return {
		"success": true,
		"message": "Evaluated expression successfully: %s" % str(eval_result),
		"data": {
			"expression": expr_str,
			"result": eval_result,
			"result_type": type_string(typeof(eval_result)),
			"context_node": str(target_node.get_path()) if target_node and target_node is Node else null
		}
	}
