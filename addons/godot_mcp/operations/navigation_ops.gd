@tool
extends RefCounted

## Operations for creating NavigationRegion nodes and baking 2D/3D navigation meshes.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func bake_navmesh(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	var dimension: String = params.get("dimension", "3D").to_upper()
	var on_thread: bool = bool(params.get("on_thread", true))
	var save_path: String = params.get("save_navmesh_path", "")

	if node_path == "":
		return {"success": false, "message": "node_path parameter cannot be empty."}

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var target_node = edited_root.get_node_or_null(NodePath(node_path))
	if not target_node and (node_path == "." or node_path == ""):
		target_node = edited_root

	if not target_node:
		return {"success": false, "message": "NavigationRegion node not found at path '%s'." % node_path}

	var applied_params: Dictionary = {}

	if dimension == "2D" or target_node is NavigationRegion2D:
		var reg2d = target_node as NavigationRegion2D
		if not reg2d:
			return {
				"success": false,
				"message": "Target node '%s' is not a NavigationRegion2D." % target_node.name
			}

		var nav_poly: NavigationPolygon = reg2d.navigation_polygon
		if not nav_poly:
			nav_poly = NavigationPolygon.new()
			reg2d.navigation_polygon = nav_poly

		if params.has("cell_size") and params["cell_size"] != null:
			nav_poly.cell_size = float(params["cell_size"])
			applied_params["cell_size"] = nav_poly.cell_size

		if params.has("agent_radius") and params["agent_radius"] != null:
			nav_poly.agent_radius = float(params["agent_radius"])
			applied_params["agent_radius"] = nav_poly.agent_radius

		reg2d.bake_navigation_polygon(on_thread)

		if save_path != "":
			var err = ResourceSaver.save(nav_poly, save_path)
			if err == OK:
				applied_params["saved_to_file"] = save_path

		return {
			"success": true,
			"message": "Triggered 2D navigation polygon baking for '%s' (threaded: %s)." % [reg2d.name, str(on_thread)],
			"data": {
				"node_name": reg2d.name,
				"dimension": "2D",
				"on_thread": on_thread,
				"parameters": applied_params,
				"saved_to_file": save_path if save_path != "" else None
			}
		}

	else:
		var reg3d = target_node as NavigationRegion3D
		if not reg3d:
			return {
				"success": false,
				"message": "Target node '%s' is not a NavigationRegion3D." % target_node.name
			}

		var nav_mesh: NavigationMesh = reg3d.navigation_mesh
		if not nav_mesh:
			nav_mesh = NavigationMesh.new()
			reg3d.navigation_mesh = nav_mesh

		if params.has("agent_radius") and params["agent_radius"] != null:
			nav_mesh.agent_radius = float(params["agent_radius"])
			applied_params["agent_radius"] = nav_mesh.agent_radius

		if params.has("agent_height") and params["agent_height"] != null:
			nav_mesh.agent_height = float(params["agent_height"])
			applied_params["agent_height"] = nav_mesh.agent_height

		if params.has("agent_max_climb") and params["agent_max_climb"] != null:
			nav_mesh.agent_max_climb = float(params["agent_max_climb"])
			applied_params["agent_max_climb"] = nav_mesh.agent_max_climb

		if params.has("agent_max_slope") and params["agent_max_slope"] != null:
			nav_mesh.agent_max_slope = float(params["agent_max_slope"])
			applied_params["agent_max_slope"] = nav_mesh.agent_max_slope

		if params.has("cell_size") and params["cell_size"] != null:
			nav_mesh.cell_size = float(params["cell_size"])
			applied_params["cell_size"] = nav_mesh.cell_size

		if params.has("cell_height") and params["cell_height"] != null:
			nav_mesh.cell_height = float(params["cell_height"])
			applied_params["cell_height"] = nav_mesh.cell_height

		reg3d.bake_navigation_mesh(on_thread)

		if save_path != "":
			var err = ResourceSaver.save(nav_mesh, save_path)
			if err == OK:
				applied_params["saved_to_file"] = save_path

		return {
			"success": true,
			"message": "Triggered 3D navigation mesh baking for '%s' (threaded: %s)." % [reg3d.name, str(on_thread)],
			"data": {
				"node_name": reg3d.name,
				"dimension": "3D",
				"on_thread": on_thread,
				"parameters": applied_params,
				"saved_to_file": save_path if save_path != "" else None
			}
		}

func create_navigation_region(params: Dictionary) -> Dictionary:
	var name_str: String = params.get("name", "NavigationRegion3D")
	var dimension: String = params.get("dimension", "3D").to_upper()
	var parent_node_path: String = params.get("parent_node_path", ".")
	var navmesh_path: String = params.get("navmesh_path", "")

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var parent_node = edited_root.get_node_or_null(NodePath(parent_node_path))
	if not parent_node and (parent_node_path == "." or parent_node_path == ""):
		parent_node = edited_root

	if not parent_node:
		return {"success": false, "message": "Parent node '%s' not found." % parent_node_path}

	var region_node: Node = null
	if dimension == "2D":
		var r2 = NavigationRegion2D.new()
		if navmesh_path != "" and ResourceLoader.exists(navmesh_path):
			var res = load(navmesh_path)
			if res is NavigationPolygon:
				r2.navigation_polygon = res
		if not r2.navigation_polygon:
			r2.navigation_polygon = NavigationPolygon.new()
		region_node = r2
	else:
		var r3 = NavigationRegion3D.new()
		if navmesh_path != "" and ResourceLoader.exists(navmesh_path):
			var res = load(navmesh_path)
			if res is NavigationMesh:
				r3.navigation_mesh = res
		if not r3.navigation_mesh:
			r3.navigation_mesh = NavigationMesh.new()
		region_node = r3

	region_node.name = name_str

	var undo_redo = _plugin.get_undo_redo()
	if undo_redo:
		undo_redo.create_action("Create NavigationRegion '%s'" % name_str)
		undo_redo.add_do_method(parent_node, "add_child", region_node)
		undo_redo.add_do_method(region_node, "set_owner", edited_root)
		undo_redo.add_do_reference(region_node)
		undo_redo.add_undo_method(parent_node, "remove_child", region_node)
		undo_redo.commit_action()
	else:
		parent_node.add_child(region_node)
		region_node.owner = edited_root

	return {
		"success": true,
		"message": "Created %s '%s' under '%s'." % [region_node.get_class(), name_str, parent_node.name],
		"data": {
			"node_name": region_node.name,
			"type_name": region_node.get_class(),
			"dimension": dimension,
			"parent_node_path": parent_node_path,
			"navmesh_attached": navmesh_path if navmesh_path != "" else "default"
		}
	}
