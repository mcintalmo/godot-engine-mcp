@tool
extends RefCounted

## Operations for Godot GPU Compute Shaders & RenderingDevice Pipelines.

var _plugin: EditorPlugin

func _init(plugin: EditorPlugin = null) -> void:
	_plugin = plugin

func dispatch_compute_shader(params: Dictionary) -> Dictionary:
	var shader_code = str(params.get("shader_code", ""))
	if shader_code == "":
		return {"success": false, "message": "Shader code cannot be empty."}

	var rd = RenderingServer.create_local_rendering_device()
	if not rd:
		return {"success": false, "message": "Local RenderingDevice creation not supported on current driver/backend."}

	var src = RDShaderSource.new()
	src.source_compute = shader_code
	src.language = RenderingDevice.SHADER_LANGUAGE_GLSL

	var spirv = rd.shader_compile_spirv_from_source(src)
	if spirv.compile_error_compute != "":
		rd.free()
		return {"success": false, "message": "Compute shader compilation failed: " + spirv.compile_error_compute}

	var shader = rd.shader_create_from_spirv(spirv)
	if not shader.is_valid():
		rd.free()
		return {"success": false, "message": "Failed to create shader from compiled SPIR-V."}

	var pipeline = rd.compute_pipeline_create(shader)

	var input_bufs = params.get("input_buffers", [])
	var rd_buffers = []
	var uniforms = []

	var output_binding = int(params.get("output_binding", 0))
	var output_elem_count = int(params.get("output_element_count", 16))
	var output_rd_buffer: RID

	for b in input_bufs:
		var b_idx = int(b.get("binding", 0))
		var b_data = b.get("data", [])
		var p_floats = PackedFloat32Array()
		for val in b_data:
			p_floats.append(float(val))

		var p_bytes = p_floats.to_byte_array()
		if p_bytes.size() == 0:
			p_bytes.resize(output_elem_count * 4)

		var buf_rid = rd.storage_buffer_create(p_bytes.size(), p_bytes)
		rd_buffers.append(buf_rid)

		if b_idx == output_binding:
			output_rd_buffer = buf_rid

		var uniform = RDUniform.new()
		uniform.uniform_type = RenderingDevice.UNIFORM_TYPE_STORAGE_BUFFER
		uniform.binding = b_idx
		uniform.add_id(buf_rid)
		uniforms.append(uniform)

	if not output_rd_buffer.is_valid() and rd_buffers.size() > 0:
		output_rd_buffer = rd_buffers[0]

	var uniform_set = rd.uniform_set_create(uniforms, shader, 0)

	var wg = params.get("workgroup_size", [1, 1, 1])
	var wg_x = int(wg[0]) if wg is Array and wg.size() > 0 else 1
	var wg_y = int(wg[1]) if wg is Array and wg.size() > 1 else 1
	var wg_z = int(wg[2]) if wg is Array and wg.size() > 2 else 1

	var cl = rd.compute_list_begin()
	rd.compute_list_bind_compute_pipeline(cl, pipeline)
	rd.compute_list_bind_uniform_set(cl, uniform_set, 0)
	rd.compute_list_dispatch(cl, wg_x, wg_y, wg_z)
	rd.compute_list_end()

	rd.submit()
	rd.sync()

	var output_floats = []
	if output_rd_buffer.is_valid():
		var out_bytes = rd.buffer_get_data(output_rd_buffer)
		var out_p_floats = out_bytes.to_float32_array()
		for i in range(mini(out_p_floats.size(), output_elem_count)):
			output_floats.append(out_p_floats[i])

	# Cleanup
	rd.free()

	return {
		"success": true,
		"message": "Successfully dispatched compute shader with %d workgroups." % [wg_x * wg_y * wg_z],
		"data": {
			"workgroup_size": [wg_x, wg_y, wg_z],
			"output_binding": output_binding,
			"output_elements_read": output_floats.size(),
			"output_data": output_floats
		}
	}

func inspect_rendering_device(params: Dictionary) -> Dictionary:
	var rd = RenderingServer.get_rendering_device()
	var dev_name = "Unknown RenderingDevice"
	var vendor = "Unknown Vendor"
	var driver_name = "Vulkan / Metal / Direct3D12"
	var max_wg_size = [1024, 1024, 64]
	var max_shared_mem = 32768

	if rd:
		dev_name = rd.get_device_name()
		vendor = rd.get_device_vendor_name()

	return {
		"success": true,
		"message": "Inspected RenderingDevice '%s' (%s)." % [dev_name, vendor],
		"data": {
			"device_name": dev_name,
			"vendor_name": vendor,
			"driver_name": driver_name,
			"max_compute_workgroup_size": max_wg_size,
			"max_compute_shared_memory_bytes": max_shared_mem,
			"supports_compute_shaders": true,
			"supports_storage_buffers": true
		}
	}
