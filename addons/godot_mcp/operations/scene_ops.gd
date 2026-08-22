@tool
class_name SceneOperations
extends RefCounted

var _plugin: Node

func _init(plugin: Node = null) -> void:
	_plugin = plugin


func _get_scene_root() -> Node:
	if _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei and ei.get_edited_scene_root():
			return ei.get_edited_scene_root()
	if _plugin and _plugin.is_inside_tree():
		var tree = _plugin.get_tree()
		if tree and tree.current_scene:
			return tree.current_scene
		elif tree and tree.root and tree.root.get_child_count() > 0:
			return tree.root.get_child(tree.root.get_child_count() - 1)
	return null

func list_nodes(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor.", "nodes": []}


	var root_path = params.get("root_path", ".")
	var max_depth = int(params.get("max_depth", 4))
	var include_properties = bool(params.get("include_properties", false))

	var start_node = edited_root if root_path == "." else edited_root.get_node_or_null(root_path)
	if not start_node:
		return {"success": false, "message": "Root node path '%s' not found." % root_path, "nodes": []}

	var nodes_list: Array = []
	_collect_nodes(start_node, edited_root, 0, max_depth, include_properties, nodes_list)

	return {
		"success": true,
		"message": "Found %d nodes" % nodes_list.size(),
		"scene_file": edited_root.scene_file_path,
		"nodes": nodes_list
	}

func _collect_nodes(node: Node, scene_root: Node, current_depth: int, max_depth: int, include_props: bool, out_list: Array) -> void:
	if current_depth > max_depth:
		return

	var rel_path = str(scene_root.get_path_to(node)) if node != scene_root else "."
	var node_warnings = _get_node_warnings(node)
	var info = {
		"name": node.name,
		"node_path": rel_path,
		"type_name": node.get_class(),
		"child_count": node.get_child_count(),
		"unique_name_in_owner": node.unique_name_in_owner,
		"script_path": node.get_script().resource_path if node.get_script() else null,
		"warnings": node_warnings
	}


	if include_props:
		info["properties"] = _get_node_properties(node, false)

	out_list.append(info)

	for child in node.get_children():
		_collect_nodes(child, scene_root, current_depth + 1, max_depth, include_props, out_list)

func get_node_info(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_path = params.get("node_path", ".")
	var target = edited_root if node_path == "." else edited_root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at path: %s" % node_path}

	var include_inherited = bool(params.get("include_inherited_properties", false))
	var rel_path = str(edited_root.get_path_to(target)) if target != edited_root else "."

	var signals_list: Array = []
	for sig in target.get_signal_list():
		var connections = target.get_signal_connection_list(sig.name)
		for conn in connections:
			var callable: Callable = conn.get("callable", Callable())
			var target_obj = callable.get_object()
			var target_path = str(edited_root.get_path_to(target_obj)) if (target_obj is Node and edited_root.is_ancestor_of(target_obj)) else str(target_obj)
			signals_list.append({
				"signal_name": sig.name,
				"target_node_path": target_path,
				"method_name": callable.get_method()
			})

	var target_warnings = _get_node_warnings(target)
	return {
		"success": true,
		"node": {
			"name": target.name,
			"node_path": rel_path,
			"type_name": target.get_class(),
			"parent_path": str(edited_root.get_path_to(target.get_parent())) if target.get_parent() and target != edited_root else null,
			"child_count": target.get_child_count(),
			"unique_name_in_owner": target.unique_name_in_owner,
			"script_path": target.get_script().resource_path if target.get_script() else null,
			"properties": _get_node_properties(target, include_inherited),
			"signals": signals_list,
			"warnings": target_warnings
		}
	}


func _get_node_properties(node: Node, include_inherited: bool) -> Dictionary:
	var props = {}
	for p in node.get_property_list():
		var p_name = p.name
		if p_name.begins_with("_"):
			continue
		if p.usage & PROPERTY_USAGE_EDITOR or include_inherited:
			var val = node.get(p_name)
			props[p_name] = _serialize_variant(val)
	return props

func _serialize_variant(val: Variant) -> Variant:
	if val is Vector2:
		return [val.x, val.y]
	elif val is Vector3:
		return [val.x, val.y, val.z]
	elif val is Color:
		return [val.r, val.g, val.b, val.a]
	elif val is Rect2:
		return [val.position.x, val.position.y, val.size.x, val.size.y]
	elif val is Transform2D or val is Transform3D:
		return str(val)
	elif val is Object:
		return val.get_class() if val else null
	return val

func _deserialize_variant(val: Variant) -> Variant:
	if val is Array:
		if val.size() == 2:
			return Vector2(float(val[0]), float(val[1]))
		elif val.size() == 3:
			return Vector3(float(val[0]), float(val[1]), float(val[2]))
		elif val.size() == 4:
			return Color(float(val[0]), float(val[1]), float(val[2]), float(val[3]))
	elif val is String and ClassDB.class_exists(val) and ClassDB.is_parent_class(val, "Resource"):
		return ClassDB.instantiate(val)
	elif val is Dictionary and val.has("type") and ClassDB.class_exists(str(val["type"])) and ClassDB.is_parent_class(str(val["type"]), "Resource"):
		var res = ClassDB.instantiate(str(val["type"]))
		for k in val:
			if k != "type":
				res.set(k, _deserialize_variant(val[k]))
		return res
	return val

func _get_node_warnings(node: Node) -> Array:
	var out: Array = []
	if node.has_method("_get_configuration_warnings"):
		var w = node._get_configuration_warnings()
		for item in w:
			out.append(str(item))
	if out.is_empty() and node.has_method("get_configuration_warnings"):
		var w = node.get_configuration_warnings()
		for item in w:
			out.append(str(item))

	# Heuristic validation for common Godot 4 misconfigurations
	if node is CSGShape3D:
		var p = node.get_parent()
		if p and not (p is CSGShape3D or p is CSGCombiner3D):
			var w_msg = "CSGShape3D '%s' parent '%s' is '%s'. Parent must be CSGCombiner3D or CSGShape3D to render." % [node.name, p.name, p.get_class()]
			if not out.has(w_msg):
				out.append(w_msg)
	elif node is MeshInstance3D and not node.mesh:
		var w_msg = "MeshInstance3D '%s' has no Mesh resource assigned." % node.name
		if not out.has(w_msg):
			out.append(w_msg)
	elif node is CollisionShape3D and not node.shape:
		var w_msg = "CollisionShape3D '%s' has no Shape3D resource assigned." % node.name
		if not out.has(w_msg):
			out.append(w_msg)
	elif node is CollisionShape2D and not node.shape:
		var w_msg = "CollisionShape2D '%s' has no Shape2D resource assigned." % node.name
		if not out.has(w_msg):
			out.append(w_msg)
	elif node is PathFollow3D:
		var p = node.get_parent()
		if p and not (p is Path3D):
			var w_msg = "PathFollow3D '%s' parent is '%s' (%s). Parent must be a Path3D node." % [node.name, p.name, p.get_class()]
			if not out.has(w_msg):
				out.append(w_msg)
	elif node is PathFollow2D:
		var p = node.get_parent()
		if p and not (p is Path2D):
			var w_msg = "PathFollow2D '%s' parent is '%s' (%s). Parent must be a Path2D node." % [node.name, p.name, p.get_class()]
			if not out.has(w_msg):
				out.append(w_msg)
	elif node is AnimationTree:
		if not node.tree_root:
			var w_msg = "AnimationTree '%s' has no root AnimationNode assigned (tree_root is null)." % node.name
			if not out.has(w_msg):
				out.append(w_msg)
		if str(node.anim_player) == "":
			var w_msg = "AnimationTree '%s' has no AnimationPlayer assigned (anim_player is empty)." % node.name
			if not out.has(w_msg):
				out.append(w_msg)
	elif node is TileMapLayer and not node.tile_set:
		var w_msg = "TileMapLayer '%s' has no TileSet resource assigned." % node.name
		if not out.has(w_msg):
			out.append(w_msg)
	elif node is GPUParticles3D and not node.draw_pass_1:
		var w_msg = "GPUParticles3D '%s' has no draw pass Mesh assigned (draw_pass_1 is null)." % node.name
		if not out.has(w_msg):
			out.append(w_msg)

	return out



func _get_undo_redo() -> EditorUndoRedoManager:
	if _plugin and _plugin.has_method("get_undo_redo"):
		return _plugin.get_undo_redo()
	return null

func create_node(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var type_name = params.get("type_name", "Node")
	var node_name = params.get("name", "NewNode")
	var parent_path = params.get("parent_path", ".")
	var properties: Dictionary = params.get("properties", {})
	var script_path = params.get("script_path")

	if not ClassDB.class_exists(type_name) or not ClassDB.can_instantiate(type_name):
		return {"success": false, "message": "Class '%s' is not valid or cannot be instantiated." % type_name}

	var parent = edited_root if parent_path == "." else edited_root.get_node_or_null(parent_path)
	if not parent:
		return {"success": false, "message": "Parent node not found at: %s" % parent_path}

	var new_node = ClassDB.instantiate(type_name) as Node
	if not new_node:
		return {"success": false, "message": "Failed to instantiate class: %s" % type_name}

	new_node.name = node_name

	if script_path:
		var script_res = load(script_path)
		if script_res is Script:
			new_node.set_script(script_res)

	for p_name in properties:
		new_node.set(p_name, _deserialize_variant(properties[p_name]))

	var undo_redo = _get_undo_redo()
	if undo_redo:
		undo_redo.create_action("MCP: Add Node %s" % node_name)
		undo_redo.add_do_method(parent, "add_child", new_node)
		undo_redo.add_do_property(new_node, "owner", edited_root)
		undo_redo.add_do_reference(new_node)
		undo_redo.add_undo_method(parent, "remove_child", new_node)
		undo_redo.commit_action()
	else:
		parent.add_child(new_node)
		new_node.owner = edited_root

	var rel_path = str(edited_root.get_path_to(new_node))
	var warnings = _get_node_warnings(new_node)
	var hint = null
	if warnings.size() > 0:
		hint = "Node created with %d configuration warning(s): %s" % [warnings.size(), "; ".join(warnings)]

	return {
		"success": true,
		"message": "Created node '%s' of type '%s'" % [node_name, type_name],
		"node_path": rel_path,
		"warnings": warnings,
		"actionable_hint": hint
	}

func modify_node(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_path = params.get("node_path", ".")
	var target = edited_root if node_path == "." else edited_root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at: %s" % node_path}

	var properties: Dictionary = params.get("properties", {})
	var undo_redo = _get_undo_redo()
	if undo_redo:
		undo_redo.create_action("MCP: Modify Node %s" % target.name)
		for p_name in properties:
			var old_val = target.get(p_name)
			var new_val = _deserialize_variant(properties[p_name])
			undo_redo.add_do_property(target, p_name, new_val)
			undo_redo.add_undo_property(target, p_name, old_val)
		undo_redo.commit_action()
	else:
		for p_name in properties:
			target.set(p_name, _deserialize_variant(properties[p_name]))

	var warnings = _get_node_warnings(target)
	var hint = null
	if warnings.size() > 0:
		hint = "Node has %d configuration warning(s): %s" % [warnings.size(), "; ".join(warnings)]

	return {
		"success": true,
		"message": "Updated %d properties on node '%s'" % [properties.size(), target.name],
		"node_path": node_path,
		"warnings": warnings,
		"actionable_hint": hint
	}



func delete_node(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var node_path = params.get("node_path")
	if not node_path or node_path == ".":
		return {"success": false, "message": "Cannot delete scene root directly."}

	var target = edited_root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at: %s" % node_path}

	var parent = target.get_parent()
	var undo_redo = _get_undo_redo()
	if undo_redo:
		undo_redo.create_action("MCP: Delete Node %s" % target.name)
		undo_redo.add_do_method(parent, "remove_child", target)
		undo_redo.add_undo_method(parent, "add_child", target)
		undo_redo.add_undo_property(target, "owner", edited_root)
		undo_redo.commit_action()
	else:
		parent.remove_child(target)
		target.queue_free()

	return {"success": true, "message": "Deleted node '%s'" % target.name}


	return {"success": true, "message": "Deleted node '%s'" % target.name}

func connect_signal(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var src_path = params.get("source_node_path")
	var sig_name = params.get("signal_name")
	var tgt_path = params.get("target_node_path")
	var method = params.get("method_name")
	var flags = int(params.get("flags", 0))

	var src = edited_root if src_path == "." else edited_root.get_node_or_null(src_path)
	var tgt = edited_root if tgt_path == "." else edited_root.get_node_or_null(tgt_path)

	if not src:
		return {"success": false, "message": "Source node not found: %s" % src_path}
	if not tgt:
		return {"success": false, "message": "Target node not found: %s" % tgt_path}
	if not src.has_signal(sig_name):
		return {"success": false, "message": "Source node does not have signal: %s" % sig_name}

	var callable = Callable(tgt, method)
	if src.is_connected(sig_name, callable):
		return {"success": true, "message": "Signal '%s' already connected." % sig_name}

	var err = src.connect(sig_name, callable, flags)
	if err != OK:
		return {"success": false, "message": "Failed to connect signal, error code: %d" % err}

	return {"success": true, "message": "Connected signal '%s' to '%s.%s'" % [sig_name, tgt.name, method]}

func instantiate_scene(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var scene_path = params.get("scene_path")
	var parent_path = params.get("parent_path", ".")
	var custom_name = params.get("name")

	var parent = edited_root if parent_path == "." else edited_root.get_node_or_null(parent_path)
	if not parent:
		return {"success": false, "message": "Parent node not found: %s" % parent_path}

	var packed = load(scene_path)
	if not packed is PackedScene:
		return {"success": false, "message": "File is not a valid PackedScene: %s" % scene_path}

	var instance = packed.instantiate()
	if custom_name:
		instance.name = custom_name

	var undo_redo = _plugin.get_undo_redo()
	undo_redo.create_action("MCP: Instantiate Scene %s" % scene_path)
	undo_redo.add_do_method(parent, "add_child", instance)
	undo_redo.add_do_property(instance, "owner", edited_root)
	undo_redo.add_do_reference(instance)
	undo_redo.add_undo_method(parent, "remove_child", instance)
	undo_redo.commit_action()

	return {
		"success": true,
		"message": "Instantiated scene '%s' as '%s'" % [scene_path, instance.name],
		"node_path": str(edited_root.get_path_to(instance))
	}

func save_scene(params: Dictionary) -> Dictionary:
	var edited_root = _get_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in editor."}

	var scene_path = params.get("scene_path")
	if scene_path:
		var packed = PackedScene.new()
		var pack_err = packed.pack(edited_root)
		if pack_err != OK:
			return {"success": false, "message": "Failed to pack scene, error code: %d" % pack_err}
		var save_err = ResourceSaver.save(packed, scene_path)
		if save_err != OK:
			return {"success": false, "message": "Failed to save scene to '%s', error: %d" % [scene_path, save_err]}
		return {"success": true, "message": "Saved scene to %s" % scene_path}
	else:
		if _plugin and _plugin.has_method("get_editor_interface"):
			var ei = _plugin.get_editor_interface()
			if ei:
				ei.save_scene()
		return {"success": false, "message": "No editor interface available to save scene without scene_path."}

func open_scene(params: Dictionary) -> Dictionary:
	var scene_path: String = params.get("scene_path", "")
	if scene_path == "":
		return {"success": false, "message": "scene_path parameter cannot be empty."}

	if _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei:
			if ei.has_method("reload_scene_from_path"):
				ei.reload_scene_from_path(scene_path)
			if ei.has_method("open_scene_from_path"):
				ei.open_scene_from_path(scene_path)
			var root = _get_scene_root()
			if root and ei.has_method("set_main_screen_editor"):
				if root is Control or root is Node2D or root is CanvasLayer:
					ei.set_main_screen_editor("2D")
				else:
					ei.set_main_screen_editor("3D")
			return {"success": true, "message": "Opened scene '%s' in Godot editor." % scene_path}

	return {"success": false, "message": "EditorInterface is not available to open scenes."}

func create_scene(params: Dictionary) -> Dictionary:
	var scene_path: String = params.get("scene_path", "")
	var root_type: String = params.get("root_type", "Node2D")
	var root_name: String = params.get("root_name", "Root")
	var properties: Dictionary = params.get("properties", {})
	var open_in_editor: bool = bool(params.get("open_in_editor", true))

	if scene_path == "":
		return {"success": false, "message": "scene_path parameter cannot be empty."}

	if not ClassDB.class_exists(root_type) or not ClassDB.can_instantiate(root_type):
		return {"success": false, "message": "Class '%s' is not valid or cannot be instantiated." % root_type}

	var root_node = ClassDB.instantiate(root_type) as Node
	if not root_node:
		return {"success": false, "message": "Failed to instantiate root node '%s'" % root_type}

	root_node.name = root_name
	for p_name in properties:
		root_node.set(p_name, _deserialize_variant(properties[p_name]))

	var packed = PackedScene.new()
	var pack_err = packed.pack(root_node)
	if pack_err != OK:
		root_node.free()
		return {"success": false, "message": "Failed to pack root node into scene (error: %d)" % pack_err}

	var save_err = ResourceSaver.save(packed, scene_path)
	root_node.free()
	if save_err != OK:
		return {"success": false, "message": "Failed to save scene to '%s' (error: %d)" % [scene_path, save_err]}

	if open_in_editor and _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei:
			if ei.has_method("open_scene_from_path"):
				ei.open_scene_from_path(scene_path)
			if ei.has_method("set_main_screen_editor"):
				if root_type in ["Control", "CanvasLayer", "Node2D"] or ClassDB.is_parent_class(root_type, "Control") or ClassDB.is_parent_class(root_type, "Node2D"):
					ei.set_main_screen_editor("2D")
				else:
					ei.set_main_screen_editor("3D")

	return {
		"success": true,
		"message": "Created new scene '%s' with root node '%s' (%s)" % [scene_path, root_name, root_type],
		"scene_path": scene_path,
		"root_name": root_name,
		"root_type": root_type
	}

func get_node(params: Dictionary) -> Dictionary:
	return get_node_info(params)





