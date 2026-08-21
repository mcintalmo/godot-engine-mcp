@tool
extends RefCounted

## Operations for Godot Project Asset Auditing, Orphan Cleanup, and Texture Inspection.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func audit_assets(params: Dictionary) -> Dictionary:
	var inc_exts = params.get("include_extensions")
	var ignore_prefixes = params.get("ignore_paths", ["res://.godot/", "res://.git/"])

	var all_files: Array[String] = []
	_scan_dir_recursive("res://", all_files, ignore_prefixes)

	if inc_exts != null and inc_exts is Array and inc_exts.size() > 0:
		var filtered: Array[String] = []
		for f in all_files:
			for ext in inc_exts:
				if f.ends_with(str(ext)):
					filtered.append(f)
					break
		all_files = filtered

	# Build dependency graph
	var referenced_set: Dictionary = {}
	var broken_deps: Array = []

	# Add entry points
	var main_scene = ProjectSettings.get_setting("application/run/main_scene", "")
	if main_scene != "":
		referenced_set[main_scene] = true

	# Autoloads
	for prop in ProjectSettings.get_property_list():
		var p_name = prop.name
		if p_name.begins_with("autoload/"):
			var al_val = ProjectSettings.get_setting(p_name)
			if al_val is String and al_val.begins_with("res://"):
				referenced_set[al_val] = true

	# Check outbound dependencies for all files
	for f in all_files:
		if f.ends_with(".tscn") or f.ends_with(".tres") or f.ends_with(".gd") or f.ends_with(".glb"):
			var deps = ResourceLoader.get_dependencies(f)
			for d in deps:
				var resolved_p = str(d)
				if resolved_p.begins_with("uid://"):
					var uid_id = ResourceUID.text_to_id(resolved_p)
					if uid_id != ResourceUID.INVALID_ID and ResourceUID.has_id(uid_id):
						resolved_p = ResourceUID.get_id_path(uid_id)
					else:
						broken_deps.append({
							"source": f,
							"dependency": d,
							"reason": "Unresolvable UID"
						})
						continue

				referenced_set[resolved_p] = true
				if not FileAccess.file_exists(resolved_p):
					broken_deps.append({
						"source": f,
						"dependency": d,
						"resolved_path": resolved_p,
						"reason": "File not found on disk"
					})

	var orphan_list: Array = []
	for f in all_files:
		if not referenced_set.has(f):
			# Skip project.godot and export presets
			if not f.ends_with("project.godot") and not f.ends_with("export_presets.cfg"):
				orphan_list.append(f)

	return {
		"success": true,
		"message": "Asset Audit: %d total, %d orphans, %d broken dependencies." % [all_files.size(), orphan_list.size(), broken_deps.size()],
		"data": {
			"total_assets": all_files.size(),
			"orphan_count": orphan_list.size(),
			"broken_count": broken_deps.size(),
			"orphans": orphan_list,
			"broken_dependencies": broken_deps
		}
	}

func clean_orphans(params: Dictionary) -> Dictionary:
	var dry_run = bool(params.get("dry_run", true))
	var quarantine = params.get("quarantine_folder")
	var targets = params.get("file_paths")

	var candidates: Array = []
	if targets != null and targets is Array and targets.size() > 0:
		for t in targets:
			candidates.append(str(t))
	else:
		var audit = audit_assets({})
		candidates = audit.get("data", {}).get("orphans", [])

	var processed: Array = []
	if not dry_run:
		var dir = DirAccess.open("res://")
		if quarantine != null and str(quarantine) != "":
			var q_path = str(quarantine)
			if not DirAccess.dir_exists_absolute(q_path):
				DirAccess.make_dir_recursive_absolute(q_path)
			for f in candidates:
				var fname = f.get_file()
				var dest = q_path.path_join(fname)
				if DirAccess.rename_absolute(f, dest) == OK:
					processed.append({"path": f, "status": "quarantined", "destination": dest})
					if FileAccess.file_exists(f + ".import"):
						DirAccess.rename_absolute(f + ".import", dest + ".import")
		else:
			for f in candidates:
				if DirAccess.remove_absolute(f) == OK:
					processed.append({"path": f, "status": "deleted"})
					if FileAccess.file_exists(f + ".import"):
						DirAccess.remove_absolute(f + ".import")

	var action_str = "Simulated cleanup of" if dry_run else ("Quarantined/Deleted" if quarantine else "Deleted")
	return {
		"success": true,
		"message": "%s %d orphan assets (Dry Run: %s)." % [action_str, candidates.size(), str(dry_run)],
		"data": {
			"dry_run": dry_run,
			"quarantine_folder": quarantine,
			"target_count": candidates.size(),
			"candidates": candidates,
			"processed": processed
		}
	}

func get_texture_info(params: Dictionary) -> Dictionary:
	var path: String = params.get("texture_path", "")
	if path == "":
		return {"success": false, "message": "texture_path cannot be empty."}

	if not FileAccess.file_exists(path):
		return {"success": false, "message": "Texture file '%s' does not exist." % path}

	var res = load(path)
	if not res or not (res is Texture2D):
		return {"success": false, "message": "File '%s' is not a valid Texture2D resource." % path}

	var tex: Texture2D = res
	var w = tex.get_width()
	var h = tex.get_height()
	var has_mips = tex.has_mipmaps()
	var format_str = "Compressed/Unknown"

	var img = tex.get_image()
	var vram_est_bytes = w * h * 4
	if img:
		format_str = str(img.get_format())
		vram_est_bytes = img.get_data_size()
	if has_mips:
		vram_est_bytes = int(vram_est_bytes * 1.33)

	return {
		"success": true,
		"message": "Texture '%s': %dx%d (%s, ~%.2f KB VRAM)." % [path.get_file(), w, h, format_str, float(vram_est_bytes) / 1024.0],
		"data": {
			"path": path,
			"width": w,
			"height": h,
			"format": format_str,
			"has_mipmaps": has_mips,
			"estimated_vram_bytes": vram_est_bytes,
			"estimated_vram_kb": float(vram_est_bytes) / 1024.0
		}
	}

func _scan_dir_recursive(path: String, out_files: Array[String], ignore_prefixes: Array) -> void:
	for ig in ignore_prefixes:
		if path.begins_with(str(ig)):
			return

	var dir = DirAccess.open(path)
	if not dir:
		return

	dir.list_dir_begin()
	var f_name = dir.get_next()
	while f_name != "":
		if f_name != "." and f_name != "..":
			var full_p = path.path_join(f_name)
			if dir.current_is_dir():
				_scan_dir_recursive(full_p, out_files, ignore_prefixes)
			else:
				if not f_name.ends_with(".import") and not f_name.ends_with(".uid"):
					out_files.append(full_p)
		f_name = dir.get_next()
	dir.list_dir_end()
