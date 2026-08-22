@tool
extends RefCounted

## Operations for Godot CSG Whiteboxing & Procedural Mesh Generation.

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

func create_csg_shape(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var shape_type = str(params.get("shape_type", "box")).to_lower()
	var node_name = str(params.get("node_name", "CSGShape"))
	var op_str = str(params.get("operation", "union")).to_lower()
	var use_col = bool(params.get("use_collision", true))

	var csg_node: CSGShape3D = null

	match shape_type:
		"box":
			var b = CSGBox3D.new()
			var sz = params.get("size", [2.0, 2.0, 2.0])
			if sz is Array and sz.size() >= 3:
				b.size = Vector3(float(sz[0]), float(sz[1]), float(sz[2]))
			csg_node = b
		"cylinder":
			var c = CSGCylinder3D.new()
			if params.has("radius"):
				c.radius = float(params["radius"])
			if params.has("height"):
				c.height = float(params["height"])
			csg_node = c
		"sphere":
			var s = CSGSphere3D.new()
			if params.has("radius"):
				s.radius = float(params["radius"])
			csg_node = s
		"polygon":
			var p = CSGPolygon3D.new()
			var pts = params.get("polygon_points", [])
			if pts is Array and pts.size() >= 3:
				var varr = PackedVector2Array()
				for pt in pts:
					if pt is Array and pt.size() >= 2:
						varr.append(Vector2(float(pt[0]), float(pt[1])))
				p.polygon = varr
			csg_node = p
		"torus":
			var t = CSGTorus3D.new()
			if params.has("radius"):
				t.outer_radius = float(params["radius"])
			csg_node = t
		"combiner":
			csg_node = CSGCombiner3D.new()
		_:
			var b_def = CSGBox3D.new()
			csg_node = b_def

	csg_node.name = node_name

	match op_str:
		"intersection":
			csg_node.operation = CSGShape3D.OPERATION_INTERSECTION
		"subtraction":
			csg_node.operation = CSGShape3D.OPERATION_SUBTRACTION
		_:
			csg_node.operation = CSGShape3D.OPERATION_UNION

	csg_node.use_collision = use_col

	var pos = params.get("position")
	if pos is Array and pos.size() >= 3:
		csg_node.position = Vector3(float(pos[0]), float(pos[1]), float(pos[2]))

	var rot = params.get("rotation_deg")
	if rot is Array and rot.size() >= 3:
		csg_node.rotation_degrees = Vector3(float(rot[0]), float(rot[1]), float(rot[2]))

	var mat_path = params.get("material_path")
	if mat_path != null and str(mat_path).strip_edges() != "":
		var mstr = str(mat_path).strip_edges()
		if ResourceLoader.exists(mstr):
			csg_node.material = ResourceLoader.load(mstr)

	parent_node.add_child(csg_node)
	csg_node.owner = root

	return {
		"success": true,
		"message": "Created CSG shape '%s' (%s, op: %s) under '%s'." % [csg_node.name, shape_type.to_upper(), op_str.to_upper(), parent_node.name],
		"data": {
			"node_name": csg_node.name,
			"node_path": str(root.get_path_to(csg_node)),
			"shape_type": shape_type,
			"operation": op_str,
			"use_collision": use_col,
			"position": [csg_node.position.x, csg_node.position.y, csg_node.position.z]
		}
	}

func generate_procedural_mesh(params: Dictionary) -> Dictionary:
	var root = _get_scene_root()
	if not root:
		return {"success": false, "message": "No active scene open in the editor."}

	var parent_path = str(params.get("parent_path", "."))
	var parent_node = _find_node(parent_path, root)
	if not parent_node:
		return {"success": false, "message": "Parent node not found at '%s'." % parent_path}

	var mesh_type = str(params.get("mesh_type", "grid")).to_lower()
	var node_name = str(params.get("node_name", "ProceduralMesh"))
	var gen_normals = bool(params.get("generate_normals", true))
	var gen_tangents = bool(params.get("generate_tangents", true))
	var save_path = params.get("save_to_resource_path")

	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	var vertex_count = 0

	match mesh_type:
		"grid":
			var sz = params.get("size", [10.0, 10.0])
			var sx = float(sz[0]) if (sz is Array and sz.size() >= 1) else 10.0
			var sz_val = float(sz[1]) if (sz is Array and sz.size() >= 2) else 10.0
			var subs = params.get("subdivisions", [4, 4])
			var nx = int(subs[0]) if (subs is Array and subs.size() >= 1) else 4
			var nz = int(subs[1]) if (subs is Array and subs.size() >= 2) else 4

			var hx = sx * 0.5
			var hz = sz_val * 0.5

			for z in range(nz):
				for x in range(nx):
					var x0 = -hx + (float(x) / nx) * sx
					var x1 = -hx + (float(x + 1) / nx) * sx
					var z0 = -hz + (float(z) / nz) * sz_val
					var z1 = -hz + (float(z + 1) / nz) * sz_val

					var u0 = float(x) / nx
					var u1 = float(x + 1) / nx
					var v0 = float(z) / nz
					var v1 = float(z + 1) / nz

					# Triangle 1
					st.set_uv(Vector2(u0, v0))
					st.add_vertex(Vector3(x0, 0, z0))
					st.set_uv(Vector2(u1, v0))
					st.add_vertex(Vector3(x1, 0, z0))
					st.set_uv(Vector2(u1, v1))
					st.add_vertex(Vector3(x1, 0, z1))

					# Triangle 2
					st.set_uv(Vector2(u0, v0))
					st.add_vertex(Vector3(x0, 0, z0))
					st.set_uv(Vector2(u1, v1))
					st.add_vertex(Vector3(x1, 0, z1))
					st.set_uv(Vector2(u0, v1))
					st.add_vertex(Vector3(x0, 0, z1))

					vertex_count += 6

		"pyramid":
			var sz = params.get("size", [2.0, 3.0, 2.0])
			var sx = float(sz[0]) if (sz is Array and sz.size() >= 1) else 2.0
			var sy = float(sz[1]) if (sz is Array and sz.size() >= 2) else 3.0
			var sz_val = float(sz[2]) if (sz is Array and sz.size() >= 3) else 2.0
			var hx = sx * 0.5
			var hz = sz_val * 0.5
			var apex = Vector3(0, sy, 0)

			# 4 Sides
			var corners = [
				Vector3(-hx, 0, -hz), Vector3(hx, 0, -hz),
				Vector3(hx, 0, hz), Vector3(-hx, 0, hz)
			]
			for i in range(4):
				var c1 = corners[i]
				var c2 = corners[(i + 1) % 4]
				st.set_uv(Vector2(0, 0)); st.add_vertex(c1)
				st.set_uv(Vector2(1, 0)); st.add_vertex(c2)
				st.set_uv(Vector2(0.5, 1)); st.add_vertex(apex)
				vertex_count += 3

		"custom_vertices":
			var verts = params.get("vertices", [])
			var inds = params.get("indices", [])
			if verts is Array:
				if inds is Array and inds.size() > 0:
					for idx in inds:
						var i = int(idx)
						if i >= 0 and i < verts.size():
							var v = verts[i]
							if v is Array and v.size() >= 3:
								st.add_vertex(Vector3(float(v[0]), float(v[1]), float(v[2])))
								vertex_count += 1
				else:
					for v in verts:
						if v is Array and v.size() >= 3:
							st.add_vertex(Vector3(float(v[0]), float(v[1]), float(v[2])))
							vertex_count += 1
		_:
			# Default cube triangle
			st.add_vertex(Vector3(-1, 0, -1))
			st.add_vertex(Vector3(1, 0, -1))
			st.add_vertex(Vector3(1, 0, 1))
			vertex_count += 3

	if gen_normals:
		st.generate_normals()
	if gen_tangents:
		st.generate_tangents()

	var array_mesh = st.commit()

	if save_path != null and str(save_path).strip_edges() != "":
		var sp = str(save_path).strip_edges()
		DirAccess.make_dir_recursive_absolute(sp.get_base_dir())
		ResourceSaver.save(array_mesh, sp)

	var mi = MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = array_mesh

	var mat_path = params.get("material_path")
	if mat_path != null and str(mat_path).strip_edges() != "":
		var mp = str(mat_path).strip_edges()
		if ResourceLoader.exists(mp):
			mi.material_override = ResourceLoader.load(mp)

	parent_node.add_child(mi)
	mi.owner = root

	return {
		"success": true,
		"message": "Generated procedural %s mesh '%s' with %d vertices under '%s'." % [mesh_type.to_upper(), mi.name, vertex_count, parent_node.name],
		"data": {
			"node_name": mi.name,
			"node_path": str(root.get_path_to(mi)),
			"mesh_type": mesh_type,
			"mesh_vertex_count": vertex_count,
			"saved_resource_path": str(save_path) if save_path else ""
		}
	}

