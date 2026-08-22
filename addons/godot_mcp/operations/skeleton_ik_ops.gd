@tool
extends RefCounted

## Operations for Godot 3D Skeletons, Bone Attachments & Inverse Kinematics.

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

func inspect_skeleton(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var skel_path = str(params.get("skeleton_node_path", "Skeleton3D"))
	var skel_node = _find_node(skel_path, root)
	if not skel_node:
		return {"success": false, "message": "Skeleton node not found at '%s'." % skel_path}

	var bones = []

	if skel_node is Skeleton3D:
		var count = skel_node.get_bone_count()
		for i in range(count):
			var b_name = skel_node.get_bone_name(i)
			var p_idx = skel_node.get_bone_parent(i)
			var p_name = skel_node.get_bone_name(p_idx) if p_idx >= 0 else ""
			var rest_t = skel_node.get_bone_rest(i)
			var g_pose = skel_node.get_bone_global_pose(i)

			bones.append({
				"index": i,
				"name": b_name,
				"parent_index": p_idx,
				"parent_name": p_name,
				"rest_position": [rest_t.origin.x, rest_t.origin.y, rest_t.origin.z],
				"global_position": [g_pose.origin.x, g_pose.origin.y, g_pose.origin.z]
			})

		return {
			"success": true,
			"message": "Inspected Skeleton3D '%s' with %d bones." % [skel_node.name, bones.size()],
			"data": {
				"skeleton_name": skel_node.name,
				"skeleton_path": str(root.get_path_to(skel_node)),
				"skeleton_type": "Skeleton3D",
				"bone_count": bones.size(),
				"bones": bones
			}
		}

	elif skel_node is Skeleton2D:
		var count = skel_node.get_bone_count()
		for i in range(count):
			var b_node = skel_node.get_bone(i)
			if b_node:
				bones.append({
					"index": i,
					"name": b_node.name,
					"parent_index": b_node.get_index_in_skeleton(),
					"position": [b_node.position.x, b_node.position.y]
				})

		return {
			"success": true,
			"message": "Inspected Skeleton2D '%s' with %d bones." % [skel_node.name, bones.size()],
			"data": {
				"skeleton_name": skel_node.name,
				"skeleton_path": str(root.get_path_to(skel_node)),
				"skeleton_type": "Skeleton2D",
				"bone_count": bones.size(),
				"bones": bones
			}
		}

	return {"success": false, "message": "Node at '%s' is not a Skeleton3D or Skeleton2D." % skel_path}

func configure_bone_attachment(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var skel_path = str(params.get("skeleton_node_path", "Skeleton3D"))
	var skel_node = _find_node(skel_path, root)
	if not (skel_node is Skeleton3D):
		return {"success": false, "message": "Target skeleton at '%s' must be a Skeleton3D." % skel_path}

	var bone_name = str(params.get("bone_name", ""))
	var bone_idx = skel_node.find_bone(bone_name)
	if bone_idx < 0:
		return {"success": false, "message": "Bone '%s' not found in Skeleton3D '%s'." % [bone_name, skel_node.name]}

	var attach_name = str(params.get("attachment_node_name", "BoneAttachment3D"))
	var attach_node: BoneAttachment3D = null

	if skel_node.has_node(attach_name):
		var existing = skel_node.get_node(attach_name)
		if existing is BoneAttachment3D:
			attach_node = existing

	if not attach_node:
		attach_node = BoneAttachment3D.new()
		attach_node.name = attach_name
		skel_node.add_child(attach_node)
		attach_node.owner = root

	attach_node.bone_name = bone_name
	attach_node.bone_idx = bone_idx

	var pos = params.get("position_offset")
	if pos is Array and pos.size() >= 3:
		attach_node.position = Vector3(float(pos[0]), float(pos[1]), float(pos[2]))

	var rot = params.get("rotation_offset_deg")
	if rot is Array and rot.size() >= 3:
		attach_node.rotation_degrees = Vector3(float(rot[0]), float(rot[1]), float(rot[2]))

	var sc = params.get("scale_offset")
	if sc is Array and sc.size() >= 3:
		attach_node.scale = Vector3(float(sc[0]), float(sc[1]), float(sc[2]))

	return {
		"success": true,
		"message": "Configured BoneAttachment3D '%s' attached to bone '%s' on '%s'." % [attach_node.name, bone_name, skel_node.name],
		"data": {
			"attachment_name": attach_node.name,
			"attachment_path": str(root.get_path_to(attach_node)),
			"skeleton_name": skel_node.name,
			"bone_name": bone_name,
			"bone_index": bone_idx,
			"position_offset": [attach_node.position.x, attach_node.position.y, attach_node.position.z]
		}
	}

func setup_inverse_kinematics(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var skel_path = str(params.get("skeleton_node_path", "Skeleton3D"))
	var skel_node = _find_node(skel_path, root)
	if not (skel_node is Skeleton3D):
		return {"success": false, "message": "Target skeleton at '%s' must be a Skeleton3D." % skel_path}

	var root_bone = str(params.get("root_bone", ""))
	var tip_bone = str(params.get("tip_bone", ""))
	var ik_name = str(params.get("ik_node_name", "SkeletonIK3D"))

	var ik_node: SkeletonIK3D = null
	if skel_node.has_node(ik_name):
		var existing = skel_node.get_node(ik_name)
		if existing is SkeletonIK3D:
			ik_node = existing

	if not ik_node:
		ik_node = SkeletonIK3D.new()
		ik_node.name = ik_name
		skel_node.add_child(ik_node)
		ik_node.owner = root

	ik_node.root_bone = root_bone
	ik_node.tip_bone = tip_bone

	if params.has("target_node_path"):
		var tp = str(params["target_node_path"])
		if tp != "":
			ik_node.target_node = NodePath(tp)

	ik_node.interpolation = float(params.get("interpolation", 1.0))
	ik_node.max_iterations = int(params.get("max_iterations", 10))
	ik_node.min_distance = float(params.get("min_distance", 0.01))

	var use_mag = bool(params.get("use_magnet", false))
	ik_node.use_magnet = use_mag
	var mag_pos = params.get("magnet_position")
	if mag_pos is Array and mag_pos.size() >= 3:
		ik_node.magnet_position = Vector3(float(mag_pos[0]), float(mag_pos[1]), float(mag_pos[2]))

	return {
		"success": true,
		"message": "Configured SkeletonIK3D '%s' (Root: %s -> Tip: %s) on '%s'." % [ik_node.name, root_bone, tip_bone, skel_node.name],
		"data": {
			"ik_node_name": ik_node.name,
			"ik_node_path": str(root.get_path_to(ik_node)),
			"skeleton_name": skel_node.name,
			"root_bone": root_bone,
			"tip_bone": tip_bone,
			"interpolation": ik_node.interpolation,
			"use_magnet": use_mag
		}
	}
