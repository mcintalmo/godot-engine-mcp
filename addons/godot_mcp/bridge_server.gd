@tool
class_name BridgeServer
extends Node

const PORT = 3118

const SceneOps = preload("res://addons/godot_mcp/operations/scene_ops.gd")
const ProjectOps = preload("res://addons/godot_mcp/operations/project_ops.gd")
const ScreenshotOps = preload("res://addons/godot_mcp/operations/screenshot_ops.gd")
const ReflectionOps = preload("res://addons/godot_mcp/operations/reflection_ops.gd")
const MaterialOps = preload("res://addons/godot_mcp/operations/material_ops.gd")
const AssetOps = preload("res://addons/godot_mcp/operations/asset_ops.gd")
const AnimationOps = preload("res://addons/godot_mcp/operations/animation_ops.gd")
const TileMapOps = preload("res://addons/godot_mcp/operations/tilemap_ops.gd")
const NavigationOps = preload("res://addons/godot_mcp/operations/navigation_ops.gd")
const PerformanceOps = preload("res://addons/godot_mcp/operations/performance_ops.gd")
const ThemeOps = preload("res://addons/godot_mcp/operations/theme_ops.gd")

var _plugin: Node
var _tcp_server: TCPServer = TCPServer.new()
var _peers: Array[WebSocketPeer] = []

var _scene_ops: RefCounted
var _project_ops: RefCounted
var _screenshot_ops: RefCounted
var _reflection_ops: RefCounted
var _material_ops: RefCounted
var _asset_ops: RefCounted
var _animation_ops: RefCounted
var _tilemap_ops: RefCounted
var _navigation_ops: RefCounted
var _performance_ops: RefCounted
var _theme_ops: RefCounted

var _port: int = PORT

func _init(plugin: Node = null, port: int = PORT) -> void:
	_plugin = plugin
	_port = port
	_scene_ops = SceneOps.new(_plugin)
	_project_ops = ProjectOps.new(_plugin)
	_screenshot_ops = ScreenshotOps.new(_plugin)
	_reflection_ops = ReflectionOps.new(_plugin)
	_material_ops = MaterialOps.new(_plugin)
	_asset_ops = AssetOps.new(_plugin)
	_animation_ops = AnimationOps.new(_plugin)
	_tilemap_ops = TileMapOps.new(_plugin)
	_navigation_ops = NavigationOps.new(_plugin)
	_performance_ops = PerformanceOps.new(_plugin)
	_theme_ops = ThemeOps.new(_plugin)










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

	# Accept incoming TCP connections
	while _tcp_server.is_connection_available():
		var tcp_conn = _tcp_server.take_connection()
		if tcp_conn:
			var ws_peer = WebSocketPeer.new()
			var err = ws_peer.accept_stream(tcp_conn)
			if err == OK:
				_peers.append(ws_peer)

	# Poll connected peers
	var to_remove: Array[WebSocketPeer] = []
	for peer in _peers:
		peer.poll()
		var state = peer.get_ready_state()
		if state == WebSocketPeer.STATE_OPEN:
			while peer.get_available_packet_count() > 0:
				var pkt = peer.get_packet()
				var text = pkt.get_string_from_utf8()
				_handle_message(peer, text)
		elif state == WebSocketPeer.STATE_CLOSED:
			to_remove.append(peer)

	for p in to_remove:
		_peers.erase(p)

func _handle_message(peer: WebSocketPeer, text: String) -> void:
	var json = JSON.new()
	var parse_err = json.parse(text)
	if parse_err != OK:
		_send_error(peer, null, -32700, "Parse error: Invalid JSON")
		return

	var req = json.data
	if not req is Dictionary:
		_send_error(peer, null, -32600, "Invalid Request")
		return

	var req_id = req.get("id")
	var method: String = req.get("method", "")
	var params: Dictionary = req.get("params", {})

	if method == "ping":
		_send_result(peer, req_id, {"pong": true, "engine": "godot"})
		return

	var result: Dictionary = {}
	match method:
		"get_version":
			result = _project_ops.get_version()
		"get_project_settings":
			result = _project_ops.get_project_settings(params)
		"set_project_setting":
			result = _project_ops.set_project_setting(params)
		"restart_editor":
			result = _project_ops.restart_editor(params)

		"list_nodes":
			result = _scene_ops.list_nodes(params)
		"get_node":
			result = _scene_ops.get_node_info(params)
		"create_node":
			result = _scene_ops.create_node(params)
		"modify_node":
			result = _scene_ops.modify_node(params)
		"delete_node":
			result = _scene_ops.delete_node(params)
		"connect_signal":
			result = _scene_ops.connect_signal(params)
		"instantiate_scene":
			result = _scene_ops.instantiate_scene(params)
		"save_scene":
			result = _scene_ops.save_scene(params)
		"open_scene":
			result = _scene_ops.open_scene(params)
		"create_scene":
			result = _scene_ops.create_scene(params)
		"take_screenshot":
			result = _screenshot_ops.take_screenshot(params)

		"get_class_info":
			result = _reflection_ops.get_class_info(params)
		"get_documentation":
			result = _reflection_ops.get_documentation(params)
		"validate_shader":
			result = _reflection_ops.validate_shader(params)
		"create_material":
			result = _material_ops.create_material(params)
		"reimport_asset":
			result = _asset_ops.reimport_asset(params)
		"create_collision_polygon":
			result = _asset_ops.create_collision_polygon(params)
		"create_animation":
			result = _animation_ops.create_animation(params)
		"set_tilemap_cells":
			result = _tilemap_ops.set_cells(params)
		"get_tilemap_cells":
			result = _tilemap_ops.get_cells(params)
		"create_tilemap_layer":
			result = _tilemap_ops.create_tilemap_layer(params)
		"bake_navmesh":
			result = _navigation_ops.bake_navmesh(params)
		"create_navigation_region":
			result = _navigation_ops.create_navigation_region(params)
		"get_performance_metrics":
			result = _performance_ops.get_metrics(params)
		"create_theme":
			result = _theme_ops.create_theme(params)
		"apply_theme_override":
			result = _theme_ops.apply_theme_override(params)










		_:
			_send_error(peer, req_id, -32601, "Method not found: %s" % method)
			return

	_send_result(peer, req_id, result)

func _send_result(peer: WebSocketPeer, req_id: Variant, result_data: Dictionary) -> void:
	var resp = {
		"jsonrpc": "2.0",
		"id": req_id,
		"result": result_data
	}
	peer.send_text(JSON.stringify(resp))

func _send_error(peer: WebSocketPeer, req_id: Variant, code: int, message: String) -> void:
	var resp = {
		"jsonrpc": "2.0",
		"id": req_id,
		"error": {
			"code": code,
			"message": message
		}
	}
	peer.send_text(JSON.stringify(resp))
