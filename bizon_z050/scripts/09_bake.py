# 09 - bake the procedural weathered materials into FS25 texture atlases.
# Runs from a timer (long job); progress in textures/bake_status.txt.
# Per atlas: <atlas>_diffuse.png (sRGB), <atlas>_normal.png (tangent, OpenGL
# Y+), <atlas>_specular.png (R = smoothness, G = metallic, B = AO).
import os
import time
import numpy as np

OUT = "/tmp/hoplite/workspace/bizon_z050/textures"
ATLASES = globals().get("ATLASES") or {"bizonZ050": 2048, "header420": 2048, "bizonZ050_tires": 1024}
SAMPLES = globals().get("SAMPLES") or 8
os.makedirs(OUT, exist_ok=True)
STATUS = os.path.join(OUT, "bake_status.txt")


def log(msg):
    with open(STATUS, "a") as f:
        f.write(msg + "\n")


def view3d_ctx():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                reg = next(r for r in area.regions if r.type == 'WINDOW')
                return dict(window=win, area=area, region=reg, screen=win.screen)
    return {}


def atlas_objs(name):
    return [o for o in D.objects if o.type == 'MESH' and o.get("fs_atlas") == name]


def atlas_mats(objs):
    ms = []
    for o in objs:
        for s in o.material_slots:
            if s.material and s.material not in ms:
                ms.append(s.material)
    return ms


def new_img(name, res, non_color):
    old = D.images.get(name)
    if old:
        D.images.remove(old)
    img = D.images.new(name, res, res, alpha=False, float_buffer=non_color)
    img.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
    return img


def target(mats, img):
    for m in mats:
        nt = m.node_tree
        n = nt.nodes.get("BAKE_TARGET") or nt.nodes.new('ShaderNodeTexImage')
        n.name = n.label = "BAKE_TARGET"
        n.location = (700, -420)
        n.image = img
        for x in nt.nodes:
            x.select = False
        n.select = True
        nt.nodes.active = n


def emit(mats, socket):
    for m in mats:
        nt = m.node_tree
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        if socket is None:
            nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            continue
        em = nt.nodes.get("BAKE_EMIT") or nt.nodes.new('ShaderNodeEmission')
        em.name = "BAKE_EMIT"
        em.location = (500, -250)
        grp = nt.nodes.get("Weathering")
        if grp is not None:
            nt.links.new(grp.outputs[socket], em.inputs['Color'])
        else:
            # clear/lamp materials: bake their flat colour as an opaque stand-in
            for l in list(em.inputs['Color'].links):
                nt.links.remove(l)
            if socket == "Color":
                em.inputs['Color'].default_value = bsdf.inputs['Base Color'].default_value
            else:
                v = 0.1 if socket == "Roughness" else 0.0
                em.inputs['Color'].default_value = (v, v, v, 1.0)
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])


def bake(objs, btype, samples):
    scn = bpy.context.scene
    scn.cycles.samples = samples
    for o in D.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    kw = dict(type=btype, margin=6, margin_type='EXTEND', use_clear=True, target='IMAGE_TEXTURES')
    if btype == 'NORMAL':
        kw.update(normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z')
    with bpy.context.temp_override(**view3d_ctx(), active_object=objs[0], selected_objects=objs):
        bpy.ops.object.bake(**kw)


def pixels(img):
    a = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)


def save(img, path):
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()


def run():
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    scn.cycles.device = 'CPU'
    scn.world.light_settings.distance = 0.6
    for name, res in ATLASES.items():
        objs = atlas_objs(name)
        if not objs:
            continue
        mats = atlas_mats(objs)
        t0 = time.time()
        maps = {}
        for key, sock, nc in (("diffuse", "Color", False), ("rough", "Roughness", True), ("metal", "Metallic", True)):
            img = new_img(f"{name}_{key}", res, nc)
            target(mats, img)
            emit(mats, sock)
            bake(objs, 'EMIT', SAMPLES)
            maps[key] = img
            log(f"{name} {key} {time.time() - t0:.0f}s")
        emit(mats, None)
        img = new_img(f"{name}_normal", res, True)
        target(mats, img)
        bake(objs, 'NORMAL', SAMPLES)
        maps["normal"] = img
        log(f"{name} normal {time.time() - t0:.0f}s")
        img = new_img(f"{name}_ao", res, True)
        target(mats, img)
        bake(objs, 'AO', max(12, SAMPLES))
        maps["ao"] = img
        log(f"{name} ao {time.time() - t0:.0f}s")
        # pack FS-style specular: R smoothness, G metallic, B ambient occlusion
        r, m, ao = pixels(maps["rough"]), pixels(maps["metal"]), pixels(maps["ao"])
        spec = np.ones_like(r)
        spec[..., 0] = 1.0 - r[..., 0]
        spec[..., 1] = m[..., 0]
        spec[..., 2] = ao[..., 0]
        simg = new_img(f"{name}_specular", res, False)
        simg.colorspace_settings.name = 'Non-Color'
        simg.pixels.foreach_set(spec.ravel())
        save(maps["diffuse"], os.path.join(OUT, f"{name}_diffuse.png"))
        save(maps["normal"], os.path.join(OUT, f"{name}_normal.png"))
        save(simg, os.path.join(OUT, f"{name}_specular.png"))
        for k in ("rough", "metal", "ao"):
            D.images.remove(maps[k])
        for m_ in mats:
            n = m_.node_tree.nodes.get("BAKE_TARGET")
            if n:
                m_.node_tree.nodes.remove(n)
            e = m_.node_tree.nodes.get("BAKE_EMIT")
            if e:
                m_.node_tree.nodes.remove(e)
        log(f"{name} DONE {time.time() - t0:.0f}s")
    log("ALL DONE")
    return None


open(STATUS, "w").write("started\n")
bpy.app.timers.register(run, first_interval=0.5)
print("bake job queued:", ATLASES, "samples", SAMPLES)
