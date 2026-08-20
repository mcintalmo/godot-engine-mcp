@tool
extends RefCounted

## Operations for DCC / Blender 3D asset import, GLTF configuration, and model instancing.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func instantiate_model(params: Dictionary) -> Dictionary:
	var source_path: String = params.get("source_path", "")
	if source_path == "":
		return {"success": false, "message": "source_path cannot be empty."}

	if not ResourceLoader.exists(source_path):
		return {"success": false, "message": "Asset does not exist at '%s'." % source_path}

	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var parent_node: Node = root
	var parent_path: String = params.get("parent_path", "")
	if parent_path != "":
		var p = root.get_node_or_null(parent_path)
		if p:
			parent_node = p

	var loaded_res = load(source_path)
	var instance: Node = null

	if loaded_res is PackedScene:
		instance = loaded_res.instantiate()
	else:
		return {"success": false, "message": "Resource at '%s' is not a PackedScene or importable 3D scene." % source_path}

	if not instance:
		return {"success": false, "message": "Failed to instantiate model from '%s'." % source_path}

	var custom_name: String = params.get("node_name", "")
	if custom_name != "":
		instance.name = custom_name

	# Transforms
	if instance is Node3D:
		var n3d = instance as Node3D
		if params.has("position") and params["position"] != null:
			var pos_arr = params["position"]
			n3d.position = Vector3(float(pos_arr[0]), float(pos_arr[1]), float(pos_arr[2]))
		if params.has("rotation") and params["rotation"] != null:
			var rot_arr = params["rotation"]
			n3d.rotation_degrees = Vector3(float(rot_arr[0]), float(rot_arr[1]), float(rot_arr[2]))
		if params.has("scale") and params["scale"] != null:
			var sc_arr = params["scale"]
			n3d.scale = Vector3(float(sc_arr[0]), float(sc_arr[1]), float(sc_arr[2]))

	# Collision Generation
	var col_mode = str(params.get("collision_mode", "none")).to_lower()
	var colliders_generated: int = 0
	if col_mode != "none" and instance is Node3D:
		colliders_generated = _create_collisions_recursive(instance, col_mode, root)

	parent_node.add_child(instance)
	_set_owner_recursive(instance, root)

	# Optional scene saving
	var save_scene_path: String = params.get("save_as_scene_path", "")
	if save_scene_path != "":
		var ps = PackedScene.new()
		ps.pack(instance)
		ResourceSaver.save(ps, save_scene_path)

	return {
		"success": true,
		"message": "Instantiated model '%s' under '%s' (Colliders: %d)." % [instance.name, parent_node.name, colliders_generated],
		"data": {
			"node_name": instance.name,
			"node_path": str(instance.get_path()),
			"node_class": instance.get_class(),
			"source_path": source_path,
			"colliders_generated": colliders_generated,
			"saved_scene_path": save_scene_path if save_scene_path != "" else null
		}
	}

func configure_gltf_import(params: Dictionary) -> Dictionary:
	var model_path: String = params.get("model_path", "")
	if model_path == "":
		return {"success": false, "message": "model_path cannot be empty."}

	var import_path = model_path + ".import"
	var config = ConfigFile.new()
	var err = config.load(import_path)
	if err != OK:
		return {"success": false, "message": "Failed to load .import file for '%s' (Error: %d)." % [model_path, err]}

	var changes: Dictionary = {}
	if params.has("import_as_skeleton_bones") and params["import_as_skeleton_bones"] != null:
		config.set_value("params", "import_as_skeleton_bones", bool(params["import_as_skeleton_bones"]))
		changes["import_as_skeleton_bones"] = bool(params["import_as_skeleton_bones"])

	if params.has("generate_lods") and params["generate_lods"] != null:
		config.set_value("params", "nodes/generate_lods", bool(params["generate_lods"]))
		changes["generate_lods"] = bool(params["generate_lods"])

	if params.has("lod_threshold") and params["lod_threshold"] != null:
		config.set_value("params", "nodes/mesh_lod_threshold", float(params["lod_threshold"]))
		changes["lod_threshold"] = float(params["lod_threshold"])

	if params.has("generate_shadow_mesh") and params["generate_shadow_mesh"] != null:
		config.set_value("params", "nodes/shadow_mesh", bool(params["generate_shadow_mesh"]))
		changes["generate_shadow_mesh"] = bool(params["generate_shadow_mesh"])

	if params.has("extract_materials") and params["extract_materials"] != null:
		config.set_value("params", "materials/extract_materials", bool(params["extract_materials"]))
		changes["extract_materials"] = bool(params["extract_materials"])

	config.save(import_path)

	var reimport = bool(params.get("reimport", true))
	if reimport and _plugin:
		_plugin.get_editor_interface().get_resource_filesystem().reimport_files(PackedStringArray([model_path]))

	return {
		"success": true,
		"message": "Configured import settings for '%s' (%d params updated)." % [model_path, changes.size()],
		"data": {
			"model_path": model_path,
			"settings_updated": changes,
			"reimported": reimport
		}
	}

func _create_collisions_recursive(node: Node, mode: String, scene_root: Node) -> int:
	var count = 0
	if node is MeshInstance3D and node.mesh:
		var mi = node as MeshInstance3D
		var static_body = StaticBody3D.new()
		static_body.name = mi.name + "_Col"
		var col_shape = CollisionShape3D.new()

		match mode:
			"trimesh":
				col_shape.shape = mi.mesh.create_trimesh_shape()
			"convex":
				col_shape.shape = mi.mesh.create_convex_shape()
			"box":
				var box = BoxShape3D.new()
				var aabb = mi.mesh.get_aabb()
				box.size = aabb.size
				col_shape.shape = box
				col_shape.position = aabb.position + aabb.size * 0.5
			_:
				col_shape.shape = mi.mesh.create_convex_shape()

		if col_shape.shape:
			static_body.add_child(col_shape)
			mi.add_child(static_body)
			_set_owner_recursive(static_body, scene_root)
			count += 1

	for c in node.get_children():
		count += _create_collisions_recursive(c, mode, scene_root)
	return count

func _set_owner_recursive(node: Node, target_owner: Node) -> void:
	if node != target_owner:
		node.owner = target_owner
	for child in node.get_children():
		_set_owner_recursive(child, target_owner)
