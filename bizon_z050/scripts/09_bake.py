# 09 - bake the procedural weathered materials into FS25 texture atlases.
# Per atlas: emission bake of the colour, emission bake of roughness /
# metallic / height packed in RGB, AO bake at half resolution; the tangent
# space normal map (OpenGL, Y+) is derived from the baked height with numpy.
# Outputs <atlas>_diffuse.png, <atlas>_normal.png and <atlas>_specular.png
# (R = smoothness, G = metallic, B = AO). Runs from a timer; progress in
# textures/bake_status.txt.
import os
import time
import numpy as np

OUT = "/tmp/hoplite/workspace/bizon_z050/textures"
ATLASES = globals().get("ATLASES") or {"bizonZ050": 4096, "bizonZ050_details": 4096, "header420": 4096,
                                       "bizonZ050_tires": 2048}
SAMPLES = globals().get("SAMPLES") or 5
BUMP_DIST = 0.004            # Bump node distance used by 01_materials
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


def new_img(name, res, float_buf, non_color):
    old = D.images.get(name)
    if old:
        D.images.remove(old)
    img = D.images.new(name, res, res, alpha=False, float_buffer=float_buf)
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


def setup(mats, mode):
    """mode: 'color', 'rmh' or None (restore the normal BSDF output)."""
    for m in mats:
        nt = m.node_tree
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        if mode is None:
            for nm in ("BAKE_EMIT", "BAKE_COMB", "BAKE_H", "BAKE_TARGET"):
                n = nt.nodes.get(nm)
                if n:
                    nt.nodes.remove(n)
            nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            continue
        em = nt.nodes.get("BAKE_EMIT") or nt.nodes.new('ShaderNodeEmission')
        em.name = "BAKE_EMIT"
        for l in list(em.inputs['Color'].links):
            nt.links.remove(l)
        grp = nt.nodes.get("Weathering")
        if grp is not None and mode == "color":
            nt.links.new(grp.outputs["Color"], em.inputs["Color"])
        elif grp is not None:
            comb = nt.nodes.get("BAKE_COMB") or nt.nodes.new('ShaderNodeCombineColor')
            comb.name = "BAKE_COMB"
            h = nt.nodes.get("BAKE_H") or nt.nodes.new('ShaderNodeMath')
            h.name = "BAKE_H"
            h.operation = 'MULTIPLY_ADD'
            h.use_clamp = True
            nt.links.new(grp.outputs["Height"], h.inputs[0])
            h.inputs[1].default_value = float(m.get("bump", 0.35))
            h.inputs[2].default_value = 0.5
            nt.links.new(grp.outputs["Roughness"], comb.inputs[0])
            nt.links.new(grp.outputs["Metallic"], comb.inputs[1])
            nt.links.new(h.outputs[0], comb.inputs[2])
            nt.links.new(comb.outputs[0], em.inputs["Color"])
        elif mode == "color":
            em.inputs['Color'].default_value = bsdf.inputs['Base Color'].default_value
        else:
            em.inputs['Color'].default_value = (0.1, 0.0, 0.5, 1.0)
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])


def bake(objs, btype, samples, margin):
    scn = bpy.context.scene
    scn.cycles.samples = samples
    for o in D.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    with bpy.context.temp_override(**view3d_ctx(), active_object=objs[0], selected_objects=objs):
        bpy.ops.object.bake(type=btype, margin=margin, margin_type='EXTEND', use_clear=True, target='IMAGE_TEXTURES')


def pixels(img):
    a = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)


def texel_size(objs, res):
    """World size of one texel (uniform density after average_islands_scale)."""
    ratios = []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        loops = np.empty(n * 3, dtype=np.int32)
        me.loop_triangles.foreach_get("loops", loops)
        area = np.empty(n, dtype=np.float64)
        me.loop_triangles.foreach_get("area", area)
        uv = np.empty(len(me.loops) * 2, dtype=np.float64)
        me.uv_layers.active.data.foreach_get("uv", uv)
        t = uv.reshape(-1, 2)[loops].reshape(n, 3, 2)
        uva = 0.5 * np.abs((t[:, 1, 0] - t[:, 0, 0]) * (t[:, 2, 1] - t[:, 0, 1]) -
                           (t[:, 2, 0] - t[:, 0, 0]) * (t[:, 1, 1] - t[:, 0, 1]))
        ok = area > 1e-8
        ratios.append(uva[ok] / area[ok])
    r = np.median(np.concatenate(ratios))
    return 1.0 / (res * np.sqrt(r))


def normal_from_height(h, texel_m):
    d = (h - 0.5) * BUMP_DIST
    gx = (np.roll(d, -1, axis=1) - np.roll(d, 1, axis=1)) / (2.0 * texel_m)
    gy = (np.roll(d, -1, axis=0) - np.roll(d, 1, axis=0)) / (2.0 * texel_m)
    n = np.dstack((-gx, -gy, np.ones_like(d)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def save_rgb(name, res, rgb, non_color):
    img = new_img(name, res, False, non_color)
    px = np.ones((res, res, 4), dtype=np.float32)
    px[..., :3] = np.clip(rgb, 0.0, 1.0)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = os.path.join(OUT, name + ".png")
    img.file_format = 'PNG'
    img.save()
    D.images.remove(img)


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
        margin = max(4, res // 512)
        t0 = time.time()
        dif = new_img(name + "_diffuse", res, False, False)
        target(mats, dif)
        setup(mats, "color")
        bake(objs, 'EMIT', SAMPLES, margin)
        dif.filepath_raw = os.path.join(OUT, name + "_diffuse.png")
        dif.file_format = 'PNG'
        dif.save()
        log(f"{name} diffuse {time.time() - t0:.0f}s")
        rmh = new_img(name + "_rmh", res, True, True)
        target(mats, rmh)
        setup(mats, "rmh")
        bake(objs, 'EMIT', SAMPLES, margin)
        log(f"{name} rough/metal/height {time.time() - t0:.0f}s")
        setup(mats, None)
        k_ao = 4 if res >= 4096 else 2                  # AO is low frequency: bake small, upscale
        ao = new_img(name + "_ao", res // k_ao, True, True)
        target(mats, ao)
        bake(objs, 'AO', 8, max(2, margin // 2))
        setup(mats, None)
        log(f"{name} ao {time.time() - t0:.0f}s")
        p = pixels(rmh)
        a = pixels(ao)[..., 0]
        a = np.repeat(np.repeat(a, k_ao, axis=0), k_ao, axis=1)
        for _ in range(k_ao // 2):
            a = (a + np.roll(a, 1, 0) + np.roll(a, 1, 1) + np.roll(np.roll(a, 1, 0), 1, 1)) * 0.25
        spec = np.dstack((1.0 - p[..., 0], p[..., 1], a))
        save_rgb(name + "_specular", res, spec, True)
        tx = texel_size(objs, res)
        save_rgb(name + "_normal", res, normal_from_height(p[..., 2], tx), True)
        for im in (dif, rmh, ao):
            D.images.remove(im)
        log(f"{name} DONE {time.time() - t0:.0f}s (texel {tx * 1000:.2f} mm)")
    log("ALL DONE")
    return None


open(STATUS, "w").write("started\n")
bpy.app.timers.register(run, first_interval=0.5)
print("bake job queued:", ATLASES, "samples", SAMPLES)
