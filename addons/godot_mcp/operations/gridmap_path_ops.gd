@tool
extends RefCounted

## Operations for Godot 3D GridMaps & Procedural Bezier Paths.

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

func configure_gridmap(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("gridmap_node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "GridMap node not found at '%s'." % node_path}

	if not (node is GridMap):
		return {"success": false, "message": "Node at '%s' is of class '%s', expected GridMap." % [node_path, node.get_class()]}

	var gm: GridMap = node
	var changes = []

	var mesh_lib_path = params.get("mesh_library_path")
	if mesh_lib_path != null and str(mesh_lib_path).strip_edges() != "":
		var mpath = str(mesh_lib_path).strip_edges()
		if ResourceLoader.exists(mpath):
			var lib = ResourceLoader.load(mpath)
			if lib is MeshLibrary:
				gm.mesh_library = lib
				changes.append("MeshLibrary: %s" % mpath)
			else:
				return {"success": false, "message": "Resource at '%s' is not a MeshLibrary." % mpath}
		else:
			return {"success": false, "message": "MeshLibrary file not found at '%s'." % mpath}

	var csize = params.get("cell_size")
	if csize != null and csize is Array and csize.size() >= 3:
		gm.cell_size = Vector3(float(csize[0]), float(csize[1]), float(csize[2]))
		changes.append("Cell Size: %s" % str(gm.cell_size))

	if params.has("collision_layer") and params["collision_layer"] != null:
		gm.collision_layer = int(params["collision_layer"])
		changes.append("Collision Layer: %d" % gm.collision_layer)

	if params.has("collision_mask") and params["collision_mask"] != null:
		gm.collision_mask = int(params["collision_mask"])
		changes.append("Collision Mask: %d" % gm.collision_mask)

	var cleared_count = 0
	if bool(params.get("clear_all", false)):
		var used = gm.get_used_cells()
		cleared_count = used.size()
		gm.clear()
		changes.append("Cleared all %d cells" % cleared_count)

	var cells_to_clear = params.get("cells_to_clear", [])
	if cells_to_clear is Array:
		for c in cells_to_clear:
			if c is Array and c.size() >= 3:
				gm.set_cell_item(Vector3i(int(c[0]), int(c[1]), int(c[2])), GridMap.INVALID_CELL_ITEM)
				cleared_count += 1

	var cells_set_count = 0
	var cells_to_set = params.get("cells_to_set", [])
	if cells_to_set is Array:
		for c in cells_to_set:
			if c is Dictionary:
				var pos_arr = c.get("position", [0, 0, 0])
				if pos_arr is Array and pos_arr.size() >= 3:
					var item_id = int(c.get("item_id", 0))
					var orientation = int(c.get("orientation", 0))
					gm.set_cell_item(Vector3i(int(pos_arr[0]), int(pos_arr[1]), int(pos_arr[2])), item_id, orientation)
					cells_set_count += 1

	if cells_set_count > 0:
		changes.append("Placed/Updated %d cells" % cells_set_count)

	var total_used = gm.get_used_cells().size()

	return {
		"success": true,
		"message": "Configured GridMap '%s': %s." % [gm.name, ", ".join(changes) if changes.size() > 0 else "No modifications"],
		"data": {
			"gridmap_name": gm.name,
			"gridmap_path": str(root.get_path_to(gm)),
			"cells_set": cells_set_count,
			"cells_cleared": cleared_count,
			"total_used_cells": total_used,
			"changes_applied": changes
		}
	}

func create_curve_path(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var ptype = str(params.get("path_type", "3d")).to_lower()
	var node_name = str(params.get("node_name", "Path3D" if ptype == "3d" else "Path2D"))
	var points = params.get("points", [])
	var is_closed = bool(params.get("closed", false))
	var add_pf = bool(params.get("add_path_follow", false))
	var pf_name = str(params.get("path_follow_name", "PathFollow"))

	var path_node: Node = null

	if ptype == "3d":
		var p3d = Path3D.new()
		p3d.name = node_name
		var c3d = Curve3D.new()

		for i in range(points.size()):
			var pt = points[i]
			if pt is Dictionary:
				var pos_arr = pt.get("position", [0, 0, 0])
				var in_arr = pt.get("in_handle", [0, 0, 0])
				var out_arr = pt.get("out_handle", [0, 0, 0])
				var pos = Vector3(float(pos_arr[0]), float(pos_arr[1]), float(pos_arr[2])) if (pos_arr is Array and pos_arr.size() >= 3) else Vector3.ZERO
				var in_h = Vector3(float(in_arr[0]), float(in_arr[1]), float(in_arr[2])) if (in_arr is Array and in_arr.size() >= 3) else Vector3.ZERO
				var out_h = Vector3(float(out_arr[0]), float(out_arr[1]), float(out_arr[2])) if (out_arr is Array and out_arr.size() >= 3) else Vector3.ZERO
				c3d.add_point(pos, in_h, out_h)
				if pt.has("tilt"):
					c3d.set_point_tilt(i, float(pt["tilt"]))

		p3d.curve = c3d
		parent_node.add_child(p3d)
		p3d.owner = root

		if add_pf:
			var pf = PathFollow3D.new()
			pf.name = pf_name
			pf.loop = is_closed
			p3d.add_child(pf)
			pf.owner = root

		path_node = p3d

	else:
		var p2d = Path2D.new()
		p2d.name = node_name
		var c2d = Curve2D.new()

		for i in range(points.size()):
			var pt = points[i]
			if pt is Dictionary:
				var pos_arr = pt.get("position", [0, 0])
				var in_arr = pt.get("in_handle", [0, 0])
				var out_arr = pt.get("out_handle", [0, 0])
				var pos = Vector2(float(pos_arr[0]), float(pos_arr[1])) if (pos_arr is Array and pos_arr.size() >= 2) else Vector2.ZERO
				var in_h = Vector2(float(in_arr[0]), float(in_arr[1])) if (in_arr is Array and in_arr.size() >= 2) else Vector2.ZERO
				var out_h = Vector2(float(out_arr[0]), float(out_arr[1])) if (out_arr is Array and out_arr.size() >= 2) else Vector2.ZERO
				c2d.add_point(pos, in_h, out_h)

		p2d.curve = c2d
		parent_node.add_child(p2d)
		p2d.owner = root

		if add_pf:
			var pf = PathFollow2D.new()
			pf.name = pf_name
			pf.loop = is_closed
			p2d.add_child(pf)
			pf.owner = root

		path_node = p2d

	return {
		"success": true,
		"message": "Created %s curve '%s' with %d control points under '%s'." % [ptype.to_upper(), node_name, points.size(), parent_node.name],
		"data": {
			"node_name": path_node.name,
			"node_path": str(root.get_path_to(path_node)),
			"path_type": ptype,
			"points_count": points.size(),
			"has_path_follow": add_pf,
			"is_closed": is_closed
		}
	}
