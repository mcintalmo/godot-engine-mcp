@tool
class_name BridgeServer
extends Node

const PORT = 3118

const OPERATION_CLASSES: Array = [
	preload("res://addons/godot_mcp/operations/scene_ops.gd"),
	preload("res://addons/godot_mcp/operations/project_ops.gd"),
	preload("res://addons/godot_mcp/operations/screenshot_ops.gd"),
	preload("res://addons/godot_mcp/operations/reflection_ops.gd"),
	preload("res://addons/godot_mcp/operations/material_ops.gd"),
	preload("res://addons/godot_mcp/operations/asset_ops.gd"),
	preload("res://addons/godot_mcp/operations/animation_ops.gd"),
	preload("res://addons/godot_mcp/operations/tilemap_ops.gd"),
	preload("res://addons/godot_mcp/operations/navigation_ops.gd"),
	preload("res://addons/godot_mcp/operations/performance_ops.gd"),
	preload("res://addons/godot_mcp/operations/theme_ops.gd"),
	preload("res://addons/godot_mcp/operations/audio_ops.gd"),
	preload("res://addons/godot_mcp/operations/play_ops.gd"),
	preload("res://addons/godot_mcp/operations/physics_ops.gd"),
	preload("res://addons/godot_mcp/operations/input_ops.gd"),
	preload("res://addons/godot_mcp/operations/environment_ops.gd"),
	preload("res://addons/godot_mcp/operations/editor_ops.gd"),
	preload("res://addons/godot_mcp/operations/dcc_ops.gd"),
	preload("res://addons/godot_mcp/operations/particle_ops.gd"),
	preload("res://addons/godot_mcp/operations/build_ops.gd"),
	preload("res://addons/godot_mcp/operations/autoload_ops.gd"),
	preload("res://addons/godot_mcp/operations/signal_ops.gd"),
	preload("res://addons/godot_mcp/operations/eval_ops.gd"),
	preload("res://addons/godot_mcp/operations/shader_ops.gd"),
	preload("res://addons/godot_mcp/operations/anim_tree_ops.gd"),
	preload("res://addons/godot_mcp/operations/localization_ops.gd"),
	preload("res://addons/godot_mcp/operations/uid_ops.gd"),
	preload("res://addons/godot_mcp/operations/plugin_ops.gd"),
	preload("res://addons/godot_mcp/operations/nav_obstacle_ops.gd"),
	preload("res://addons/godot_mcp/operations/tileset_terrain_ops.gd"),
	preload("res://addons/godot_mcp/operations/scene_diff_ops.gd"),
	preload("res://addons/godot_mcp/operations/editor_history_ops.gd"),
	preload("res://addons/godot_mcp/operations/editor_selection_ops.gd"),
	preload("res://addons/godot_mcp/operations/asset_audit_ops.gd"),
	preload("res://addons/godot_mcp/operations/gut_test_ops.gd"),
	preload("res://addons/godot_mcp/operations/editor_layout_ops.gd"),
	preload("res://addons/godot_mcp/operations/scene_hierarchy_ops.gd"),
	preload("res://addons/godot_mcp/operations/script_lifecycle_ops.gd"),
	preload("res://addons/godot_mcp/operations/camera_rendering_ops.gd"),
	preload("res://addons/godot_mcp/operations/input_simulation_ops.gd"),
	preload("res://addons/godot_mcp/operations/e2e_automation_ops.gd"),
	preload("res://addons/godot_mcp/operations/gridmap_path_ops.gd"),
	preload("res://addons/godot_mcp/operations/profiling_diagnostics_ops.gd"),
	preload("res://addons/godot_mcp/operations/multiplayer_ops.gd"),
	preload("res://addons/godot_mcp/operations/gameplay_scaffolding_ops.gd"),
	preload("res://addons/godot_mcp/operations/procedural_geometry_ops.gd"),
	preload("res://addons/godot_mcp/operations/skeleton_ik_ops.gd"),
	preload("res://addons/godot_mcp/operations/physics_constraints_ops.gd"),
	preload("res://addons/godot_mcp/operations/lightmap_gi_ops.gd"),
	preload("res://addons/godot_mcp/operations/openxr_ops.gd"),
	preload("res://addons/godot_mcp/operations/rendering_device_ops.gd"),
	preload("res://addons/godot_mcp/operations/multimesh_scatter_ops.gd"),
]

var _plugin: Node
var _port: int = PORT
var _tcp_server: TCPServer = TCPServer.new()
var _peers: Array[WebSocketPeer] = []
var _ops_modules: Array[RefCounted] = []

func _init(plugin: Node = null, port: int = PORT) -> void:
	_plugin = plugin
	_port = port
	_ops_modules.clear()
	for op_cls in OPERATION_CLASSES:
		_ops_modules.append(op_cls.new(_plugin))

func start() -> void:
	var err = _tcp_server.listen(_port, "127.0.0.1")
	if err == OK:
		print("[Godot MCP] Live Editor Bridge listening on 127.0.0.1:%d" % _port)
	else:
		push_error("[Godot MCP] Failed to start WebSocket server on port %d, error code: %d" % [_port, err])

func stop() -> void:
	for peer in _peers:
		peer.close()
	_peers.clear()
	_tcp_server.stop()
	print("[Godot MCP] Live Editor Bridge stopped.")

func _process(_delta: float) -> void:
	if not _tcp_server.is_listening():
		return

	while _tcp_server.is_connection_available():
		var conn = _tcp_server.take_connection()
		if conn:
			var ws_peer = WebSocketPeer.new()
			ws_peer.accept_stream(conn)
			_peers.append(ws_peer)

	var i = _peers.size() - 1
	while i >= 0:
		var peer = _peers[i]
		peer.poll()
		var state = peer.get_ready_state()

		if state == WebSocketPeer.STATE_OPEN:
			while peer.get_available_packet_count() > 0:
				var packet = peer.get_packet()
				var text = packet.get_string_from_utf8()
				var response = _handle_raw_request(text)
				peer.send_text(response)
		elif state == WebSocketPeer.STATE_CLOSED:
			_peers.remove_at(i)

		i -= 1

func _handle_raw_request(raw_json: String) -> String:
	var json = JSON.new()
	var err = json.parse(raw_json)
	if err != OK:
		return JSON.stringify({
			"jsonrpc": "2.0",
			"id": null,
			"error": {
				"code": -32700,
				"message": "Parse error: invalid JSON."
			}
		})

	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		return JSON.stringify({
			"jsonrpc": "2.0",
			"id": null,
			"error": {
				"code": -32600,
				"message": "Invalid Request: expected JSON-RPC 2.0 object."
			}
		})

	var req = data as Dictionary
	var req_id = req.get("id", null)
	var method = req.get("method", "")
	var params = req.get("params", {})

	if typeof(params) != TYPE_DICTIONARY:
		params = {}

	var result = _dispatch_rpc(method, params)

	if result.has("error") and typeof(result["error"]) == TYPE_DICTIONARY:
		return JSON.stringify({
			"jsonrpc": "2.0",
			"id": req_id,
			"error": result["error"]
		})

	return JSON.stringify({
		"jsonrpc": "2.0",
		"id": req_id,
		"result": result
	})

func _dispatch_rpc(method: String, params: Dictionary) -> Dictionary:
	if method == "ping":
		return {"pong": true}

	for op in _ops_modules:
		if op.has_method(method):
			return op.call(method, params)

	return {
		"success": false,
		"message": "Method '%s' not found on Godot bridge." % method
	}
