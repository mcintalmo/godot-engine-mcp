@tool
extends RefCounted

## Operations for creating TileMapLayer nodes, batch-painting tile cells, and querying level tile geometry.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func set_cells(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	var cells: Array = params.get("cells", [])
	var clear_before_paint: bool = bool(params.get("clear_before_paint", false))

	if node_path == "":
		return {"success": false, "message": "node_path parameter cannot be empty."}

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var target_node = edited_root.get_node_or_null(NodePath(node_path))
	if not target_node and (node_path == "." or node_path == ""):
		target_node = edited_root

	if not target_node:
		return {"success": false, "message": "TileMapLayer/TileMap node not found at path '%s'." % node_path}

	if not target_node.has_method("set_cell"):
		return {
			"success": false,
			"message": "Target node '%s' (type: %s) does not support set_cell(). Expected TileMapLayer or TileMap." % [
				target_node.name, target_node.get_class()
			]
		}

	if clear_before_paint and target_node.has_method("clear"):
		target_node.clear()

	var painted_count: int = 0
	var erased_count: int = 0

	for c in cells:
		if typeof(c) != TYPE_DICTIONARY:
			continue
		var c_dict = c as Dictionary
		var raw_coords = c_dict.get("coords", [0, 0])
		if typeof(raw_coords) != TYPE_ARRAY or (raw_coords as Array).size() < 2:
			continue

		var coords = Vector2i(int((raw_coords as Array)[0]), int((raw_coords as Array)[1]))
		var source_id = int(c_dict.get("source_id", 0))
		var raw_atlas = c_dict.get("atlas_coords", [0, 0])
		var atlas_coords = Vector2i(0, 0)
		if typeof(raw_atlas) == TYPE_ARRAY and (raw_atlas as Array).size() >= 2:
			atlas_coords = Vector2i(int((raw_atlas as Array)[0]), int((raw_atlas as Array)[1]))
		var alt_tile = int(c_dict.get("alternative_tile", 0))

		target_node.set_cell(coords, source_id, atlas_coords, alt_tile)
		if source_id == -1:
			erased_count += 1
		else:
			painted_count += 1

	var used_rect_data: Array = []
	if target_node.has_method("get_used_rect"):
		var rect: Rect2i = target_node.get_used_rect()
		used_rect_data = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

	return {
		"success": true,
		"message": "Applied tile cells to '%s' (painted: %d, erased: %d)." % [target_node.name, painted_count, erased_count],
		"data": {
			"node_path": node_path,
			"node_name": target_node.name,
			"painted_count": painted_count,
			"erased_count": erased_count,
			"used_rect": used_rect_data
		}
	}

func get_cells(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	var region: Array = params.get("region", [])

	if node_path == "":
		return {"success": false, "message": "node_path parameter cannot be empty."}

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var target_node = edited_root.get_node_or_null(NodePath(node_path))
	if not target_node and (node_path == "." or node_path == ""):
		target_node = edited_root

	if not target_node:
		return {"success": false, "message": "TileMapLayer/TileMap node not found at path '%s'." % node_path}

	if not target_node.has_method("get_used_cells"):
		return {
			"success": false,
			"message": "Target node '%s' (type: %s) does not support get_used_cells()." % [
				target_node.name, target_node.get_class()
			]
		}

	var used_cells: Array = target_node.get_used_cells()
	var result_cells: Array = []

	var filter_region: bool = region.size() >= 4
	var min_x = int(region[0]) if filter_region else 0
	var min_y = int(region[1]) if filter_region else 0
	var max_x = int(region[2]) if filter_region else 0
	var max_y = int(region[3]) if filter_region else 0

	for coords in used_cells:
		var v2i = coords as Vector2i
		if filter_region:
			if v2i.x < min_x or v2i.x > max_x or v2i.y < min_y or v2i.y > max_y:
				continue

		var s_id: int = target_node.get_cell_source_id(v2i) if target_node.has_method("get_cell_source_id") else 0
		var ac: Vector2i = target_node.get_cell_atlas_coords(v2i) if target_node.has_method("get_cell_atlas_coords") else Vector2i(0, 0)
		var alt: int = target_node.get_cell_alternative_tile(v2i) if target_node.has_method("get_cell_alternative_tile") else 0

		result_cells.append({
			"coords": [v2i.x, v2i.y],
			"source_id": s_id,
			"atlas_coords": [ac.x, ac.y],
			"alternative_tile": alt
		})

	var used_rect_data: Array = []
	if target_node.has_method("get_used_rect"):
		var rect: Rect2i = target_node.get_used_rect()
		used_rect_data = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

	return {
		"success": true,
		"message": "Retrieved %d cells from '%s'." % [result_cells.size(), target_node.name],
		"data": {
			"node_path": node_path,
			"node_name": target_node.name,
			"cell_count": result_cells.size(),
			"cells": result_cells,
			"used_rect": used_rect_data
		}
	}

func create_tilemap_layer(params: Dictionary) -> Dictionary:
	var name_str: String = params.get("name", "TileMapLayer")
	var parent_node_path: String = params.get("parent_node_path", ".")
	var tile_set_path: String = params.get("tile_set_path", "")

	if not _plugin:
		return {"success": false, "message": "Editor plugin reference not initialized."}

	var editor_interface = _plugin.get_editor_interface()
	var edited_root = editor_interface.get_edited_scene_root()
	if not edited_root:
		return {"success": false, "message": "No active scene open in Godot Editor."}

	var parent_node = edited_root.get_node_or_null(NodePath(parent_node_path))
	if not parent_node and (parent_node_path == "." or parent_node_path == ""):
		parent_node = edited_root

	if not parent_node:
		return {"success": false, "message": "Parent node '%s' not found." % parent_node_path}

	var layer: Node = null
	if ClassDB.class_exists("TileMapLayer"):
		layer = ClassDB.instantiate("TileMapLayer")
	else:
		layer = TileMap.new()

	layer.name = name_str

	if tile_set_path != "":
		if ResourceLoader.exists(tile_set_path):
			var ts = load(tile_set_path)
			if ts and ts is TileSet:
				layer.set("tile_set", ts)
		else:
			return {
				"success": false,
				"message": "TileSet resource not found at path '%s'." % tile_set_path
			}

	var undo_redo = _plugin.get_undo_redo()
	if undo_redo:
		undo_redo.create_action("Create TileMapLayer '%s'" % name_str)
		undo_redo.add_do_method(parent_node, "add_child", layer)
		undo_redo.add_do_method(layer, "set_owner", edited_root)
		undo_redo.add_do_reference(layer)
		undo_redo.add_undo_method(parent_node, "remove_child", layer)
		undo_redo.commit_action()
	else:
		parent_node.add_child(layer)
		layer.owner = edited_root

	return {
		"success": true,
		"message": "Created TileMapLayer '%s' under '%s'." % [name_str, parent_node.name],
		"data": {
			"node_name": layer.name,
			"type_name": layer.get_class(),
			"parent_node_path": parent_node_path,
			"tile_set_attached": tile_set_path if tile_set_path != "" else None
		}
	}
