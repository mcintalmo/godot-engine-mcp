@tool
extends RefCounted

## Operations for Godot 2D and 3D Navigation Obstacles and dynamic RVO avoidance configuration.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func configure_navigation_obstacle(params: Dictionary) -> Dictionary:
	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var is_3d = bool(params.get("is_3d", true))
	var obstacle: Node = null
	var node_path = params.get("node_path")

	if node_path != null and str(node_path) != "":
		var target = root.get_node_or_null(str(node_path))
		if target is NavigationObstacle3D or target is NavigationObstacle2D:
			obstacle = target
		else:
			return {"success": false, "message": "Node at '%s' is not a NavigationObstacle." % str(node_path)}
	else:
		var parent: Node = root
		var p_path = params.get("parent_path")
		if p_path != null and str(p_path) != "":
			var found_p = root.get_node_or_null(str(p_path))
			if found_p:
				parent = found_p

		if is_3d:
			obstacle = NavigationObstacle3D.new()
		else:
			obstacle = NavigationObstacle2D.new()

		obstacle.name = params.get("node_name", "NavigationObstacle3D" if is_3d else "NavigationObstacle2D")
		parent.add_child(obstacle)
		obstacle.owner = root

	# Configure properties
	obstacle.radius = float(params.get("radius", 1.0))
	obstacle.avoidance_layers = int(params.get("avoidance_layers", 1))

	if "affect_navigation_mesh" in obstacle:
		obstacle.affect_navigation_mesh = bool(params.get("affect_navigation_mesh", false))
	if "carve_navigation_mesh" in obstacle:
		obstacle.carve_navigation_mesh = bool(params.get("carve_navigation_mesh", false))

	var raw_vel = params.get("velocity")
	if raw_vel != null and raw_vel is Array:
		if is_3d and raw_vel.size() == 3:
			obstacle.velocity = Vector3(float(raw_vel[0]), float(raw_vel[1]), float(raw_vel[2]))
		elif not is_3d and raw_vel.size() == 2:
			obstacle.velocity = Vector2(float(raw_vel[0]), float(raw_vel[1]))

	var raw_verts = params.get("vertices")
	if raw_verts != null and raw_verts is Array:
		if is_3d:
			var pts: PackedVector3Array = PackedVector3Array()
			for v in raw_verts:
				if v is Array and v.size() >= 2:
					var y_val = float(v[2]) if v.size() >= 3 else 0.0
					pts.append(Vector3(float(v[0]), y_val, float(v[1])))
			obstacle.vertices = pts
		else:
			var pts: PackedVector2Array = PackedVector2Array()
			for v in raw_verts:
				if v is Array and v.size() >= 2:
					pts.append(Vector2(float(v[0]), float(v[1])))
			obstacle.vertices = pts

	return {
		"success": true,
		"message": "Configured NavigationObstacle '%s' (3D: %s)." % [obstacle.name, str(is_3d)],
		"data": {
			"node_name": obstacle.name,
			"node_path": str(obstacle.get_path()),
			"is_3d": is_3d,
			"radius": obstacle.radius,
			"avoidance_layers": obstacle.avoidance_layers,
			"vertex_count": obstacle.vertices.size()
		}
	}
