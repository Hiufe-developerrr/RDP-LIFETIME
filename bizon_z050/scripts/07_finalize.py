# 07 - FS25 preparation: apply modifiers, fold attached detail meshes into
# their moving parents, join static parts per texture atlas, FS-style
# hierarchy, collisions, viewport clean-up (collisions hidden, small empties).
# UVs are done by 07b_uv.py (separate MCP calls keep each step short).
TAG_ROOT = "final"
purge_part(TAG_ROOT)
CC = coll("Z050_combine")
CH = coll("Z050_header420")
CCOL = coll("Z050_collision")


def view3d_ctx():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                reg = next(r for r in area.regions if r.type == 'WINDOW')
                return dict(window=win, area=area, region=reg, screen=win.screen)
    return {}


def apply_mods(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        if ob.type != 'MESH' or not ob.modifiers:
            continue
        me = D.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        old = ob.data
        ob.modifiers.clear()
        ob.data = me
        if old.users == 0:
            D.meshes.remove(old)


def join(active, others):
    objs = [active] + [o for o in others if o is not active]
    if len(objs) > 1:
        with bpy.context.temp_override(**view3d_ctx(), active_object=active, object=active,
                                       selected_objects=objs, selected_editable_objects=objs):
            bpy.ops.object.join()
    return active


def join_named(name, objs):
    if not objs:
        return None
    ob = join(objs[0], objs[1:])
    ob.name = name
    ob.data.name = name
    return ob


def bake_local(ob):
    """Move a static child's local offset into its mesh (identity local transform)."""
    if ob.matrix_basis != Matrix.Identity(4):
        ob.data.transform(ob.matrix_basis)
        ob.matrix_basis = Matrix.Identity(4)


if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
apply_mods([o for o in D.objects if o.type == 'MESH' and o.get("z050_part")])

# Zero-area faces left by the bevel on tiny cylinders get huge UV islands
# (average_islands_scale divides by their area) and overwrite neighbours in
# the bake: dissolve them. N-gons are triangulated (the exporter does anyway).
for o in D.objects:
    if o.type == 'MESH' and o.get("z050_part"):
        bm_ = bmesh.new()
        bm_.from_mesh(o.data)
        bmesh.ops.dissolve_degenerate(bm_, dist=1e-6, edges=bm_.edges[:])
        tiny = [f for f in bm_.faces if f.calc_area() < 1e-9]
        if tiny:
            bmesh.ops.delete(bm_, geom=tiny, context='FACES')
        ng = [f for f in bm_.faces if len(f.verts) > 4]
        if ng:
            bmesh.ops.triangulate(bm_, faces=ng, quad_method='BEAUTY', ngon_method='BEAUTY')
        bm_.to_mesh(o.data)
        bm_.free()

# 1) detail meshes that belong to moving parts (feeder house, auger, reel, reel arms)
for ob in [o for o in D.objects if o.get("attach")]:
    tgt = D.objects.get(ob["attach"])
    if tgt is not None:
        join(tgt, [ob])
        tgt.pop("attach", None)

# 2) static combine parts, grouped by texture atlas
groups = {"body": [], "detail": [], "lights": []}
for o in list(CC.objects):
    if o.type == 'MESH' and o.parent is None and not o.get("keep"):
        groups[o.get("grp", "body")].append(o)
body = join_named("bizonZ050_body", groups["body"])
details = join_named("bizonZ050_details", groups["detail"])
lights = join_named("bizonZ050_lights", groups["lights"])
lift = D.objects.get("z050_liftCylinders")
if lift:
    lift.name = lift.data.name = "feederLiftCylinders"
tie = D.objects.get("z050_tieRod")
if tie:
    tie.name = tie.data.name = "rearAxleTieRod"

# header static parts
hroot = D.objects["header420"]
hstatic = [o for o in CH.objects if o.type == 'MESH' and o.parent == hroot and o.name != "knife"]
hbody = join_named("header420_body", hstatic)

# 3) hierarchy
root = empty("bizonZ050", (0, 0, 0), CC, TAG_ROOT, size=0.6, kind='ARROWS')
for n in ("bizonZ050_body", "bizonZ050_details", "bizonZ050_lights", "feederHouse", "feederLiftCylinders",
          "steeringWheel", "pipe", "frontAxle", "rearAxle"):
    ob = D.objects.get(n)
    if ob is not None and ob.parent is None:
        set_parent(ob, root)
for n in ("bizonZ050_body", "bizonZ050_details", "bizonZ050_lights", "feederLiftCylinders", "header420_body"):
    if n in D.objects:
        bake_local(D.objects[n])

# 4) collisions (hidden in the viewport; flag them in the GIANTS exporter)


def col_box(name, lo, hi, parent):
    bm = bmesh.new()
    box(bm, lo, hi)
    ob = make_obj(name, bm, [], CCOL, TAG_ROOT, smooth=None, wnormal=False)
    ob.display_type = 'WIRE'
    ob.hide_render = True
    ob["collision"] = True
    set_parent(ob, parent)
    bake_local(ob)
    return ob


col_box("bizonZ050_collisionBody", (-HB, -0.62, 0.66), (HB, REAR_Y, REAR_TOP), root)
col_box("bizonZ050_collisionTank", (-TANK_HW, TANK_Y0, 2.02), (TANK_HW, TANK_Y1, TANK_TOP), root)
col_box("bizonZ050_collisionCab", (-0.93, PLAT_Y0 - 0.12, 1.78), (0.93, PLAT_Y1, CANOPY_Z + 0.03), root)
col_box("header420_collision", (-2.20, -3.62, 0.05), (2.20, -1.62, 1.40), hroot)
CCOL.hide_render = True
lc = bpy.context.view_layer.layer_collection.children.get("Z050_collision")
if lc is not None:
    lc.hide_viewport = True

# 5) unobtrusive transform groups (small plain axes instead of big circles)
for o in D.objects:
    if o.type == 'EMPTY' and o.users_collection and o.users_collection[0] in (CC, CH):
        o.empty_display_type = 'PLAIN_AXES'
        o.empty_display_size = 0.12
for ob in D.objects:
    if ob.type == 'MESH' and ob.data.name != ob.name:
        ob.data.name = ob.name

# 6) atlas assignment (used by 07b_uv / 09_bake)


def atlas_of(o):
    if o.name.startswith("tire"):
        return "bizonZ050_tires"
    if o.name == "bizonZ050_lights":
        return None
    if o.users_collection and o.users_collection[0] == CH:
        return "header420"
    if o.name in ("bizonZ050_body", "feederHouse", "pipeTube"):
        return "bizonZ050"
    return "bizonZ050_details"


stats = {}
for o in D.objects:
    if o.type == 'MESH' and o.users_collection and o.users_collection[0] in (CC, CH):
        a = atlas_of(o)
        if a:
            o["fs_atlas"] = a
        o.data.calc_loop_triangles()
        k = a or "lights"
        stats[k] = stats.get(k, 0) + len(o.data.loop_triangles)
print("tris per atlas:", stats, "total:", sum(stats.values()))
print("combine objects:", sorted(o.name for o in CC.objects if o.type == 'MESH'))
print("header objects:", sorted(o.name for o in CH.objects if o.type == 'MESH'))
