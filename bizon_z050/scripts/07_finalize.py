# 07 - FS25 preparation: apply modifiers, join static parts, FS-style
# hierarchy with pivots for moving parts, collision boxes, UV atlases.
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


def join(target_name, names):
    objs = [D.objects[n] for n in names if n in D.objects]
    if not objs:
        return None
    active = objs[0]
    if len(objs) > 1:
        with bpy.context.temp_override(**view3d_ctx(), active_object=active, object=active,
                                       selected_objects=objs, selected_editable_objects=objs):
            bpy.ops.object.join()
    active.name = target_name
    active.data.name = target_name
    return active


if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

all_mesh = [o for o in D.objects if o.type == 'MESH' and o.get("z050_part")]
apply_mods(all_mesh)

# ------------------------------------------------------------ combine joins
body = join("bizonZ050_body", [
    "z050_bodyLower", "z050_bodyRibs", "z050_grainTank", "z050_tankTop", "z050_radiatorGrille",
    "z050_platform", "z050_frontAxle", "z050_rearAxleMount", "z050_hitch", "z050_railings",
    "z050_canopyFrame", "z050_canopyRoof", "z050_seat", "z050_steeringColumn", "z050_headlightBodies",
    "z050_lampsMisc", "z050_unloadRiser", "z050_pipeCradle", "z050_grainElevator", "z050_beltDrives",
    "z050_exhaust", "z050_airIntake", "z050_hoses", "z050_rearKit", "z050_smvSign", "z050_decals", "ladder"])
lights = join("bizonZ050_lights", ["z050_headlightGlass", "z050_lampsGlass", "z050_rearLights"])
lift = join("feederLiftCylinders", ["z050_liftCylinders"])
pipe_mesh = D.objects["pipeTube"]

# header joins
hbody = join("header420_body", ["z050h_trough", "z050h_endPlates", "z050h_cutterBar", "z050h_knifeDrive",
                                "z050h_reelLift", "z050h_drives"])

# ------------------------------------------------------------ hierarchy
root = empty("bizonZ050", (0, 0, 0), CC, TAG_ROOT, size=1.0, kind='ARROWS')
for n in ("bizonZ050_body", "bizonZ050_lights", "feederHouse", "feederLiftCylinders", "steeringWheel",
          "pipe", "frontAxle", "rearAxle"):
    ob = D.objects[n]
    if ob.parent is None:
        set_parent(ob, root)
tie = D.objects.get("z050_tieRod")
if tie:
    tie.name = tie.data.name = "rearAxleTieRod"



def bake_local(ob):
    """Move a static child's local offset into its mesh (identity local transform)."""
    if ob.parent is not None and ob.matrix_basis != Matrix.Identity(4):
        ob.data.transform(ob.matrix_basis)
        ob.matrix_basis = Matrix.Identity(4)


for n in ("bizonZ050_body", "bizonZ050_lights", "feederLiftCylinders", "header420_body"):
    if n in D.objects:
        bake_local(D.objects[n])

# ------------------------------------------------------------ collisions


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
col_box("bizonZ050_collisionCab", (-0.93, PLAT_Y0 - 0.12, 1.83), (0.93, PLAT_Y1, CANOPY_Z + 0.02), root)
col_box("header420_collision", (-2.20, -3.62, 0.05), (2.20, -1.70, 1.40), D.objects["header420"])

# ------------------------------------------------------------ naming
for ob in D.objects:
    if ob.type == 'MESH' and ob.data.name != ob.name:
        ob.data.name = ob.name

# ------------------------------------------------------------ UV atlases


def unwrap(objs, margin=0.0015):
    objs = [o for o in objs if o and o.type == 'MESH']
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
        bpy.ops.uv.pack_islands(rotate=True, rotate_method='ANY', scale=True, margin_method='FRACTION',
                                margin=margin, shape_method='CONCAVE')
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in objs:
        o.select_set(False)


meshes_c = [o for o in D.objects if o.type == 'MESH' and o.users_collection and o.users_collection[0] == CC]
tires = [o for o in meshes_c if o.name.startswith("tire")]
glassy = [o for o in meshes_c if o.name == "bizonZ050_lights"]
atlas_body = [o for o in meshes_c if o not in tires and o not in glassy]
atlas_header = [o for o in D.objects if o.type == 'MESH' and o.users_collection and o.users_collection[0] == CH]
unwrap(atlas_body)
unwrap(tires)
unwrap(atlas_header)
unwrap(glassy)
for o in atlas_body:
    o["fs_atlas"] = "bizonZ050"
for o in tires:
    o["fs_atlas"] = "bizonZ050_tires"
for o in atlas_header:
    o["fs_atlas"] = "header420"

# ------------------------------------------------------------ report
dg = bpy.context.evaluated_depsgraph_get()


def tris(objs):
    t = 0
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        t += len(me.loop_triangles)
    return t


print("combine meshes:", len(meshes_c), "tris:", tris(meshes_c))
print("header meshes:", len(atlas_header), "tris:", tris(atlas_header))
print("combine objects:", sorted(o.name for o in meshes_c))
print("header objects:", sorted(o.name for o in atlas_header))
