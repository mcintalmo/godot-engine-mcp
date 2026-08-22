@tool
extends RefCounted

## Operations for Godot GPU MultiMesh Scattering & Foliage Systems.

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

func scatter_multimesh(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var node_name = str(params.get("node_name", "MultiMeshInstance3D"))
	var count = int(params.get("instance_count", 100))
	var min_s = float(params.get("min_scale", 0.8))
	var max_s = float(params.get("max_scale", 1.3))
	var random_yaw = bool(params.get("random_yaw", true))

	var area = params.get("area_size", [50.0, 50.0])
	var area_x = float(area[0]) if area is Array and area.size() > 0 else 50.0
	var area_z = float(area[1]) if area is Array and area.size() > 1 else 50.0

	var mesh_path = str(params.get("mesh_path", ""))
	var mesh_res: Mesh = null
	if mesh_path != "" and ResourceLoader.exists(mesh_path):
		mesh_res = ResourceLoader.load(mesh_path)
	if not mesh_res:
		var prism = PrismMesh.new()
		prism.size = Vector3(1.0, 2.0, 1.0)
		mesh_res = prism

	var mmi = MultiMeshInstance3D.new()
	mmi.name = node_name

	var mm = MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh_res
	mm.instance_count = count

	var rng = RandomNumberGenerator.new()
	rng.randomize()

	for i in range(count):
		var rx = rng.randf_range(-area_x * 0.5, area_x * 0.5)
		var rz = rng.randf_range(-area_z * 0.5, area_z * 0.5)
		var s = rng.randf_range(min_s, max_s)
		var yaw = rng.randf_range(0.0, TAU) if random_yaw else 0.0

		var t3d = Transform3D()
		t3d = t3d.rotated(Vector3.UP, yaw)
		t3d = t3d.scaled(Vector3(s, s, s))
		t3d.origin = Vector3(rx, 0.0, rz)
		mm.set_instance_transform(i, t3d)

	mmi.multimesh = mm
	parent_node.add_child(mmi)
	mmi.owner = root

	return {
		"success": true,
		"message": "Scattered %d GPU MultiMesh instances across area [%.1fm x %.1fm] under '%s'." % [count, area_x, area_z, parent_path],
		"data": {
			"node_name": mmi.name,
			"node_path": str(root.get_path_to(mmi)),
			"instance_count": count,
			"area_size": [area_x, area_z],
			"scale_range": [min_s, max_s],
			"mesh_path": mesh_path
		}
	}

func configure_lod_manager(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("node_path", "GeometryInstance3D"))
	var target_node = _find_node(node_path, root)
	if not (target_node is GeometryInstance3D):
		return {"success": false, "message": "Target node '%s' must be a GeometryInstance3D." % node_path}

	var geom: GeometryInstance3D = target_node
	var v_begin = float(params.get("visibility_range_begin", 0.0))
	var v_end = float(params.get("visibility_range_end", 150.0))
	var v_begin_m = float(params.get("visibility_range_begin_margin", 10.0))
	var v_end_m = float(params.get("visibility_range_end_margin", 10.0))
	var fade_mode = str(params.get("fade_mode", "self")).to_lower()

	geom.visibility_range_begin = v_begin
	geom.visibility_range_end = v_end
	geom.visibility_range_begin_margin = v_begin_m
	geom.visibility_range_end_margin = v_end_m

	match fade_mode:
		"disabled":
			geom.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
		"dependencies":
			geom.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DEPENDENCIES
		_:
			geom.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF

	return {
		"success": true,
		"message": "Configured LOD visibility range [%.1fm to %.1fm] for '%s'." % [v_begin, v_end, geom.name],
		"data": {
			"node_name": geom.name,
			"node_path": str(root.get_path_to(geom)),
			"visibility_range_begin": v_begin,
			"visibility_range_end": v_end,
			"visibility_range_begin_margin": v_begin_m,
			"visibility_range_end_margin": v_end_m,
			"fade_mode": fade_mode
		}
	}
