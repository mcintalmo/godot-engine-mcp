@tool
extends RefCounted

## Operations for Godot VFX particle systems and ParticleProcessMaterial configuration.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func configure_particles(params: Dictionary) -> Dictionary:
	var target_node: Node = null
	var node_path: String = params.get("node_path", "")
	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()

	if node_path != "" and root:
		target_node = root.get_node_or_null(node_path)

	var ptype = str(params.get("particle_type", "gpu_3d")).to_lower()
	var created_new = false

	if not target_node and root:
		var parent: Node = root
		var parent_path = params.get("parent_path", "")
		if parent_path != "":
			var p = root.get_node_or_null(parent_path)
			if p: parent = p

		match ptype:
			"gpu_3d": target_node = GPUParticles3D.new()
			"cpu_3d": target_node = CPUParticles3D.new()
			"gpu_2d": target_node = GPUParticles2D.new()
			"cpu_2d": target_node = CPUParticles2D.new()
			_: target_node = GPUParticles3D.new()

		var nname = params.get("node_name", "")
		if nname != "":
			target_node.name = nname
		else:
			target_node.name = "Particles3D" if ptype.ends_with("3d") else "Particles2D"

		parent.add_child(target_node)
		target_node.owner = root
		created_new = true

	# Common node properties
	if target_node:
		if params.has("amount"): target_node.set("amount", int(params["amount"]))
		if params.has("lifetime"): target_node.set("lifetime", float(params["lifetime"]))
		if params.has("explosiveness"): target_node.set("explosiveness", float(params["explosiveness"]))
		if params.has("emitting"): target_node.set("emitting", bool(params["emitting"]))

	var mat: ParticleProcessMaterial = null
	if target_node and (target_node is GPUParticles3D or target_node is GPUParticles2D):
		if not target_node.process_material or not (target_node.process_material is ParticleProcessMaterial):
			target_node.process_material = ParticleProcessMaterial.new()
		mat = target_node.process_material as ParticleProcessMaterial
	else:
		mat = ParticleProcessMaterial.new()

	# Process Material Properties
	var eshape = str(params.get("emission_shape", "point")).to_lower()
	match eshape:
		"point": mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_POINT
		"sphere":
			mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
			if params.has("emission_sphere_radius"):
				mat.emission_sphere_radius = float(params["emission_sphere_radius"])
		"box":
			mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
			if params.has("emission_box_extents"):
				var ext = params["emission_box_extents"]
				mat.emission_box_extents = Vector3(float(ext[0]), float(ext[1]), float(ext[2]))
		"ring":
			mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_RING
			if params.has("emission_sphere_radius"):
				mat.emission_ring_radius = float(params["emission_sphere_radius"])

	if params.has("direction"):
		var d = params["direction"]
		mat.direction = Vector3(float(d[0]), float(d[1]), float(d[2]))
	if params.has("spread"):
		mat.spread = float(params["spread"])

	if params.has("initial_velocity_min"):
		mat.set_param_min(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY, float(params["initial_velocity_min"]))
	if params.has("initial_velocity_max"):
		mat.set_param_max(ParticleProcessMaterial.PARAM_INITIAL_LINEAR_VELOCITY, float(params["initial_velocity_max"]))

	if params.has("gravity"):
		var g = params["gravity"]
		mat.gravity = Vector3(float(g[0]), float(g[1]), float(g[2]))

	if params.has("scale_min"):
		mat.set_param_min(ParticleProcessMaterial.PARAM_SCALE, float(params["scale_min"]))
	if params.has("scale_max"):
		mat.set_param_max(ParticleProcessMaterial.PARAM_SCALE, float(params["scale_max"]))

	# Color ramp gradient
	if params.has("color_gradient") and params["color_gradient"] != null:
		var col_list: Array = params["color_gradient"]
		if col_list.size() > 0:
			var grad = Gradient.new()
			var p_colors: PackedColorArray = PackedColorArray()
			var p_offsets: PackedFloat32Array = PackedFloat32Array()
			for i in range(col_list.size()):
				p_colors.append(Color.from_string(str(col_list[i]), Color.WHITE))
				p_offsets.append(float(i) / max(1.0, float(col_list.size() - 1)))
			grad.colors = p_colors
			grad.offsets = p_offsets
			var grad_tex = GradientTexture1D.new()
			grad_tex.gradient = grad
			mat.color_ramp = grad_tex

	var save_path: String = params.get("save_path", "")
	if save_path != "":
		ResourceSaver.save(mat, save_path)

	return {
		"success": true,
		"message": "Configured particle system%s (Type: %s, Emission: %s)." % [
			" '" + target_node.name + "'" if target_node else "",
			ptype,
			eshape
		],
		"data": {
			"node_name": target_node.name if target_node else null,
			"node_path": str(target_node.get_path()) if target_node else null,
			"particle_type": ptype,
			"emission_shape": eshape,
			"created_new_node": created_new,
			"saved_material_path": save_path if save_path != "" else null
		}
	}
