@tool
extends RefCounted

## Operations for Godot Physics Joints, Constraints & Ragdoll Simulation.

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

func configure_physics_joint(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var joint_type = str(params.get("joint_type", "hinge_3d")).to_lower()
	var node_name = str(params.get("node_name", "PhysicsJoint"))
	var node_a = str(params.get("node_a_path", ""))
	var node_b = str(params.get("node_b_path", ""))

	var joint_node: Node = null

	match joint_type:
		"pin_3d":
			joint_node = PinJoint3D.new()
		"hinge_3d":
			joint_node = HingeJoint3D.new()
		"slider_3d":
			joint_node = SliderJoint3D.new()
		"cone_twist_3d":
			joint_node = ConeTwistJoint3D.new()
		"generic_6dof_3d":
			joint_node = Generic6DOFJoint3D.new()
		"pin_2d":
			joint_node = PinJoint2D.new()
		"groove_2d":
			joint_node = GrooveJoint2D.new()
		"damped_spring_2d":
			joint_node = DampedSpringJoint2D.new()
		_:
			joint_node = HingeJoint3D.new()

	joint_node.name = node_name

	# Wire node paths
	if node_a != "":
		joint_node.set("node_a", NodePath(node_a))
	if node_b != "":
		joint_node.set("node_b", NodePath(node_b))

	# Position & Rotation
	var pos = params.get("position")
	if pos is Array:
		if joint_node is Node3D and pos.size() >= 3:
			joint_node.position = Vector3(float(pos[0]), float(pos[1]), float(pos[2]))
		elif joint_node is Node2D and pos.size() >= 2:
			joint_node.position = Vector2(float(pos[0]), float(pos[1]))

	var rot = params.get("rotation_deg")
	if rot is Array:
		if joint_node is Node3D and rot.size() >= 3:
			joint_node.rotation_degrees = Vector3(float(rot[0]), float(rot[1]), float(rot[2]))
		elif joint_node is Node2D and rot.size() >= 1:
			joint_node.rotation_degrees = float(rot[0])

	# Apply custom parameters
	var custom_params = params.get("parameters")
	var applied_params = []
	if custom_params is Dictionary:
		for k in custom_params.keys():
			var val = custom_params[k]
			joint_node.set(str(k), val)
			applied_params.append(str(k))

	parent_node.add_child(joint_node)
	joint_node.owner = root

	return {
		"success": true,
		"message": "Configured physics joint '%s' (%s) connecting '%s' and '%s'." % [joint_node.name, joint_type.to_upper(), node_a, node_b],
		"data": {
			"joint_name": joint_node.name,
			"joint_path": str(root.get_path_to(joint_node)),
			"joint_type": joint_type,
			"node_a": node_a,
			"node_b": node_b,
			"applied_parameters": applied_params
		}
	}

func generate_ragdoll(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var skel_path = str(params.get("skeleton_node_path", "Skeleton3D"))
	var skel_node = _find_node(skel_path, root)
	if not (skel_node is Skeleton3D):
		return {"success": false, "message": "Target skeleton at '%s' must be a Skeleton3D." % skel_path}

	var shape_type = str(params.get("shape_type", "capsule")).to_lower()
	var mass_val = float(params.get("mass_per_bone", 5.0))
	var friction_val = float(params.get("friction", 0.5))
	var bounce_val = float(params.get("bounce", 0.0))

	var req_bones = params.get("bone_names")
	var target_bone_names = []
	if req_bones is Array and req_bones.size() > 0:
		for b in req_bones:
			target_bone_names.append(str(b))
	else:
		# Auto-discover all bones
		for i in range(skel_node.get_bone_count()):
			target_bone_names.append(skel_node.get_bone_name(i))

	var created_bones = []
	for b_name in target_bone_names:
		var b_idx = skel_node.find_bone(b_name)
		if b_idx < 0:
			continue

		var pb = PhysicalBone3D.new()
		pb.name = "PhysicalBone_" + b_name.replace(".", "_")
		pb.bone_name = b_name
		pb.mass = mass_val
		pb.friction = friction_val
		pb.bounce = bounce_val

		var cs = CollisionShape3D.new()
		cs.name = "CollisionShape3D"

		match shape_type:
			"box":
				var box = BoxShape3D.new()
				box.size = Vector3(0.2, 0.4, 0.2)
				cs.shape = box
			"sphere":
				var sph = SphereShape3D.new()
				sph.radius = 0.15
				cs.shape = sph
			_:
				var cap = CapsuleShape3D.new()
				cap.radius = 0.1
				cap.height = 0.35
				cs.shape = cap

		pb.add_child(cs)
		skel_node.add_child(pb)
		pb.owner = root
		cs.owner = root

		created_bones.append(pb.name)

	return {
		"success": true,
		"message": "Generated ragdoll with %d PhysicalBone3D nodes on Skeleton3D '%s'." % [created_bones.size(), skel_node.name],
		"data": {
			"skeleton_name": skel_node.name,
			"skeleton_path": str(root.get_path_to(skel_node)),
			"physical_bones_count": created_bones.size(),
			"physical_bones": created_bones,
			"shape_type": shape_type,
			"mass_per_bone": mass_val
		}
	}
