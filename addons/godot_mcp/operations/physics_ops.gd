@tool
extends RefCounted

## Operations for Godot 3D Physics geometric queries, raycasts, shape sweeps, and body telemetry.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func _get_space_state() -> PhysicsDirectSpaceState3D:
	if not _plugin:
		return null
	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if edited_root and edited_root is Node3D and edited_root.get_world_3d():
		return edited_root.get_world_3d().direct_space_state
	# Fallback to editor main viewport world
	var vp = _plugin.get_tree().root
	if vp and vp.get_world_3d():
		return vp.get_world_3d().direct_space_state
	return null

func cast_ray_3d(params: Dictionary) -> Dictionary:
	var space_state = _get_space_state()
	if not space_state:
		return {"success": false, "message": "No active 3D world physics space found in edited scene."}

	var from_arr = params.get("from_pos", [0.0, 0.0, 0.0])
	var to_arr = params.get("to_pos", [0.0, -10.0, 0.0])
	var from_pos = Vector3(float(from_arr[0]), float(from_arr[1]), float(from_arr[2]))
	var to_pos = Vector3(float(to_arr[0]), float(to_arr[1]), float(to_arr[2]))

	var mask: int = int(params.get("collision_mask", 4294967295))
	var collide_bodies: bool = bool(params.get("collide_with_bodies", true))
	var collide_areas: bool = bool(params.get("collide_with_areas", false))
	var hit_inside: bool = bool(params.get("hit_from_inside", false))

	var exclude_rids: Array[RID] = []
	var exclude_names: Array = params.get("exclude_nodes", [])
	if _plugin and exclude_names.size() > 0:
		var root = _plugin.get_editor_interface().get_edited_scene_root()
		if root:
			for node_name in exclude_names:
				var target_node = root.get_node_or_null(str(node_name))
				if target_node and target_node is CollisionObject3D:
					exclude_rids.append(target_node.get_rid())

	var query = PhysicsRayQueryParameters3D.create(from_pos, to_pos, mask, exclude_rids)
	query.collide_with_bodies = collide_bodies
	query.collide_with_areas = collide_areas
	query.hit_from_inside = hit_inside

	var result = space_state.intersect_ray(query)

	if result.is_empty():
		return {
			"success": true,
			"message": "Raycast from %s to %s did not intersect any colliders." % [str(from_pos), str(to_pos)],
			"data": {
				"has_hit": false,
				"from_pos": [from_pos.x, from_pos.y, from_pos.z],
				"to_pos": [to_pos.x, to_pos.y, to_pos.z],
				"ray_length": from_pos.distance_to(to_pos)
			}
		}

	var hit_pos: Vector3 = result.get("position", Vector3.ZERO)
	var hit_norm: Vector3 = result.get("normal", Vector3.UP)
	var collider = result.get("collider")
	var collider_name = collider.name if collider else "Unknown"
	var collider_path = str(collider.get_path()) if collider and collider is Node else ""
	var collider_class = collider.get_class() if collider else ""
	var shape_idx: int = int(result.get("shape", 0))
	var dist: float = from_pos.distance_to(hit_pos)

	return {
		"success": true,
		"message": "Raycast HIT '%s' at %s (Distance: %.2fm)." % [collider_name, str(hit_pos), dist],
		"data": {
			"has_hit": true,
			"hit_position": [round(hit_pos.x * 1000.0) / 1000.0, round(hit_pos.y * 1000.0) / 1000.0, round(hit_pos.z * 1000.0) / 1000.0],
			"hit_normal": [round(hit_norm.x * 1000.0) / 1000.0, round(hit_norm.y * 1000.0) / 1000.0, round(hit_norm.z * 1000.0) / 1000.0],
			"distance": round(dist * 1000.0) / 1000.0,
			"collider_name": collider_name,
			"collider_path": collider_path,
			"collider_class": collider_class,
			"shape_index": shape_idx,
			"from_pos": [from_pos.x, from_pos.y, from_pos.z],
			"to_pos": [to_pos.x, to_pos.y, to_pos.z]
		}
	}

