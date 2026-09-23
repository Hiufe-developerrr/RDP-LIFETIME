# 08 - render environment (not exported): stubble field ground, sun, cameras.
TAG = "env"
purge_part(TAG)
E = coll("Env_render")


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)


# ground: stubble field with soil showing through
m = D.materials.get("Env_stubble") or D.materials.new("Env_stubble")
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
tc = nt.nodes.new('ShaderNodeTexCoord')
n1 = nt.nodes.new('ShaderNodeTexNoise')
n1.inputs['Scale'].default_value = 0.35
n1.inputs['Detail'].default_value = 6
n2 = nt.nodes.new('ShaderNodeTexNoise')
n2.inputs['Scale'].default_value = 60.0
n2.inputs['Detail'].default_value = 3
mp = nt.nodes.new('ShaderNodeMapping')
mp.inputs['Scale'].default_value = (1.0, 9.0, 1.0)
n3 = nt.nodes.new('ShaderNodeTexNoise')
n3.inputs['Scale'].default_value = 25.0
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.35
ramp.color_ramp.elements[0].color = srgb('#5E4A32')
ramp.color_ramp.elements[1].position = 0.62
ramp.color_ramp.elements[1].color = srgb('#C9AE74')
mix = nt.nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'
mix.inputs[7].default_value = srgb('#A88E5A')
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.6
L = nt.links.new
L(tc.outputs['Object'], n1.inputs['Vector'])
L(tc.outputs['Object'], mp.inputs['Vector'])
L(mp.outputs['Vector'], n3.inputs['Vector'])
L(tc.outputs['Object'], n2.inputs['Vector'])
L(n3.outputs['Fac'], ramp.inputs['Fac'])
L(ramp.outputs['Color'], mix.inputs[6])
L(n1.outputs['Fac'], mix.inputs[0])
L(mix.outputs[2], bsdf.inputs['Base Color'])
L(n2.outputs['Fac'], bump.inputs['Height'])
L(bump.outputs['Normal'], bsdf.inputs['Normal'])
bsdf.inputs['Roughness'].default_value = 0.95
L(bsdf.outputs['BSDF'], out.inputs['Surface'])
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=400.0)
g = make_obj("env_ground", bm, [m], E, TAG, smooth=None, wnormal=False)

sun_d = D.lights.get("env_sun") or D.lights.new("env_sun", 'SUN')
sun_d.energy = 3.2
sun_d.angle = radians(1.2)
sun_d.color = (1.0, 0.96, 0.9)
sun = D.objects.new("env_sun", sun_d)
E.objects.link(sun)
sun.rotation_euler = (radians(48), 0.0, radians(-38))
sun["z050_part"] = TAG

CAMS = {
    "cam_front_left": ((9.2, -9.6, 3.3), (0.1, 0.4, 1.45), 35),
    "cam_rear_right": ((-8.2, 10.4, 3.4), (0.0, 1.9, 1.55), 35),
    "cam_side_left": ((17.5, 0.6, 1.9), (0.0, 0.6, 1.75), 55),
    "cam_operator": ((3.9, -4.9, 4.4), (0.0, -0.95, 2.65), 40),
    "cam_header": ((3.6, -6.4, 1.9), (0.9, -2.7, 0.55), 38),
}
for name, (loc, tgt, lens) in CAMS.items():
    cd = D.cameras.get(name) or D.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 300
    cam = D.objects.new(name, cd)
    E.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam["z050_part"] = TAG
bpy.context.scene.camera = D.objects["cam_front_left"]
print("render env ready:", list(CAMS))
