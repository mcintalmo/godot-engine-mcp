@tool
class_name ScreenshotOperations
extends RefCounted

var _plugin: Node

func _init(plugin: Node = null) -> void:
	_plugin = plugin

func take_screenshot(params: Dictionary) -> Dictionary:
	var viewport: Viewport = null
	var vp_type = params.get("viewport_type", "main_2d_3d")

	if _plugin and _plugin.has_method("get_editor_interface"):
		var ei = _plugin.get_editor_interface()
		if ei:
			if vp_type == "2d" and ei.has_method("get_editor_viewport_2d"):
				viewport = ei.get_editor_viewport_2d()
			elif vp_type == "3d" and ei.has_method("get_editor_viewport_3d"):
				viewport = ei.get_editor_viewport_3d()
			elif ei.has_method("get_editor_main_screen") and ei.get_editor_main_screen():
				viewport = ei.get_editor_main_screen().get_viewport()

	if not viewport and _plugin and _plugin.is_inside_tree():
		viewport = _plugin.get_tree().root

	if not viewport:
		return {"success": false, "message": "Could not access editor or main viewport."}

	var texture = viewport.get_texture()
	if not texture:
		return {"success": false, "message": "Could not get viewport texture."}

	var img: Image = texture.get_image()
	if not img or img.is_empty():
		return {"success": false, "message": "Could not get viewport image or image is empty."}


	var output_path = params.get("output_path")
	if output_path:
		var err = img.save_png(output_path)
		if err != OK:
			return {"success": false, "message": "Failed to save screenshot to %s, error code: %d" % [output_path, err]}
		return {
			"success": true,
			"message": "Screenshot saved to %s" % output_path,
			"path": output_path,
			"width": img.get_width(),
			"height": img.get_height()
		}

	var buffer: PackedByteArray = img.save_png_to_buffer()
	var b64: String = Marshalls.raw_to_base64(buffer)

	return {
		"success": true,
		"message": "Captured viewport screenshot (%dx%d)" % [img.get_width(), img.get_height()],
		"image_base64": b64,
		"mime_type": "image/png",
		"width": img.get_width(),
		"height": img.get_height()
	}
