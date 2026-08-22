@tool
extends RefCounted

## Operations for 'Playwright for Godot' Autonomous E2E Testing & UI Automation Engine.

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

func _collect_all_nodes(node: Node, acc: Array[Node]) -> void:
	if not node:
		return
	acc.append(node)
	for child in node.get_children():
		_collect_all_nodes(child, acc)

func find_elements(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var root_path = str(params.get("root_path", ""))
	var search_root = root
	if root_path != "" and root_path != ".":
		var scoped = _find_node(root_path, root)
		if scoped:
			search_root = scoped

	var stype = str(params.get("selector_type", "text")).to_lower()
	var query = str(params.get("query", ""))
	var max_res = int(params.get("max_results", 50))

	var all_nodes: Array[Node] = []
	_collect_all_nodes(search_root, all_nodes)

	var matches = []

	for n in all_nodes:
		if matches.size() >= max_res:
			break

		var is_match = false
		var text_val = ""

		if n.get("text") != null:
			text_val = str(n.get("text"))
		elif n.get("placeholder_text") != null:
			text_val = str(n.get("placeholder_text"))

		if stype == "text":
			if query.to_lower() in text_val.to_lower():
				is_match = true
		elif stype == "role" or stype == "type":
			if n.is_class(query) or n.get_class().to_lower() == query.to_lower():
				is_match = true
		elif stype == "name":
			if query.to_lower() in n.name.to_lower():
				is_match = true
		elif stype == "group":
			if n.is_in_group(query):
				is_match = true
		elif stype == "path":
			if str(n.get_path()).ends_with(query):
				is_match = true

		if is_match:
			var node_info = {
				"name": n.name,
				"path": str(root.get_path_to(n)),
				"class": n.get_class(),
				"text": text_val,
				"visible": n.is_visible_in_tree() if n is CanvasItem or n is Node3D else true,
			}
			if n is Control:
				var gr = n.get_global_rect()
				node_info["screen_rect"] = [gr.position.x, gr.position.y, gr.size.x, gr.size.y]
				node_info["center_position"] = [gr.get_center().x, gr.get_center().y]
			if n is BaseButton:
				node_info["disabled"] = n.disabled
			matches.append(node_info)

	return {
		"success": true,
		"message": "Found %d matching elements for selector [%s='%s']." % [matches.size(), stype, query],
		"data": {
			"selector_type": stype,
			"query": query,
			"matches_count": matches.size(),
			"elements": matches
		}
	}

func interact_node(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	var action = str(params.get("action", "click")).to_lower()
	var details = ""

	if action == "click":
		if node is BaseButton:
			if node.disabled:
				return {"success": false, "message": "Cannot click disabled button '%s'." % node.name}
			node.pressed.emit()
			details = "Emitted 'pressed' signal on Button"
		elif node is Control:
			var center = node.get_global_rect().get_center()
			var mb = InputEventMouseButton.new()
			mb.button_index = MOUSE_BUTTON_LEFT
			mb.pressed = true
			mb.position = center
			Input.parse_input_event(mb)
			mb.pressed = false
			Input.parse_input_event(mb)
			details = "Dispatched mouse click at center position %s" % str(center)
		else:
			details = "Triggered generic click"

	elif action == "type_text":
		var text_to_type = str(params.get("text", ""))
		var clear_first = bool(params.get("clear_before_type", true))
		if node is LineEdit:
			node.text = text_to_type if clear_first else (node.text + text_to_type)
			node.text_changed.emit(node.text)
			node.text_submitted.emit(node.text)
			details = "Typed '%s' into LineEdit" % text_to_type
		elif node is TextEdit:
			node.text = text_to_type if clear_first else (node.text + text_to_type)
			node.text_changed.emit()
			details = "Typed '%s' into TextEdit" % text_to_type
		else:
			return {"success": false, "message": "Node '%s' does not support text input." % node.name}

	elif action == "focus":
		if node is Control:
			node.grab_focus()
			details = "Grabbed UI focus"
		else:
			details = "Focus requested on non-control node"

	elif action == "hover":
		if node is Control:
			var center = node.get_global_rect().get_center()
			var mm = InputEventMouseMotion.new()
			mm.position = center
			Input.parse_input_event(mm)
			details = "Dispatched mouse hover at %s" % str(center)
		else:
			details = "Hover requested"

	elif action == "scroll":
		var delta_arr = params.get("scroll_delta", [0, 100])
		if node is ScrollContainer and delta_arr is Array and delta_arr.size() >= 2:
			node.scroll_horizontal += int(delta_arr[0])
			node.scroll_vertical += int(delta_arr[1])
			details = "Scrolled by (%d, %d)" % [int(delta_arr[0]), int(delta_arr[1])]
		else:
			details = "Scroll action applied"

	else:
		return {"success": false, "message": "Unsupported interaction action '%s'." % action}

	return {
		"success": true,
		"message": "Executed '%s' on node '%s': %s." % [action, node.name, details],
		"data": {
			"node_name": node.name,
			"node_path": str(root.get_path_to(node)),
			"action": action,
			"details": details
		}
	}

func wait_for_condition(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var ctype = str(params.get("condition_type", "node_exists")).to_lower()
	var node_path = str(params.get("node_path", ""))
	var satisfied = false
	var actual_value = null
	var details = ""

	if ctype == "node_exists":
		var n = _find_node(node_path, root)
		satisfied = (n != null)
		actual_value = satisfied
		details = "Node '%s' %s" % [node_path, "exists" if satisfied else "does not exist"]

	elif ctype == "node_visible":
		var n = _find_node(node_path, root)
		if n:
			satisfied = n.is_visible_in_tree() if (n is CanvasItem or n is Node3D) else true
		actual_value = satisfied
		details = "Node '%s' visibility is %s" % [node_path, str(satisfied)]

	elif ctype == "property_equals":
		var n = _find_node(node_path, root)
		var prop_name = str(params.get("property_name", ""))
		var expected = params.get("expected_value")
		if n and prop_name != "":
			actual_value = n.get(prop_name)
			satisfied = (str(actual_value) == str(expected))
		details = "Property '%s' equals '%s' (Actual: '%s')" % [prop_name, str(expected), str(actual_value)]

	elif ctype == "expression_true":
		var expr_str = str(params.get("expression", "true"))
		var expr = Expression.new()
		var err = expr.parse(expr_str)
		if err == OK:
			var res = expr.execute([], root)
			satisfied = bool(res)
			actual_value = res
			details = "Expression '%s' evaluated to %s" % [expr_str, str(res)]
		else:
			return {"success": false, "message": "Failed to parse expression '%s'." % expr_str}

	return {
		"success": true,
		"message": "Condition check [%s]: %s (Satisfied: %s)." % [ctype, details, str(satisfied)],
		"data": {
			"condition_type": ctype,
			"satisfied": satisfied,
			"actual_value": actual_value,
			"details": details
		}
	}

func assert_node_state(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "Node not found at '%s' for assertion." % node_path}

	var assertions = params.get("assertions", {})
	if not (assertions is Dictionary) or assertions.size() == 0:
		return {"success": false, "message": "No assertions provided."}

	var all_passed = true
	var results = []

	for k in assertions.keys():
		var expected = assertions[k]
		var actual = null
		var passed = false

		if k == "visible":
			actual = node.is_visible_in_tree() if (node is CanvasItem or node is Node3D) else true
			passed = (bool(actual) == bool(expected))
		elif k == "disabled" and node is BaseButton:
			actual = node.disabled
			passed = (bool(actual) == bool(expected))
		else:
			actual = node.get(k)
			passed = (str(actual) == str(expected))

		if not passed:
			all_passed = false

		results.append({
			"property": k,
			"expected": expected,
			"actual": actual,
			"passed": passed
		})

	return {
		"success": all_passed,
		"message": "Assertions on node '%s': %s (%d/%d passed)." % [node.name, "ALL PASSED" if all_passed else "FAILED", results.filter(func(r): return r.passed).size(), results.size()],
		"data": {
			"node_name": node.name,
			"node_path": str(root.get_path_to(node)),
			"all_passed": all_passed,
			"assertions": results
		}
	}
