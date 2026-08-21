@tool
extends RefCounted

## Operations for Godot TileSet Terrain sets, autotiling patterns, and peering bit configuration.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func configure_tileset_terrain(params: Dictionary) -> Dictionary:
	var path: String = params.get("tileset_path", "")
	if path == "":
		return {"success": false, "message": "tileset_path cannot be empty."}

	var tileset: TileSet = null
	var node_target: Node = null

	if path.begins_with("res://"):
		if FileAccess.file_exists(path):
			var res = load(path)
			if res is TileSet:
				tileset = res
		else:
			tileset = TileSet.new()
	else:
		var root: Node = null
		if _plugin:
			root = _plugin.get_editor_interface().get_edited_scene_root()
		if root:
			var target = root.get_node_or_null(path)
			if target and "tile_set" in target and target.tile_set is TileSet:
				tileset = target.tile_set
				node_target = target

	if not tileset:
		tileset = TileSet.new()

	var set_idx: int = int(params.get("terrain_set", 0))
	while tileset.get_terrain_sets_count() <= set_idx:
		tileset.add_terrain_set(tileset.get_terrain_sets_count())

	var mode_str = params.get("mode", "match_corners_and_sides")
	var mode_enum = TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES
	match mode_str:
		"match_corners":
			mode_enum = TileSet.TERRAIN_MODE_MATCH_CORNERS
		"match_sides":
			mode_enum = TileSet.TERRAIN_MODE_MATCH_SIDES
		_:
			mode_enum = TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES

	tileset.set_terrain_set_mode(set_idx, mode_enum)

	var terrains = params.get("terrains", [])
	for i in range(terrains.size()):
		var t_info = terrains[i]
		while tileset.get_terrains_count(set_idx) <= i:
			tileset.add_terrain(set_idx, tileset.get_terrains_count(set_idx))

		var t_name = t_info.get("name", "Terrain %d" % i)
		tileset.set_terrain_name(set_idx, i, t_name)

		var t_color_str = t_info.get("color")
		if t_color_str != null and str(t_color_str) != "":
			tileset.set_terrain_color(set_idx, i, Color(str(t_color_str)))

	var peering_bits = params.get("tile_peering_bits", [])
	for p in peering_bits:
		var src_id = int(p.get("source_id", 0))
		var coords_arr = p.get("atlas_coords", [0, 0])
		var coords = Vector2i(int(coords_arr[0]), int(coords_arr[1]))

		var src = tileset.get_source(src_id)
		if src and src is TileSetAtlasSource:
			var atlas: TileSetAtlasSource = src
			var t_idx = int(p.get("terrain", 0))
			atlas.set_tile_terrain_set(coords, set_idx)
			atlas.set_tile_terrain(coords, t_idx)

			var bits = p.get("bits", {})
			for bit_name in bits:
				var bit_val = int(bits[bit_name])
				var neighbor = _parse_cell_neighbor(bit_name)
				if neighbor != -1:
					atlas.set_tile_terrain_peering_bit(coords, neighbor, bit_val)

	var save_dest = params.get("save_path")
	if save_dest != null and str(save_dest) != "":
		ResourceSaver.save(tileset, str(save_dest))
	elif path.begins_with("res://"):
		ResourceSaver.save(tileset, path)

	return {
		"success": true,
		"message": "Configured TileSet terrain set %d (%s) with %d terrains." % [set_idx, mode_str, terrains.size()],
		"data": {
			"tileset_path": path,
			"terrain_set": set_idx,
			"mode": mode_str,
			"terrain_count": tileset.get_terrains_count(set_idx),
			"saved_path": save_dest if save_dest else (path if path.begins_with("res://") else null)
		}
	}

func _parse_cell_neighbor(name: String) -> int:
	match name.to_lower():
		"right_side": return TileSet.CELL_NEIGHBOR_RIGHT_SIDE
		"right_corner": return TileSet.CELL_NEIGHBOR_RIGHT_CORNER
		"bottom_right_side": return TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_SIDE
		"bottom_right_corner": return TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER
		"bottom_side": return TileSet.CELL_NEIGHBOR_BOTTOM_SIDE
		"bottom_corner": return TileSet.CELL_NEIGHBOR_BOTTOM_CORNER
		"bottom_left_side": return TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_SIDE
		"bottom_left_corner": return TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER
		"left_side": return TileSet.CELL_NEIGHBOR_LEFT_SIDE
		"left_corner": return TileSet.CELL_NEIGHBOR_LEFT_CORNER
		"top_left_side": return TileSet.CELL_NEIGHBOR_TOP_LEFT_SIDE
		"top_left_corner": return TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER
		"top_side": return TileSet.CELL_NEIGHBOR_TOP_SIDE
		"top_corner": return TileSet.CELL_NEIGHBOR_TOP_CORNER
		"top_right_side": return TileSet.CELL_NEIGHBOR_TOP_RIGHT_SIDE
		"top_right_corner": return TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER
		_: return -1
