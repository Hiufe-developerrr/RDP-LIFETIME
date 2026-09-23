# 07b - non-overlapping UV atlases (smart project + average scale + pack).
# Set ATLAS = "<name>" before this script to unwrap a single atlas.
import time

ONLY = globals().get("ATLAS")


def view3d_ctx():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                reg = next(r for r in area.regions if r.type == 'WINDOW')
                return dict(window=win, area=area, region=reg, screen=win.screen)
    return {}


THIN = {"bizonZ050_details": ("Z050_wire", "Z050_hose", "Z050_belt", "Z050_chain", "Z050_steel"),
        "header420": ("Z050_paint_gray", "Z050_hose", "Z050_belt", "Z050_chain")}


def shrink_thin(objs, prefixes, k=0.25):
    """Long thin parts (cables, hoses, chains, tine bars) would dictate the
    atlas scale as metre-long UV strips; their islands are packed smaller."""
    for o in objs:
        idx = {i for i, m in enumerate(o.data.materials) if m and m.name.startswith(prefixes)}
        if not idx:
            continue
        uv = o.data.uv_layers.active.data
        for p in o.data.polygons:
            if p.material_index in idx:
                for li in p.loop_indices:
                    uv[li].uv = uv[li].uv * k


def unwrap(objs, margin, shape, thin=None):
    for o in D.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")
    bpy.context.view_layer.objects.active = objs[0]
    with bpy.context.temp_override(**view3d_ctx()):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=radians(66), island_margin=0.0, area_weight=0.0,
                                 correct_aspect=True, scale_to_bounds=False)
        bpy.ops.uv.average_islands_scale()
        if thin:
            bpy.ops.object.mode_set(mode='OBJECT')
            shrink_thin(objs, thin)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(rotate=True, rotate_method='ANY', scale=True, margin_method='FRACTION',
                                margin=margin, shape_method=shape)
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in objs:
        o.select_set(False)


def coverage(objs):
    tot = 0.0
    for o in objs:
        uv = o.data.uv_layers.active.data
        for p in o.data.polygons:
            pts = [uv[i].uv for i in p.loop_indices]
            a = 0.0
            for i in range(len(pts)):
                a += pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y
            tot += abs(a) / 2
    return tot


PLAN = {"bizonZ050": (0.0012, 'CONCAVE'), "header420": (0.0012, 'CONCAVE'),
        "bizonZ050_details": (0.002, 'CONCAVE'), "bizonZ050_tires": (0.002, 'CONCAVE')}
for name, (margin, shape) in PLAN.items():
    if ONLY and name != ONLY:
        continue
    objs = [o for o in D.objects if o.type == 'MESH' and o.get("fs_atlas") == name]
    if not objs:
        continue
    t0 = time.time()
    unwrap(objs, margin, shape, THIN.get(name))
    print(f"{name}: {len(objs)} objects, coverage {coverage(objs):.2f}, {time.time() - t0:.1f}s")
if not ONLY:
    lo = D.objects.get("bizonZ050_lights")
    if lo:
        unwrap([lo], 0.004, 'AABB')
