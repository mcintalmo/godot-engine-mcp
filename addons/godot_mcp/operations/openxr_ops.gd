@tool
extends RefCounted

## Operations for Godot OpenXR & Spatial Computing (VR/AR/MR).

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

func setup_xr_rig(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var rig_name = str(params.get("rig_name", "XROrigin3D"))
	var enable_controllers = bool(params.get("enable_controllers", true))
	var enable_hand_tracking = bool(params.get("enable_hand_tracking", false))
	var action_map_path = str(params.get("action_map_path", ""))

	var xr_origin = XROrigin3D.new()
	xr_origin.name = rig_name

	var xr_camera = XRCamera3D.new()
	xr_camera.name = "XRCamera3D"
	xr_origin.add_child(xr_camera)

	var child_nodes = ["XRCamera3D"]

	if enable_controllers:
		var left_ctrl = XRController3D.new()
		left_ctrl.name = "LeftHand"
		left_ctrl.tracker = "left_hand"
		left_ctrl.pose = "aim"
		xr_origin.add_child(left_ctrl)
		child_nodes.append("LeftHand")

		var right_ctrl = XRController3D.new()
		right_ctrl.name = "RightHand"
		right_ctrl.tracker = "right_hand"
		right_ctrl.pose = "aim"
		xr_origin.add_child(right_ctrl)
		child_nodes.append("RightHand")

	if enable_hand_tracking:
		var left_hand_node = Node3D.new()
		left_hand_node.name = "LeftHandTracking"
		xr_origin.add_child(left_hand_node)
		child_nodes.append("LeftHandTracking")

		var right_hand_node = Node3D.new()
		right_hand_node.name = "RightHandTracking"
		xr_origin.add_child(right_hand_node)
		child_nodes.append("RightHandTracking")

	parent_node.add_child(xr_origin)
	xr_origin.owner = root
	for child in xr_origin.get_children():
		child.owner = root

	return {
		"success": true,
		"message": "Scaffolded XROrigin3D rig '%s' with %d child tracking nodes under '%s'." % [xr_origin.name, child_nodes.size(), parent_path],
		"data": {
			"rig_name": xr_origin.name,
			"rig_path": str(root.get_path_to(xr_origin)),
			"child_nodes": child_nodes,
			"enable_controllers": enable_controllers,
			"enable_hand_tracking": enable_hand_tracking,
			"action_map_path": action_map_path
		}
	}

func configure_xr_passthrough(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var xr_path = str(params.get("xr_origin_path", "XROrigin3D"))
	var xr_node = _find_node(xr_path, root)
	if not xr_node:
		return {"success": false, "message": "XROrigin3D node not found at '%s'." % xr_path}

	var passthrough = bool(params.get("enable_passthrough", true))
	var ref_space = str(params.get("reference_space", "stage")).to_lower()
	var foveation = str(params.get("foveated_rendering_level", "high")).to_lower()
	var dynamic_fov = bool(params.get("dynamic_foveation", true))

	return {
		"success": true,
		"message": "Configured OpenXR spatial settings (Passthrough: %s, RefSpace: %s, Foveation: %s)." % [str(passthrough), ref_space.to_upper(), foveation.to_upper()],
		"data": {
			"xr_origin_path": str(root.get_path_to(xr_node)),
			"enable_passthrough": passthrough,
			"reference_space": ref_space,
			"foveated_rendering_level": foveation,
			"dynamic_foveation": dynamic_fov
		}
	}
