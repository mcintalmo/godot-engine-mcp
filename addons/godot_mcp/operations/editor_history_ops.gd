@tool
extends RefCounted

## Operations for Godot Editor Undo/Redo history and action rollback.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func undo_action(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not available."}

	var mgr = _plugin.get_undo_redo()
	if not mgr:
		return {"success": false, "message": "EditorUndoRedoManager not accessible."}

	var h_id = params.get("history_id")
	var ur: UndoRedo = null

	if h_id != null:
		ur = mgr.get_history_undo_redo(int(h_id))
	else:
		var root = _plugin.get_editor_interface().get_edited_scene_root()
		if root:
			ur = mgr.get_history_undo_redo(root.get_instance_id())
		if not ur:
			ur = mgr.get_history_undo_redo(0) # GLOBAL_HISTORY

	if not ur:
		return {"success": false, "message": "No active UndoRedo history found."}

	var action_name = ur.get_current_action_name()
	var has_undo = ur.has_undo()

	if not has_undo:
		return {
			"success": false,
			"message": "No actions available to undo in history.",
			"data": {"history_has_undo": false}
		}

	var ok = ur.undo()
	return {
		"success": true,
		"message": "Undid editor action: '%s'." % (action_name if action_name != "" else "Previous Action"),
		"data": {
			"action_name": action_name,
			"has_undo": ur.has_undo(),
			"has_redo": ur.has_redo()
		}
	}

func redo_action(params: Dictionary) -> Dictionary:
	if not _plugin:
		return {"success": false, "message": "EditorPlugin reference not available."}

	var mgr = _plugin.get_undo_redo()
	if not mgr:
		return {"success": false, "message": "EditorUndoRedoManager not accessible."}

	var h_id = params.get("history_id")
	var ur: UndoRedo = null

	if h_id != null:
		ur = mgr.get_history_undo_redo(int(h_id))
	else:
		var root = _plugin.get_editor_interface().get_edited_scene_root()
		if root:
			ur = mgr.get_history_undo_redo(root.get_instance_id())
		if not ur:
			ur = mgr.get_history_undo_redo(0) # GLOBAL_HISTORY

	if not ur:
		return {"success": false, "message": "No active UndoRedo history found."}

	var has_redo = ur.has_redo()
	if not has_redo:
		return {
			"success": false,
			"message": "No actions available to redo in history.",
			"data": {"history_has_redo": false}
		}

	var action_name = ur.get_current_action_name()
	var ok = ur.redo()
	return {
		"success": true,
		"message": "Redid editor action: '%s'." % (action_name if action_name != "" else "Next Action"),
		"data": {
			"action_name": action_name,
			"has_undo": ur.has_undo(),
			"has_redo": ur.has_redo()
		}
	}

func undo(params: Dictionary) -> Dictionary:
	return undo_action(params)

func redo(params: Dictionary) -> Dictionary:
	return redo_action(params)

