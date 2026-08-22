@tool
extends RefCounted

## Operations for Godot Multiplayer Spawner & Network Synchronization.

var _plugin: EditorPlugin

# Simulated network parameters
var _simulated_latency_ms: int = 0
var _simulated_packet_loss: float = 0.0
var _simulated_jitter_ms: int = 0
var _simulated_offline: bool = false

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

func configure_multiplayer_spawner(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("spawner_node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "MultiplayerSpawner node not found at '%s'." % node_path}

	if not (node is MultiplayerSpawner):
		return {"success": false, "message": "Node at '%s' is '%s', expected MultiplayerSpawner." % [node_path, node.get_class()]}

	var spawner: MultiplayerSpawner = node
	var changes = []

	if params.has("spawn_path") and params["spawn_path"] != null:
		spawner.spawn_path = NodePath(str(params["spawn_path"]))
		changes.append("Spawn Path: %s" % str(spawner.spawn_path))

	if params.has("spawn_limit") and params["spawn_limit"] != null:
		spawner.spawn_limit = int(params["spawn_limit"])
		changes.append("Spawn Limit: %d" % spawner.spawn_limit)

	if bool(params.get("clear_spawnable_scenes", false)):
		spawner.clear_spawnable_scenes()
		changes.append("Cleared spawnable scenes")

	var scenes = params.get("spawnable_scenes", [])
	var added_scenes = 0
	if scenes is Array:
		for sc in scenes:
			var sc_path = str(sc).strip_edges()
			if sc_path != "":
				spawner.add_spawnable_scene(sc_path)
				added_scenes += 1
		if added_scenes > 0:
			changes.append("Added %d spawnable scenes" % added_scenes)

	var total_scenes = spawner.get_spawnable_scene_count()

	return {
		"success": true,
		"message": "Configured MultiplayerSpawner '%s': %s." % [spawner.name, ", ".join(changes) if changes.size() > 0 else "No modifications"],
		"data": {
			"spawner_name": spawner.name,
			"spawner_path": str(root.get_path_to(spawner)),
			"spawn_path": str(spawner.spawn_path),
			"spawn_limit": spawner.spawn_limit,
			"spawnable_scene_count": total_scenes,
			"changes_applied": changes
		}
	}

func configure_multiplayer_synchronizer(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var node_path = str(params.get("synchronizer_node_path", ""))
	var node = _find_node(node_path, root)
	if not node:
		return {"success": false, "message": "MultiplayerSynchronizer node not found at '%s'." % node_path}

	if not (node is MultiplayerSynchronizer):
		return {"success": false, "message": "Node at '%s' is '%s', expected MultiplayerSynchronizer." % [node_path, node.get_class()]}

	var sync_node: MultiplayerSynchronizer = node
	var changes = []

	if params.has("root_path") and params["root_path"] != null:
		sync_node.root_path = NodePath(str(params["root_path"]))
		changes.append("Root Path: %s" % str(sync_node.root_path))

	if params.has("replication_interval") and params["replication_interval"] != null:
		sync_node.replication_interval = float(params["replication_interval"])
		changes.append("Replication Interval: %.3fs" % sync_node.replication_interval)

	if sync_node.replication_config == null:
		sync_node.replication_config = SceneReplicationConfig.new()

	var rep_config: SceneReplicationConfig = sync_node.replication_config

	if bool(params.get("clear_properties", false)):
		var props = rep_config.get_properties()
		for p in props:
			rep_config.remove_property(p)
		changes.append("Cleared replication properties")

	var props_to_set = params.get("properties", [])
	var set_count = 0
	if props_to_set is Array:
		for p in props_to_set:
			if p is Dictionary:
				var p_path = str(p.get("path", "")).strip_edges()
				if p_path != "":
					var np = NodePath(p_path)
					if not rep_config.has_property(np):
						rep_config.add_property(np)
					var spawn = bool(p.get("spawn", true))
					var sync = bool(p.get("sync", true))
					var watch = bool(p.get("watch", false))
					rep_config.property_set_spawn(np, spawn)
					rep_config.property_set_sync(np, sync)
					rep_config.property_set_watch(np, watch)
					set_count += 1
		if set_count > 0:
			changes.append("Configured %d replication properties" % set_count)

	var total_props = rep_config.get_properties().size()

	return {
		"success": true,
		"message": "Configured MultiplayerSynchronizer '%s': %s." % [sync_node.name, ", ".join(changes) if changes.size() > 0 else "No modifications"],
		"data": {
			"synchronizer_name": sync_node.name,
			"synchronizer_path": str(root.get_path_to(sync_node)),
			"root_path": str(sync_node.root_path),
			"replication_interval": sync_node.replication_interval,
			"total_properties": total_props,
			"changes_applied": changes
		}
	}

func simulate_network_conditions(params: Dictionary) -> Dictionary:
	_simulated_latency_ms = int(params.get("latency_ms", 0))
	_simulated_packet_loss = float(params.get("packet_loss_percent", 0.0))
	_simulated_jitter_ms = int(params.get("jitter_ms", 0))
	_simulated_offline = bool(params.get("offline_mode", false))

	return {
		"success": true,
		"message": "Configured simulated network conditions: Latency %dms, Packet Loss %.1f%%, Jitter %dms, Offline: %s." % [
			_simulated_latency_ms, _simulated_packet_loss, _simulated_jitter_ms, str(_simulated_offline)
		],
		"data": {
			"latency_ms": _simulated_latency_ms,
			"packet_loss_percent": _simulated_packet_loss,
			"jitter_ms": _simulated_jitter_ms,
			"offline_mode": _simulated_offline,
			"status": "SIMULATION_ACTIVE" if (_simulated_latency_ms > 0 or _simulated_packet_loss > 0.0 or _simulated_offline) else "NORMAL"
		}
	}
