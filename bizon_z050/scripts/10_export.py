# 10 - FS25 package: baked atlas materials (+ switch script stored in the
# .blend), FBX export with the baked materials, self-contained .blend save.
import os

BASE = "/tmp/hoplite/workspace/bizon_z050"
TEX = os.path.join(BASE, "textures")
ATLASES = ["bizonZ050", "header420", "bizonZ050_tires"]

SWITCH = '''# Switch the Bizon Z050 meshes between the procedural (weathered, Cycles)
# materials and the baked FS25 atlas materials. Run from the Text Editor.
import bpy

MODE = "BAKED"  # "BAKED" before the GIANTS I3D / FBX export, "PROCEDURAL" to go back


def to_baked():
    for ob in bpy.data.objects:
        atlas = ob.get("fs_atlas")
        if ob.type != 'MESH' or not atlas or "proc_mats" in ob:
            continue
        me = ob.data
        ob["proc_mats"] = [m.name if m else "" for m in me.materials]
        attr = me.attributes.get("proc_mat_index") or me.attributes.new("proc_mat_index", 'INT', 'FACE')
        idx = [0] * len(me.polygons)
        me.polygons.foreach_get("material_index", idx)
        attr.data.foreach_set("value", idx)
        me.materials.clear()
        me.materials.append(bpy.data.materials[atlas + "_mat"])
        me.polygons.foreach_set("material_index", [0] * len(me.polygons))
        me.update()


def to_procedural():
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or "proc_mats" not in ob:
            continue
        me = ob.data
        me.materials.clear()
        for n in ob["proc_mats"]:
            me.materials.append(bpy.data.materials.get(n))
        attr = me.attributes.get("proc_mat_index")
        if attr is not None:
            idx = [0] * len(me.polygons)
            attr.data.foreach_get("value", idx)
            me.polygons.foreach_set("material_index", idx)
            me.attributes.remove(attr)
        del ob["proc_mats"]
        me.update()


if MODE == "BAKED":
    to_baked()
else:
    to_procedural()
'''


def load(path, non_color):
    im = D.images.load(path, check_existing=True)
    im.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
    return im


def baked_mat(atlas):
    name = atlas + "_mat"
    m = D.materials.get(name) or D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (650, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (350, 0)
    td = nt.nodes.new('ShaderNodeTexImage')
    td.image = load(os.path.join(TEX, atlas + "_diffuse.png"), False)
    td.location = (-450, 320)
    ts = nt.nodes.new('ShaderNodeTexImage')
    ts.image = load(os.path.join(TEX, atlas + "_specular.png"), True)
    ts.location = (-450, 0)
    tn = nt.nodes.new('ShaderNodeTexImage')
    tn.image = load(os.path.join(TEX, atlas + "_normal.png"), True)
    tn.location = (-450, -320)
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    sep.location = (-150, 0)
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    inv.location = (80, 60)
    nmap = nt.nodes.new('ShaderNodeNormalMap')
    nmap.location = (-150, -320)
    L = nt.links.new
    L(td.outputs['Color'], bsdf.inputs['Base Color'])
    L(ts.outputs['Color'], sep.inputs['Color'])
    L(sep.outputs['Red'], inv.inputs[1])
    L(inv.outputs[0], bsdf.inputs['Roughness'])
    L(sep.outputs['Green'], bsdf.inputs['Metallic'])
    L(tn.outputs['Color'], nmap.inputs['Color'])
    L(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    L(bsdf.outputs['BSDF'], out.inputs['Surface'])
    m.use_fake_user = True
    return m


for a in ATLASES:
    baked_mat(a)
for m in D.materials:
    if m.name.startswith("Z050_"):
        m.use_fake_user = True
ng = D.node_groups.get("Z050_Weathering")
if ng:
    ng.use_fake_user = True

txt = D.texts.get("fs25_switch_materials.py") or D.texts.new("fs25_switch_materials.py")
txt.clear()
txt.write(SWITCH)
exec(compile(SWITCH, "switch", "exec"), {})  # -> baked atlas materials

# ---------------------------------------------------------------- FBX
os.makedirs(os.path.join(BASE, "export"), exist_ok=True)
sel = []
for cname in ("Z050_combine", "Z050_header420"):
    for o in D.collections[cname].all_objects:
        if o.type in ('MESH', 'EMPTY'):
            sel.append(o)
for o in D.objects:
    o.select_set(o in sel)
bpy.context.view_layer.objects.active = D.objects["bizonZ050"]
fbx = os.path.join(BASE, "export", "bizon_z050_super_fs25.fbx")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'EMPTY', 'MESH'},
                         use_mesh_modifiers=True, mesh_smooth_type='OFF', use_tspace=True,
                         use_custom_props=True, add_leaf_bones=False, bake_anim=False,
                         path_mode='RELATIVE', axis_forward='-Z', axis_up='Y',
                         apply_scale_options='FBX_SCALE_ALL')
print("fbx:", fbx, os.path.getsize(fbx))

exec(compile(SWITCH.replace('MODE = "BAKED"', 'MODE = "PROCEDURAL"'), "switch", "exec"), {})

# ---------------------------------------------------------------- .blend
scn = bpy.context.scene
w = scn.world
nt = w.node_tree
for n in list(nt.nodes):
    if n.type in ('TEX_ENVIRONMENT', 'MAPPING', 'TEX_COORD'):
        nt.nodes.remove(n)
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
sky = nt.nodes.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_elevation = radians(42)
sky.sun_rotation = radians(140)
nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 0.35
for im in list(D.images):
    if im.filepath and im.filepath.startswith("/opt/"):
        D.images.remove(im)
scn.camera = D.objects.get("cam_front_left")
for o in D.objects:
    o.select_set(False)
os.makedirs(os.path.join(BASE, "blend"), exist_ok=True)
path = os.path.join(BASE, "blend", "bizon_z050_super.blend")
bpy.ops.wm.save_as_mainfile(filepath=path, compress=True, relative_remap=True)
print("saved:", path, os.path.getsize(path))
