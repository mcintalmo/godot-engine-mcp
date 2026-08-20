@tool
extends RefCounted

## Operations for Godot signal introspection, event connection wiring, and connection graph inspection.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_node_signals(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	if node_path == "":
		return {"success": false, "message": "node_path cannot be empty."}

	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var target = root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at path '%s'." % node_path}

	var include_inherited: bool = bool(params.get("include_inherited", true))
	var signals_list = target.get_signal_list()
	var result_signals: Array = []

	for sig in signals_list:
		var sig_name = str(sig.get("name", ""))
		var args_arr = sig.get("args", [])
		var formatted_args: Array = []

		for a in args_arr:
			formatted_args.append({
				"name": a.get("name", ""),
				"type": type_string(a.get("type", TYPE_NIL))
			})

		result_signals.append({
			"name": sig_name,
			"argument_count": formatted_args.size(),
			"arguments": formatted_args
		})

	return {
		"success": true,
		"message": "Found %d signals on node '%s' (%s)." % [result_signals.size(), target.name, target.get_class()],
		"data": {
			"node_name": target.name,
			"node_path": str(target.get_path()),
			"node_class": target.get_class(),
			"signal_count": result_signals.size(),
			"signals": result_signals
		}
	}

func connect_signal(params: Dictionary) -> Dictionary:
	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var src_path: String = params.get("source_node_path", "")
	var sig_name: String = params.get("signal_name", "")
	var tgt_path: String = params.get("target_node_path", "")
	var method_name: String = params.get("method_name", "")
	var disconnect_flag: bool = bool(params.get("disconnect", false))

	var src_node = root.get_node_or_null(src_path)
	if not src_node:
		return {"success": false, "message": "Source node not found at '%s'." % src_path}

	var tgt_node = root.get_node_or_null(tgt_path)
	if not tgt_node:
		return {"success": false, "message": "Target node not found at '%s'." % tgt_path}

	if not src_node.has_signal(sig_name):
		return {"success": false, "message": "Source node '%s' does not have signal '%s'." % [src_node.name, sig_name]}

	var callable = Callable(tgt_node, method_name)

	if disconnect_flag:
		if src_node.is_connected(sig_name, callable):
			src_node.disconnect(sig_name, callable)
			return {
				"success": true,
				"message": "Disconnected signal '%s.%s' from '%s.%s'." % [src_node.name, sig_name, tgt_node.name, method_name],
				"data": {
					"source_node": str(src_node.get_path()),
					"signal_name": sig_name,
					"target_node": str(tgt_node.get_path()),
					"method_name": method_name,
					"connected": false
				}
			}
		else:
			return {"success": false, "message": "Signal '%s.%s' is not connected to '%s.%s'." % [src_node.name, sig_name, tgt_node.name, method_name]}

	var flags = 0
	if bool(params.get("persist", true)):
		flags |= Object.CONNECT_PERSIST
	if bool(params.get("one_shot", false)):
		flags |= Object.CONNECT_ONE_SHOT
	if bool(params.get("deferred", false)):
		flags |= Object.CONNECT_DEFERRED

	if src_node.is_connected(sig_name, callable):
		return {"success": true, "message": "Signal '%s.%s' is already connected to '%s.%s'." % [src_node.name, sig_name, tgt_node.name, method_name]}

	var err = src_node.connect(sig_name, callable, flags)
	if err != OK:
		return {"success": false, "message": "Failed to connect signal (Error: %d)." % err}

	return {
		"success": true,
		"message": "Connected signal '%s.%s' -> '%s.%s' (Flags: %d)." % [src_node.name, sig_name, tgt_node.name, method_name, flags],
		"data": {
			"source_node": str(src_node.get_path()),
			"signal_name": sig_name,
			"target_node": str(tgt_node.get_path()),
			"method_name": method_name,
			"flags": flags,
			"connected": true
		}
	}

func get_signal_connections(params: Dictionary) -> Dictionary:
	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_path: String = params.get("node_path", "")
	var target = root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at '%s'." % node_path}

	var sig_filter = params.get("signal_name")
	var inc = bool(params.get("incoming", true))
	var outg = bool(params.get("outgoing", true))

	var outgoing_conns: Array = []
	var incoming_conns: Array = []

	if outg:
		for sig in target.get_signal_list():
			var sname = str(sig.get("name", ""))
			if sig_filter and str(sig_filter) != "" and sname != str(sig_filter):
				continue
			var conns = target.get_signal_connection_list(sname)
			for c in conns:
				var call_obj = c.get("callable")
				var tgt_obj = call_obj.get_object() if call_obj is Callable else null
				outgoing_conns.append({
					"signal_name": sname,
					"target_node": str(tgt_obj.get_path()) if tgt_obj and tgt_obj is Node else str(tgt_obj),
					"method_name": call_obj.get_method() if call_obj is Callable else "",
					"flags": c.get("flags", 0)
				})

	if inc:
		var all_nodes = _get_all_nodes_recursive(root)
		for n in all_nodes:
			for sig in n.get_signal_list():
				var sname = str(sig.get("name", ""))
				var conns = n.get_signal_connection_list(sname)
				for c in conns:
					var call_obj = c.get("callable")
					if call_obj is Callable and call_obj.get_object() == target:
						incoming_conns.append({
							"source_node": str(n.get_path()),
							"signal_name": sname,
							"method_name": call_obj.get_method(),
							"flags": c.get("flags", 0)
						})

	return {
		"success": true,
		"message": "Found %d outgoing and %d incoming signal connections for '%s'." % [outgoing_conns.size(), incoming_conns.size(), target.name],
		"data": {
			"node_path": str(target.get_path()),
			"outgoing_connections": outgoing_conns,
			"incoming_connections": incoming_conns
		}
	}

func _get_all_nodes_recursive(node: Node) -> Array[Node]:
	var result: Array[Node] = [node]
	for c in node.get_children():
		result.append_array(_get_all_nodes_recursive(c))
	return result