func cast_shape_3d(params: Dictionary) -> Dictionary:
	var space_state = _get_space_state()
	if not space_state:
		return {"success": false, "message": "No active 3D world physics space found in edited scene."}

	var shape_type: String = params.get("shape_type", "sphere").to_lower()
	var shape_params: Dictionary = params.get("shape_params", {})
	var shape_res: Shape3D = null

	match shape_type:
		"sphere":
			var sphere = SphereShape3D.new()
			sphere.radius = float(shape_params.get("radius", 0.5))
			shape_res = sphere
		"box":
			var box = BoxShape3D.new()
			var sx = float(shape_params.get("size_x", shape_params.get("x", 1.0)))
			var sy = float(shape_params.get("size_y", shape_params.get("y", 1.0)))
			var sz = float(shape_params.get("size_z", shape_params.get("z", 1.0)))
			box.size = Vector3(sx, sy, sz)
			shape_res = box
		"capsule":
			var capsule = CapsuleShape3D.new()
			capsule.radius = float(shape_params.get("radius", 0.5))
			capsule.height = float(shape_params.get("height", 2.0))
			shape_res = capsule
		"cylinder":
			var cylinder = CylinderShape3D.new()
			cylinder.radius = float(shape_params.get("radius", 0.5))
			cylinder.height = float(shape_params.get("height", 2.0))
			shape_res = cylinder
		_:
			return {"success": false, "message": "Unsupported shape type: '%s'." % shape_type}

	var origin_arr = params.get("origin", [0.0, 0.0, 0.0])
	var origin_vec = Vector3(float(origin_arr[0]), float(origin_arr[1]), float(origin_arr[2]))
	var mask: int = int(params.get("collision_mask", 4294967295))
	var max_results: int = int(params.get("max_results", 32))

	var shape_query = PhysicsShapeQueryParameters3D.new()
	shape_query.shape_rid = shape_res.get_rid()
	shape_query.transform = Transform3D(Basis(), origin_vec)
	shape_query.collision_mask = mask

	var motion_arr = params.get("motion")
	var motion_res = null
	if motion_arr != null and motion_arr is Array and motion_arr.size() >= 3:
		var motion_vec = Vector3(float(motion_arr[0]), float(motion_arr[1]), float(motion_arr[2]))
		shape_query.motion = motion_vec
		var cast_fractions = space_state.cast_motion(shape_query)
		motion_res = {
			"safe_fraction": cast_fractions[0] if cast_fractions.size() > 0 else 1.0,
			"unsafe_fraction": cast_fractions[1] if cast_fractions.size() > 1 else 1.0
		}

	var overlaps = space_state.intersect_shape(shape_query, max_results)
	var overlap_list: Array = []

	for item in overlaps:
		var col = item.get("collider")
		var col_name = col.name if col else "Unknown"
		var col_path = str(col.get_path()) if col and col is Node else ""
		var col_class = col.get_class() if col else ""
		overlap_list.append({
			"collider_name": col_name,
			"collider_path": col_path,
			"collider_class": col_class,
			"shape_index": int(item.get("shape", 0))
		})

	return {
		"success": true,
		"message": "Shape cast (%s) found %d overlapping colliders." % [shape_type, overlap_list.size()],
		"data": {
			"shape_type": shape_type,
			"origin": [origin_vec.x, origin_vec.y, origin_vec.z],
			"overlap_count": overlap_list.size(),
			"overlaps": overlap_list,
			"motion_cast": motion_res
		}
	}

