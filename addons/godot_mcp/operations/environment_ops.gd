@tool
extends RefCounted

## Operations for Godot Environment post-processing, Sky generators, and WorldEnvironment node configuration.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func configure_environment(params: Dictionary) -> Dictionary:
	var target_env: Environment = null
	var target_node: WorldEnvironment = null
	var node_path: String = params.get("node_path", "")

	if node_path != "" and _plugin:
		var root = _plugin.get_editor_interface().get_edited_scene_root()
		if root:
			var n = root.get_node_or_null(node_path)
			if n and n is WorldEnvironment:
				target_node = n
				if not target_node.environment:
					target_node.environment = Environment.new()
				target_env = target_node.environment

	if not target_env:
		target_env = Environment.new()

	var applied_props: Dictionary = {}

	# 1. Background Mode
	if params.has("background_mode") and params["background_mode"] != null:
		var bg_mode_str = str(params["background_mode"]).to_lower()
		match bg_mode_str:
			"clear_color": target_env.background_mode = Environment.BG_CLEAR_COLOR
			"custom_color", "color": target_env.background_mode = Environment.BG_COLOR
			"sky": target_env.background_mode = Environment.BG_SKY
			"canvas": target_env.background_mode = Environment.BG_CANVAS
			"keep": target_env.background_mode = Environment.BG_KEEP
		applied_props["background_mode"] = bg_mode_str

	if params.has("background_color") and params["background_color"] != null:
		var col = Color.from_string(str(params["background_color"]), Color.BLACK)
		target_env.background_color = col
		applied_props["background_color"] = str(col)

	# 2. Sky Generator
	if params.has("sky_type") and params["sky_type"] != null:
		var stype = str(params["sky_type"]).to_lower()
		var sky = Sky.new()
		var sparams: Dictionary = params.get("sky_params", {})

		match stype:
			"procedural":
				var psky = ProceduralSkyMaterial.new()
				if sparams.has("sky_top_color"): psky.sky_top_color = Color.from_string(str(sparams["sky_top_color"]), psky.sky_top_color)
				if sparams.has("sky_horizon_color"): psky.sky_horizon_color = Color.from_string(str(sparams["sky_horizon_color"]), psky.sky_horizon_color)
				if sparams.has("ground_bottom_color"): psky.ground_bottom_color = Color.from_string(str(sparams["ground_bottom_color"]), psky.ground_bottom_color)
				if sparams.has("ground_horizon_color"): psky.ground_horizon_color = Color.from_string(str(sparams["ground_horizon_color"]), psky.ground_horizon_color)
				if sparams.has("sun_angle_max"): psky.sun_angle_max = float(sparams["sun_angle_max"])
				sky.sky_material = psky
			"physical":
				var phys = PhysicalSkyMaterial.new()
				if sparams.has("rayleigh_coefficient"): phys.rayleigh_coefficient = float(sparams["rayleigh_coefficient"])
				if sparams.has("mie_coefficient"): phys.mie_coefficient = float(sparams["mie_coefficient"])
				if sparams.has("turbidity"): phys.turbidity = float(sparams["turbidity"])
				sky.sky_material = phys
			"panorama":
				var pano = PanoramaSkyMaterial.new()
				if sparams.has("panorama_path") and ResourceLoader.exists(str(sparams["panorama_path"])):
					pano.panorama = load(str(sparams["panorama_path"]))
				sky.sky_material = pano

		target_env.sky = sky
		applied_props["sky_type"] = stype

	# 3. Tonemap
	if params.has("tonemap_mode") and params["tonemap_mode"] != null:
		var tm = str(params["tonemap_mode"]).to_lower()
		match tm:
			"linear": target_env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
			"reinhardt": target_env.tonemap_mode = Environment.TONE_MAPPER_REINHARDT
			"filmic": target_env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
			"aces": target_env.tonemap_mode = Environment.TONE_MAPPER_ACES
		applied_props["tonemap_mode"] = tm

	if params.has("tonemap_exposure") and params["tonemap_exposure"] != null:
		target_env.tonemap_exposure = float(params["tonemap_exposure"])
		applied_props["tonemap_exposure"] = target_env.tonemap_exposure

	# 4. Glow / Bloom
	if params.has("glow_enabled") and params["glow_enabled"] != null:
		target_env.glow_enabled = bool(params["glow_enabled"])
		applied_props["glow_enabled"] = target_env.glow_enabled

	if params.has("glow_intensity") and params["glow_intensity"] != null:
		target_env.glow_intensity = float(params["glow_intensity"])
		applied_props["glow_intensity"] = target_env.glow_intensity

	if params.has("glow_bloom") and params["glow_bloom"] != null:
		target_env.glow_bloom = float(params["glow_bloom"])
		applied_props["glow_bloom"] = target_env.glow_bloom

	# 5. SSAO / SSIL / SSR
	if params.has("ssao_enabled") and params["ssao_enabled"] != null:
		target_env.ssao_enabled = bool(params["ssao_enabled"])
		applied_props["ssao_enabled"] = target_env.ssao_enabled

	if params.has("ssao_radius") and params["ssao_radius"] != null:
		target_env.ssao_radius = float(params["ssao_radius"])
		applied_props["ssao_radius"] = target_env.ssao_radius

	if params.has("ssil_enabled") and params["ssil_enabled"] != null:
		target_env.ssil_enabled = bool(params["ssil_enabled"])
		applied_props["ssil_enabled"] = target_env.ssil_enabled

	if params.has("ssr_enabled") and params["ssr_enabled"] != null:
		target_env.ssr_enabled = bool(params["ssr_enabled"])
		applied_props["ssr_enabled"] = target_env.ssr_enabled

	# 6. Volumetric Fog
	if params.has("volumetric_fog_enabled") and params["volumetric_fog_enabled"] != null:
		target_env.volumetric_fog_enabled = bool(params["volumetric_fog_enabled"])
		applied_props["volumetric_fog_enabled"] = target_env.volumetric_fog_enabled

	if params.has("volumetric_fog_density") and params["volumetric_fog_density"] != null:
		target_env.volumetric_fog_density = float(params["volumetric_fog_density"])
		applied_props["volumetric_fog_density"] = target_env.volumetric_fog_density

	if params.has("volumetric_fog_albedo") and params["volumetric_fog_albedo"] != null:
		target_env.volumetric_fog_albedo = Color.from_string(str(params["volumetric_fog_albedo"]), target_env.volumetric_fog_albedo)
		applied_props["volumetric_fog_albedo"] = str(target_env.volumetric_fog_albedo)

	var saved_path: String = params.get("save_path", "")
	if saved_path != "":
		ResourceSaver.save(target_env, saved_path)

	return {
		"success": true,
		"message": "Configured Environment (%d properties updated%s)." % [
			applied_props.size(),
			", saved to " + saved_path if saved_path != "" else ""
		],
		"data": {
			"properties_set": applied_props,
			"saved_path": saved_path if saved_path != "" else null,
			"target_node": node_path if node_path != "" else null
		}
	}
