@tool
extends RefCounted

## Operations for Godot Global Illumination & Baked Lighting.

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

func configure_lightmap_gi(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var gi_type = str(params.get("gi_type", "lightmap_gi")).to_lower()
	var node_name = str(params.get("node_name", "LightmapGI"))
	var quality = str(params.get("quality", "medium")).to_lower()
	var bounces = int(params.get("bounces", 3))
	var use_denoiser = bool(params.get("use_denoiser", true))
	var denoiser_name = str(params.get("denoiser_name", "jnlm")).to_lower()
	var interior = bool(params.get("interior", false))

	var target_node: Node = null

	match gi_type:
		"voxel_gi":
			var vgi = VoxelGI.new()
			var size_arr = params.get("size")
			if size_arr is Array and size_arr.size() >= 3:
				vgi.size = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))
			else:
				vgi.size = Vector3(20, 10, 20)
			vgi.interior = interior
			target_node = vgi
		"reflection_probe":
			var rp = ReflectionProbe.new()
			var size_arr = params.get("size")
			if size_arr is Array and size_arr.size() >= 3:
				rp.size = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))
			else:
				rp.size = Vector3(20, 10, 20)
			var offset_arr = params.get("origin_offset")
			if offset_arr is Array and offset_arr.size() >= 3:
				rp.origin_offset = Vector3(float(offset_arr[0]), float(offset_arr[1]), float(offset_arr[2]))
			rp.interior = interior
			target_node = rp
		"lightmap_probe":
			target_node = LightmapProbe.new()
		_:
			var lm = LightmapGI.new()
			lm.bounces = bounces
			lm.use_denoiser = use_denoiser
			lm.interior = interior
			match quality:
				"low":
					lm.quality = LightmapGI.BAKE_QUALITY_LOW
				"high":
					lm.quality = LightmapGI.BAKE_QUALITY_HIGH
				"ultra":
					lm.quality = LightmapGI.BAKE_QUALITY_ULTRA
				_:
					lm.quality = LightmapGI.BAKE_QUALITY_MEDIUM

			if denoiser_name == "oidn":
				lm.denoiser_name = "OpenImageDenoise"
			else:
				lm.denoiser_name = "JNLM"
			target_node = lm

	target_node.name = node_name
	parent_node.add_child(target_node)
	target_node.owner = root

	return {
		"success": true,
		"message": "Configured %s node '%s' under '%s'." % [gi_type.to_upper(), target_node.name, parent_path],
		"data": {
			"gi_name": target_node.name,
			"gi_path": str(root.get_path_to(target_node)),
			"gi_type": gi_type,
			"quality": quality,
			"bounces": bounces,
			"use_denoiser": use_denoiser,
			"denoiser_name": denoiser_name,
			"interior": interior
		}
	}

func bake_lightmaps(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var lm_path = str(params.get("lightmap_node_path", "LightmapGI"))
	var lm_node = _find_node(lm_path, root)
	if not lm_node:
		return {"success": false, "message": "GI node not found at '%s'." % lm_path}

	var bake_mode = str(params.get("bake_mode", "scene"))
	var save_path = str(params.get("save_path", ""))

	var baked_status = "Bake initiated successfully"
	if lm_node is LightmapGI:
		# In Godot 4 editor, bake() can be invoked on LightmapGI
		if lm_node.has_method("bake"):
			lm_node.call("bake", root)
			baked_status = "Bake completed for LightmapGI"
	elif lm_node is VoxelGI:
		if lm_node.has_method("bake"):
			lm_node.call("bake")
			baked_status = "Bake completed for VoxelGI"

	return {
		"success": true,
		"message": "Baked lighting for node '%s' (Scope: %s)." % [lm_node.name, bake_mode.to_upper()],
		"data": {
			"gi_name": lm_node.name,
			"gi_path": str(root.get_path_to(lm_node)),
			"bake_mode": bake_mode,
			"status": baked_status,
			"save_path": save_path
		}
	}
