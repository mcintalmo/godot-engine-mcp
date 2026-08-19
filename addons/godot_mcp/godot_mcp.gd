@tool
extends EditorPlugin

const BridgeServer = preload("res://addons/godot_mcp/bridge_server.gd")

var _server: BridgeServer = null

func _enter_tree() -> void:
	print("[Godot MCP] Initializing Godot MCP Editor Plugin (Godot 4.7+)...")
	_server = BridgeServer.new(self)
	add_child(_server)
	_server.start()

func _exit_tree() -> void:
	if _server != null:
		print("[Godot MCP] Stopping Godot MCP Editor Plugin...")
		_server.stop()
		_server.queue_free()
		_server = null