func get_body_physics_state_3d(params: Dictionary) -> Dictionary:
	var node_path = params.get("node_path", "")
	if not _plugin:
		return {"success": false, "message": "EditorPlugin not initialized."}

	var root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var target = root.get_node_or_null(node_path)
	if not target:
		return {"success": false, "message": "Node not found at path '%s'." % node_path}

	if not (target is CollisionObject3D):
		return {"success": false, "message": "Node '%s' is of class '%s', which is not a CollisionObject3D." % [node_path, target.get_class()]}

	var rid = target.get_rid()
	var direct_state = PhysicsServer3D.body_get_direct_state(rid)

	var lin_vel = Vector3.ZERO
	var ang_vel = Vector3.ZERO
	var mass = 1.0
	var inv_mass = 1.0
	var is_sleeping = false
	var center_mass = Vector3.ZERO
	var total_grav = Vector3.ZERO
	var contacts: Array = []

	if direct_state:
		lin_vel = direct_state.linear_velocity
		ang_vel = direct_state.angular_velocity
		inv_mass = direct_state.inverse_mass
		mass = 1.0 / inv_mass if inv_mass > 0.0 else 0.0
		is_sleeping = direct_state.sleeping
		center_mass = direct_state.center_of_mass
		total_grav = direct_state.total_gravity

		var contact_count = direct_state.get_contact_count()
		for i in range(contact_count):
			var c_pos = direct_state.get_contact_local_position(i)
			var c_norm = direct_state.get_contact_local_normal(i)
			var c_imp = direct_state.get_contact_impulse(i)
			contacts.append({
				"index": i,
				"position": [c_pos.x, c_pos.y, c_pos.z],
				"normal": [c_norm.x, c_norm.y, c_norm.z],
				"impulse": [c_imp.x, c_imp.y, c_imp.z]
			})
	elif target is RigidBody3D:
		lin_vel = target.linear_velocity
		ang_vel = target.angular_velocity
		mass = target.mass
		is_sleeping = target.sleeping
		center_mass = target.center_of_mass

	return {
		"success": true,
		"message": "Physics state for '%s' (%s)." % [target.name, target.get_class()],
		"data": {
			"node_name": target.name,
			"node_path": str(target.get_path()),
			"class": target.get_class(),
			"collision_layer": target.collision_layer,
			"collision_mask": target.collision_mask,
			"linear_velocity": [round(lin_vel.x * 100.0) / 100.0, round(lin_vel.y * 100.0) / 100.0, round(lin_vel.z * 100.0) / 100.0],
			"angular_velocity": [round(ang_vel.x * 100.0) / 100.0, round(ang_vel.y * 100.0) / 100.0, round(ang_vel.z * 100.0) / 100.0],
			"mass": round(mass * 100.0) / 100.0,
			"is_sleeping": is_sleeping,
			"center_of_mass": [center_mass.x, center_mass.y, center_mass.z],
			"total_gravity": [total_grav.x, total_grav.y, total_grav.z],
			"contact_count": contacts.size(),
			"contacts": contacts
		}
	}

func set_physics_debug_mode(params: Dictionary) -> Dictionary:
	var applied: Array[String] = []

	if params.has("visible_collision_shapes") and params["visible_collision_shapes"] != null and _plugin:
		var val = bool(params["visible_collision_shapes"])
		_plugin.get_tree().debug_collisions_hint = val
		applied.append("visible_collision_shapes = %s" % ("true" if val else "false"))

	if params.has("visible_paths") and params["visible_paths"] != null and _plugin:
		var val = bool(params["visible_paths"])
		_plugin.get_tree().debug_paths_hint = val
		applied.append("visible_paths = %s" % ("true" if val else "false"))

	if params.has("visible_navigation") and params["visible_navigation"] != null and _plugin:
		var val = bool(params["visible_navigation"])
		_plugin.get_tree().debug_navigation_hint = val
		applied.append("visible_navigation = %s" % ("true" if val else "false"))

	return {
		"success": true,
		"message": "Updated physics debug visualization (%s)." % (", ".join(applied) if applied.size() > 0 else "no changes"),
		"data": {
			"visible_collision_shapes": _plugin.get_tree().debug_collisions_hint if _plugin else false,
			"visible_paths": _plugin.get_tree().debug_paths_hint if _plugin else false,
			"visible_navigation": _plugin.get_tree().debug_navigation_hint if _plugin else false
		}
	}
