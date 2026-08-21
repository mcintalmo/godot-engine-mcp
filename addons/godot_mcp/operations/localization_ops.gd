@tool
extends RefCounted

## Operations for Godot Localization and Translation management in project.godot and TranslationServer.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func get_translations(params: Dictionary) -> Dictionary:
	var setting_key = "internationalization/locale/translations"
	var raw_translations = ProjectSettings.get_setting(setting_key, PackedStringArray())
	var trans_list: Array = []

	for t in raw_translations:
		var p = str(t)
		var exists = FileAccess.file_exists(p) or ResourceLoader.exists(p)
		trans_list.append({
			"path": p,
			"exists": exists
		})

	var loaded_locales = TranslationServer.get_loaded_locales()
	var fallback = ProjectSettings.get_setting("internationalization/locale/fallback", "en")

	return {
		"success": true,
		"message": "Found %d translation tables in project.godot." % trans_list.size(),
		"data": {
			"translation_count": trans_list.size(),
			"translations": trans_list,
			"loaded_locales": loaded_locales,
			"fallback_locale": str(fallback)
		}
	}

func add_translation(params: Dictionary) -> Dictionary:
	var path: String = params.get("translation_path", "")
	if path == "":
		return {"success": false, "message": "translation_path cannot be empty."}

	var setting_key = "internationalization/locale/translations"
	var existing = ProjectSettings.get_setting(setting_key, PackedStringArray())
	var updated_arr: Array = []

	for item in existing:
		updated_arr.append(str(item))

	if not updated_arr.has(path):
		updated_arr.append(path)

	ProjectSettings.set_setting(setting_key, PackedStringArray(updated_arr))
	ProjectSettings.save()

	var test_locale = params.get("test_locale")
	if test_locale != null and str(test_locale) != "":
		TranslationServer.set_locale(str(test_locale))

	return {
		"success": true,
		"message": "Added translation '%s' to project.godot." % path,
		"data": {
			"translation_path": path,
			"total_translations": updated_arr.size(),
			"test_locale_set": str(test_locale) if test_locale else null
		}
	}
