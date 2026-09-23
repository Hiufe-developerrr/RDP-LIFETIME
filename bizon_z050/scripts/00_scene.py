# 00 - scene setup: clean scene, units, collections, render settings, world.
import os

for o in list(D.objects):
    D.objects.remove(o, do_unlink=True)
for block in (D.meshes, D.curves, D.cameras, D.lights):
    for b in list(block):
        if b.users == 0:
            block.remove(b)

scn = bpy.context.scene
scn.name = "Bizon_Z050_Super"
us = scn.unit_settings
us.system = 'METRIC'
us.scale_length = 1.0
us.length_unit = 'METERS'

root = coll("Z050_combine")
coll("Z050_header420")
coll("Z050_collision")
coll("Env_render")
default = D.collections.get("Collection")
if default is not None and not default.objects and not default.children:
    D.collections.remove(default)

r = scn.render
r.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = 96
scn.cycles.preview_samples = 16
scn.cycles.use_denoising = True
scn.cycles.denoiser = 'OPENIMAGEDENOISE'
scn.cycles.max_bounces = 6
scn.cycles.transparent_max_bounces = 8
r.resolution_x, r.resolution_y, r.resolution_percentage = 1600, 900, 100
r.film_transparent = False
scn.view_settings.view_transform = 'AgX'
try:
    scn.view_settings.look = 'AgX - Medium High Contrast'
except TypeError:
    pass

world = D.worlds.get("Z050_world") or D.worlds.new("Z050_world")
scn.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld')
bg = nt.nodes.new('ShaderNodeBackground')
hdri = "/opt/bizon_runtime/hdri/sky_2k.hdr"
if os.path.exists(hdri):
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = D.images.load(hdri, check_existing=True)
    mp = nt.nodes.new('ShaderNodeMapping')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp.inputs['Rotation'].default_value[2] = radians(115)
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0
else:
    sky = nt.nodes.new('ShaderNodeTexSky')
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

print("scene ready:", scn.name, [c.name for c in scn.collection.children])
