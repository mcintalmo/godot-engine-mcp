@tool
extends RefCounted

## Operations for Godot AnimationTree setup, state machine graph generation, and transition configuration.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func configure_animation_tree(params: Dictionary) -> Dictionary:
	var root: Node = null
	if _plugin:
		root = _plugin.get_editor_interface().get_edited_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in editor."}

	var tree: AnimationTree = null
	var node_path = params.get("node_path")

	if node_path != null and str(node_path) != "":
		var target = root.get_node_or_null(str(node_path))
		if target is AnimationTree:
			tree = target
		else:
			return {"success": false, "message": "Target node '%s' is not an AnimationTree." % str(node_path)}
	else:
		var parent: Node = root
		var p_path = params.get("parent_path")
		if p_path != null and str(p_path) != "":
			var found_p = root.get_node_or_null(str(p_path))
			if found_p:
				parent = found_p

		tree = AnimationTree.new()
		tree.name = params.get("node_name", "AnimationTree")
		parent.add_child(tree)
		tree.owner = root

	var anim_player_path = params.get("anim_player_path")
	if anim_player_path != null and str(anim_player_path) != "":
		tree.anim_player = NodePath(str(anim_player_path))

	var tree_type = params.get("tree_type", "state_machine")
	var state_machine: AnimationNodeStateMachine = null

	if tree_type == "state_machine":
		if not tree.tree_root or not (tree.tree_root is AnimationNodeStateMachine):
			state_machine = AnimationNodeStateMachine.new()
			tree.tree_root = state_machine
		else:
			state_machine = tree.tree_root

		var states = params.get("states", [])
		for s in states:
			var s_name = s.get("name", "")
			var anim_name = s.get("animation", "")
			if s_name != "" and anim_name != "":
				var anim_node = AnimationNodeAnimation.new()
				anim_node.animation = StringName(anim_name)
				state_machine.add_node(StringName(s_name), anim_node)

		var transitions = params.get("transitions", [])
		for t in transitions:
			var from_s = t.get("from", "")
			var to_s = t.get("to", "")
			if from_s != "" and to_s != "":
				var trans = AnimationNodeStateMachineTransition.new()
				var adv_cond = t.get("advance_condition")
				if adv_cond != null and str(adv_cond) != "":
					trans.advance_condition = StringName(str(adv_cond))
				var adv_expr = t.get("advance_expression")
				if adv_expr != null and str(adv_expr) != "":
					trans.advance_expression = str(adv_expr)
				if bool(t.get("auto_advance", false)):
					trans.advance_mode = AnimationNodeStateMachineTransition.ADVANCE_MODE_AUTO

				state_machine.add_transition(StringName(from_s), StringName(to_s), trans)

	tree.active = bool(params.get("active", true))

	var save_path = params.get("save_as_resource_path")
	if save_path != null and str(save_path) != "":
		if tree.tree_root:
			ResourceSaver.save(tree.tree_root, str(save_path))

	return {
		"success": true,
		"message": "Configured AnimationTree '%s' (%s)." % [tree.name, tree_type],
		"data": {
			"node_name": tree.name,
			"node_path": str(tree.get_path()),
			"tree_type": tree_type,
			"active": tree.active,
			"anim_player": str(tree.anim_player),
			"saved_resource_path": save_path
		}
	}
