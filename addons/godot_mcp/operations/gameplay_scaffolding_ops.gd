@tool
extends RefCounted

## Operations for Godot Gameplay AI & State Machine Scaffolding.

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

func scaffold_state_machine(params: Dictionary) -> Dictionary:
	var target_dir = str(params.get("target_dir", "res://scripts/state_machine")).rstrip("/")
	var machine_name = str(params.get("machine_name", "CharacterStateMachine"))
	var states = params.get("states", ["Idle", "Move", "Jump", "Fall"])
	var gen_hierarchy = bool(params.get("generate_node_hierarchy", true))
	var parent_path = str(params.get("parent_node_path", "."))

	# Ensure target directory exists
	DirAccess.make_dir_recursive_absolute(target_dir)

	var files_created = []

	# 1. Base State.gd
	var state_script_path = "%s/state.gd" % target_dir
	var state_code = """class_name State
extends Node

signal transitioned(state: State, new_state_name: String)

func enter() -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass
"""
	var f = FileAccess.open(state_script_path, FileAccess.WRITE)
	if f:
		f.store_string(state_code)
		f.close()
		files_created.append(state_script_path)

	# 2. StateMachine.gd
	var sm_script_path = "%s/%s.gd" % [target_dir, machine_name.to_snake_case()]
	var sm_code = """class_name %s
extends Node

@export var initial_state: State

var current_state: State
var states: Dictionary = {}

func _ready() -> void:
	for child in get_children():
		if child is State:
			states[child.name.to_lower()] = child
			child.transitioned.connect(on_child_transitioned)
	
	if initial_state:
		initial_state.enter()
		current_state = initial_state

func _process(delta: float) -> void:
	if current_state:
		current_state.update(delta)

func _physics_process(delta: float) -> void:
	if current_state:
		current_state.physics_update(delta)

func on_child_transitioned(state: State, new_state_name: String) -> void:
	if state != current_state:
		return
	
	var new_state = states.get(new_state_name.to_lower())
	if not new_state:
		push_warning("State '%s' does not exist in StateMachine." % new_state_name)
		return
	
	if current_state:
		current_state.exit()
	
	new_state.enter()
	current_state = new_state
""" % machine_name
	f = FileAccess.open(sm_script_path, FileAccess.WRITE)
	if f:
		f.store_string(sm_code)
		f.close()
		files_created.append(sm_script_path)

	# 3. Individual State Scripts
	var state_scripts = {}
	if states is Array:
		for s in states:
			var s_name = str(s).strip_edges()
			if s_name != "":
				var script_name = "%s_%s" % [machine_name.to_snake_case(), s_name.to_snake_case()]
				var path = "%s/%s_state.gd" % [target_dir, s_name.to_snake_case()]
				var code = """extends State

func enter() -> void:
	# Enter logic for %s state
	pass

func exit() -> void:
	# Exit logic for %s state
	pass

func update(_delta: float) -> void:
	# Frame process logic for %s state
	pass

func physics_update(_delta: float) -> void:
	# Physics process logic for %s state
	pass
""" % [s_name, s_name, s_name, s_name]
				f = FileAccess.open(path, FileAccess.WRITE)
				if f:
					f.store_string(code)
					f.close()
					files_created.append(path)
					state_scripts[s_name] = path

	var hierarchy_created = false
	var root = _get_scene_root()
	if gen_hierarchy and root:
		var parent_node = _find_node(parent_path, root)
		if parent_node:
			var sm_node = Node.new()
			sm_node.name = machine_name
			if ResourceLoader.exists(sm_script_path):
				sm_node.set_script(ResourceLoader.load(sm_script_path))
			parent_node.add_child(sm_node)
			sm_node.owner = root

			var first_state_node: Node = null
			for s_name in state_scripts.keys():
				var s_node = Node.new()
				s_node.name = s_name
				var s_path = state_scripts[s_name]
				if ResourceLoader.exists(s_path):
					s_node.set_script(ResourceLoader.load(s_path))
				sm_node.add_child(s_node)
				s_node.owner = root
				if first_state_node == null:
					first_state_node = s_node

			if first_state_node and sm_node.get("initial_state") != null:
				sm_node.set("initial_state", first_state_node)
			hierarchy_created = true

	return {
		"success": true,
		"message": "Scaffolded State Machine '%s' with %d states in '%s'." % [machine_name, state_scripts.size(), target_dir],
		"data": {
			"machine_name": machine_name,
			"target_dir": target_dir,
			"files_created": files_created,
			"states_count": state_scripts.size(),
			"hierarchy_attached": hierarchy_created
		}
	}

func create_dialogue_resource(params: Dictionary) -> Dictionary:
	var res_path = str(params.get("resource_path", "res://dialogue/conversation.json"))
	var format = str(params.get("format", "json")).to_lower()
	var nodes = params.get("dialogue_nodes", [])

	# Ensure parent directory exists
	var dir_path = res_path.get_base_dir()
	if dir_path != "":
		DirAccess.make_dir_recursive_absolute(dir_path)

	var node_list = []
	if nodes is Array:
		for n in nodes:
			if n is Dictionary:
				node_list.append(n)

	var payload = {
		"version": "1.0",
		"dialogue_tree": node_list
	}

	var content = JSON.stringify(payload, "\t")
	var f = FileAccess.open(res_path, FileAccess.WRITE)
	if not f:
		return {"success": false, "message": "Failed to write dialogue file at '%s'." % res_path}

	f.store_string(content)
	f.close()

	return {
		"success": true,
		"message": "Created dialogue tree at '%s' with %d nodes." % [res_path, node_list.size()],
		"data": {
			"dialogue_path": res_path,
			"dialogue_format": format,
			"dialogue_nodes_count": node_list.size(),
			"dialogue_nodes": node_list
		}
	}

