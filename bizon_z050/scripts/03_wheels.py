# 03 - wheels: front drive 18.4-30 (R-1 chevron lugs, cream W16 rim with
# vent holes), rear steer 10.00-15 (rib tread), knuckles and hubs.
TAG = "wheels"
purge_part(TAG)
C = coll("Z050_combine")
TIRE, CREAM, DARK, STEEL = "Z050_rubber_tire", "Z050_paint_cream", "Z050_metal_dark", "Z050_steel"


def interp(tab, x):
    x = abs(x)
    for (x0, r0), (x1, r1) in zip(tab, tab[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return r0 + (r1 - r0) * t
    return tab[-1][1]


def front_tire(bm, s):
    """18.4-30 bias tyre around the local X axis; s=+1 outer side is +X."""
    R, h, W2 = FW_R, 0.042, 0.236
    half = [(0.381, 0.200), (0.405, 0.214), (0.455, 0.227), (0.525, W2), (0.585, 0.233),
            (0.640, 0.223), (0.688, 0.204), (0.716, 0.182), (0.729, 0.155), (0.733, 0.10), (0.734, 0.0)]
    prof = half + [(r, -x) for (r, x) in reversed(half[:-1])]
    prof += [(0.372, -0.200), (0.372, 0.200)]
    revolve(bm, prof, 80, axis='X', closed=True)
    # sidewall rim-protector rib
    for sx in (1, -1):
        revolve(bm, [(0.44, sx * 0.222), (0.455, sx * 0.232), (0.47, sx * 0.230), (0.475, sx * 0.224)],
                80, axis='X')
    carcass = [(0.0, 0.734), (0.10, 0.733), (0.155, 0.729), (0.182, 0.716), (0.204, 0.688),
               (0.223, 0.640), (0.233, 0.585)]
    n_lugs = 23
    xa, xb = 0.012, 0.226
    for side in (1, -1):
        for k in range(n_lugs):
            th0 = 2 * pi * k / n_lugs + (pi / n_lugs if side < 0 else 0.0)
            rings = []
            st = 8
            for i in range(st + 1):
                t = i / st
                x = xa + (xb - xa) * t
                rc = interp(carcass, x)
                th = th0 - (x - xa) / 0.734 * (1.0 + 0.35 * t)
                rb, rt = rc - 0.012, min(R, rc + h)
                wb, wt = 0.080, 0.062
                ring = []
                for (w, r) in ((-wb, rb), (wb, rb), (wt, rt), (-wt, rt)):
                    a = th + (w / 2) / r
                    ring.append((side * x, r * cos(a), r * sin(a)))
                rings.append(ring)
            loft(bm, rings, cap=True)
    if s < 0:
        for v in bm.verts:
            v.co.x = -v.co.x


def front_rim(s):
    """(barrel, disc, hub) bmeshes for the W16L-30 rim, outer side +X*s."""
    bm = bmesh.new()
    outer = [(0.418, 0.214), (0.404, 0.206), (0.384, 0.192), (0.384, 0.125), (0.346, 0.095),
             (0.346, -0.060), (0.384, -0.090), (0.384, -0.192), (0.404, -0.206), (0.418, -0.214)]
    inner = [(r - 0.009, x) for (r, x) in reversed(outer)]
    inner[0] = (0.409, -0.212)
    inner[-1] = (0.409, 0.212)
    revolve(bm, outer + inner, 72, axis='X', closed=True, mi=0)
    cyl(bm, (0.08, 0.35, 0.0), (0.12, 0.395, 0.0), 0.007, 8, 2)          # valve stem
    disc = bmesh.new()
    dprof = [(0.3375, 0.030), (0.300, 0.040), (0.262, 0.074), (0.150, 0.080), (0.105, 0.080),
             (0.105, 0.068), (0.150, 0.068), (0.255, 0.062), (0.292, 0.028), (0.3375, 0.018)]
    revolve(disc, dprof, 64, axis='X', closed=True, mi=0)
    hub = bmesh.new()
    revolve(hub, [(0.0, 0.080), (0.100, 0.080), (0.100, 0.105), (0.085, 0.118), (0.060, 0.128),
                  (0.0, 0.132)], 32, axis='X', mi=1)
    bolt_ring(hub, (0.081, 0, 0), (1, 0, 0), 0.128, 10, 0.013, 0.018, mi=1)
    if s < 0:
        for b in (bm, disc, hub):
            for v in b.verts:
                v.co.x = -v.co.x
    return bm, disc, hub


def cut_holes(ob, s, n, r_pos, r_hole, x_mid, depth):
    """Boolean vent holes through the wheel disc (applied via depsgraph)."""
    cb = bmesh.new()
    for i in range(n):
        a = 2 * pi * (i + 0.5) / n
        y, z = r_pos * cos(a), r_pos * sin(a)
        cyl(cb, (s * (x_mid - depth), y, z), (s * (x_mid + depth), y, z), r_hole, 24)
    cme = D.meshes.new("_cutter")
    cb.to_mesh(cme)
    cb.free()
    cutter = D.objects.new("_cutter", cme)
    C.objects.link(cutter)
    cutter.matrix_world = world_matrix(ob)
    md = ob.modifiers.new("holes", 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.solver = 'EXACT'
    md.object = cutter
    dg = bpy.context.evaluated_depsgraph_get()
    new = D.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.remove(md)
    ob.data = new
    new.name = old.name
    D.meshes.remove(old)
    D.objects.remove(cutter, do_unlink=True)
    D.meshes.remove(cme)
    new.shade_smooth()
    new.set_sharp_from_angle(angle=radians(35))


def rear_tire(bm):
    R, W2 = RW_R, 0.128
    half = [(0.191, 0.108), (0.215, 0.120), (0.26, W2), (0.31, 0.126), (0.350, 0.114), (0.378, 0.094),
            (0.392, 0.074), (0.396, 0.066), (0.384, 0.060), (0.384, 0.048), (0.399, 0.042),
            (0.400, 0.016), (0.386, 0.011)]
    prof = half + [(0.386, 0.0)] + [(r, -x) for (r, x) in reversed(half)]
    prof += [(0.184, -0.108), (0.184, 0.108)]
    revolve(bm, prof, 64, axis='X', closed=True)


def rear_rim(s):
    bm = bmesh.new()
    outer = [(0.214, 0.112), (0.203, 0.106), (0.192, 0.098), (0.192, 0.060), (0.168, 0.042),
             (0.168, -0.042), (0.192, -0.060), (0.192, -0.098), (0.203, -0.106), (0.214, -0.112)]
    inner = [(r - 0.006, x) for (r, x) in reversed(outer)]
    revolve(bm, outer + inner, 48, axis='X', closed=True, mi=0)
    disc = bmesh.new()
    revolve(disc, [(0.1615, 0.006), (0.125, 0.012), (0.105, 0.040), (0.055, 0.042), (0.055, 0.032),
                   (0.100, 0.030), (0.118, 0.002), (0.1615, -0.006)], 40, axis='X', closed=True, mi=0)
    hub = bmesh.new()
    revolve(hub, [(0.0, 0.042), (0.052, 0.042), (0.052, 0.062), (0.040, 0.075), (0.0, 0.080)], 20,
            axis='X', mi=1)
    bolt_ring(hub, (0.043, 0, 0), (1, 0, 0), 0.075, 6, 0.010, 0.014, mi=1)
    if s < 0:
        for b in (bm, disc, hub):
            for v in b.verts:
                v.co.x = -v.co.x
    return bm, disc, hub


def finish_rim(name, parts, hub_pos, parent, s, n, r_pos, r_hole, x_mid):
    """Cut vent holes into the disc alone, then merge barrel + disc + hub."""
    barrel, disc, hubm = parts
    for b in parts:
        bmesh.ops.translate(b, verts=b.verts, vec=Vector(hub_pos))
    mats = [CREAM, STEEL, DARK]
    tmp = make_obj("_disc_tmp", disc, mats, C, TAG, origin=hub_pos)
    cut_holes(tmp, s, n, r_pos, r_hole, x_mid, 0.05)
    bm = bmesh.new()
    bm.from_mesh(tmp.data)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(hub_pos))
    for b in (barrel, hubm):
        me = D.meshes.new("_m")
        b.to_mesh(me)
        b.free()
        bm.from_mesh(me)
        D.meshes.remove(me)
    old = tmp.data
    D.objects.remove(tmp, do_unlink=True)
    D.meshes.remove(old)
    return make_obj(name, bm, mats, C, TAG, origin=hub_pos, parent=parent)


front_axle_empty = empty("frontAxle", (0, 0, FW_R), C, TAG, size=0.5)
for s, nm in ((1, "Left"), (-1, "Right")):
    hub = (s * FW_X, 0.0, FW_R)
    w = empty("wheelFront" + nm, hub, C, TAG, parent=front_axle_empty, size=0.9, kind='CIRCLE')
    bm = bmesh.new()
    front_tire(bm, s)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(hub))
    make_obj("tireFront" + nm, bm, [TIRE], C, TAG, origin=hub, parent=w, bevel=0.006,
             bevel_segs=1, bevel_angle=40)
    finish_rim("rimFront" + nm, front_rim(s), hub, w, s, 8, 0.205, 0.038, 0.071)
    # stub hub between final drive and disc
    bm = bmesh.new()
    revolve(bm, [(0.0, s * 1.075), (0.13, s * 1.075), (0.13, s * 1.10), (0.10, s * 1.12),
                 (0.10, s * (FW_X + 0.072)), (0.0, s * (FW_X + 0.072))],
            28, center=(0, 0, FW_R), axis='X')
    make_obj("hubFront" + nm, bm, [DARK], C, TAG, origin=hub, parent=w)

rear_axle = D.objects["rearAxle"]
for s, nm in ((1, "Left"), (-1, "Right")):
    king = (s * 0.78, RW_Y, 0.47)
    kn = empty("steeringKnuckleRear" + nm, king, C, TAG, parent=rear_axle, size=0.25)
    bm = bmesh.new()
    cyl(bm, (s * 0.78, RW_Y, 0.31), (s * 0.78, RW_Y, 0.34), 0.05, 14)
    cyl(bm, (s * 0.78, RW_Y, 0.60), (s * 0.78, RW_Y, 0.63), 0.05, 14)
    box(bm, (min(s * 0.80, s * 0.845), RW_Y - 0.05, 0.31), (max(s * 0.80, s * 0.845), RW_Y + 0.05, 0.63))
    box(bm, (min(s * 0.78, s * 0.80), RW_Y - 0.05, 0.31), (max(s * 0.78, s * 0.80), RW_Y + 0.05, 0.34))
    box(bm, (min(s * 0.78, s * 0.80), RW_Y - 0.05, 0.60), (max(s * 0.78, s * 0.80), RW_Y + 0.05, 0.63))
    cyl(bm, (s * 0.84, RW_Y, RW_R), (s * (RW_X + 0.02), RW_Y, RW_R), 0.035, 12)       # stub axle
    # steering arm pointing back to the tie rod
    box(bm, (s * 0.74 - 0.025, RW_Y, 0.635), (s * 0.74 + 0.025, RW_Y + 0.26, 0.665))
    box(bm, (min(s * 0.74, s * 0.80), RW_Y - 0.03, 0.63), (max(s * 0.74, s * 0.80), RW_Y + 0.03, 0.665))
    cyl(bm, (s * 0.74, RW_Y + 0.24, 0.60), (s * 0.74, RW_Y + 0.24, 0.67), 0.022, 10)
    make_obj("knuckleRear" + nm, bm, [DARK], C, TAG, origin=king, parent=kn, bevel=0.005)
    hub = (s * RW_X, RW_Y, RW_R)
    w = empty("wheelRear" + nm, hub, C, TAG, parent=kn, size=0.45, kind='CIRCLE')
    bm = bmesh.new()
    rear_tire(bm)
    if s < 0:
        for v in bm.verts:
            v.co.x = -v.co.x
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(hub))
    make_obj("tireRear" + nm, bm, [TIRE], C, TAG, origin=hub, parent=w, bevel=0.004, bevel_segs=1,
             bevel_angle=40)
    finish_rim("rimRear" + nm, rear_rim(s), hub, w, s, 5, 0.140, 0.018, 0.008)

# tie rod between the steering arms (child of the rear axle)
bm = bmesh.new()
cyl(bm, (-0.74, RW_Y + 0.24, 0.62), (0.74, RW_Y + 0.24, 0.62), 0.018, 10)
cyl(bm, (-0.25, RW_Y + 0.07, 0.56), (-0.52, RW_Y + 0.19, 0.61), 0.035, 12, 0)     # steering cylinder
cyl(bm, (-0.52, RW_Y + 0.19, 0.61), (-0.72, RW_Y + 0.235, 0.63), 0.015, 8, 1)
make_obj("z050_tieRod", bm, [DARK, "Z050_chrome"], C, TAG, parent=rear_axle)

print("wheel objects:", len([o for o in D.objects if o.get("z050_part") == TAG]))
