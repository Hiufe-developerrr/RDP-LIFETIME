# 04 - open operator station (Z050 Super style): railings, sun canopy on four
# posts (cream top, grey underside), seat, steering column + wheel, levers,
# pedals, instrument box, headlights, work lights, beacon, mirrors, ladder.
TAG = "operator"
purge_part(TAG)
C = coll("Z050_combine")
RED, CREAM, GRAY, DARK, STEEL = ("Z050_paint_red", "Z050_paint_cream", "Z050_paint_gray",
                                 "Z050_metal_dark", "Z050_steel")
RUB, CHROME, GLASS, ORANGE, LRED = ("Z050_rubber_black", "Z050_chrome", "Z050_glass",
                                    "Z050_lamp_orange", "Z050_lamp_red")
FZ = PLAT_Z
RAIL_R = 0.019

# ------------------------------------------------------------------ railings
bm = bmesh.new()
top = FZ + 0.92
mid = FZ + 0.50
# main loop: left side (ends at ladder gap) -> front -> right side down to floor
tube(bm, [(PLAT_HW - 0.03, -1.00, FZ), (PLAT_HW - 0.03, -1.00, top), (PLAT_HW - 0.03, PLAT_Y0 + 0.05, top),
          (-PLAT_HW + 0.03, PLAT_Y0 + 0.05, top), (-PLAT_HW + 0.03, PLAT_Y1 - 0.05, top),
          (-PLAT_HW + 0.03, PLAT_Y1 - 0.05, TANK_TOP - 0.55)], RAIL_R, 12, round_r=0.09)
tube(bm, [(PLAT_HW - 0.03, -1.00, mid), (PLAT_HW - 0.03, PLAT_Y0 + 0.05, mid),
          (-PLAT_HW + 0.03, PLAT_Y0 + 0.05, mid), (-PLAT_HW + 0.03, PLAT_Y1 - 0.05, mid)], RAIL_R, 12,
     round_r=0.09)
for (x, y) in ((PLAT_HW - 0.03, PLAT_Y0 + 0.05), (-PLAT_HW + 0.03, PLAT_Y0 + 0.05), (-PLAT_HW + 0.03, -1.0)):
    tube(bm, [(x, y, FZ), (x, y, top)], RAIL_R, 12)
    cyl(bm, (x, y, FZ), (x, y, FZ + 0.012), 0.045, 12)            # foot plates
make_obj("z050_railings", bm, [RED], C, TAG)

# ---------------------------------------------------------------- sun canopy
bm = bmesh.new()
post_r = 0.022
cz = CANOPY_Z - 0.06
posts = [(0.80, PLAT_Y0 + 0.08), (-0.80, PLAT_Y0 + 0.08), (0.74, TANK_Y0 - 0.05), (-0.74, TANK_Y0 - 0.05)]
for (x, y) in posts[:2]:
    tube(bm, [(x, y, FZ), (x, y, cz)], post_r, 12, mi=1)
for (x, y) in posts[2:]:
    tube(bm, [(x, y, TANK_TOP - 0.62), (x, y, cz)], post_r, 12, mi=1)
    box(bm, (x - 0.05, TANK_Y0 - 0.03, TANK_TOP - 0.70), (x + 0.05, TANK_Y0, TANK_TOP - 0.55), 1)
# canopy frame tubes
tube(bm, [(0.80, PLAT_Y0 + 0.08, cz), (0.80, TANK_Y0 - 0.05, cz), (-0.80, TANK_Y0 - 0.05, cz),
          (-0.80, PLAT_Y0 + 0.08, cz)], 0.018, 10, mi=1, closed=True)
make_obj("z050_canopyFrame", bm, [RED, GRAY], C, TAG)

bm = bmesh.new()
y0, y1, hw = PLAT_Y0 - 0.12, TANK_Y0 + 0.14, 0.88
zt = CANOPY_Z
# roof shell: slightly crowned top plate with a turned-down skirt
outline = rrect2d(2 * hw, y1 - y0, 0.07, 3, 0.0, (y0 + y1) / 2)
rings = [[(x, y, zt - 0.075) for (x, y) in outline],
         [(x, y, zt - 0.012) for (x, y) in outline],
         [(x * 0.985, (y - (y0 + y1) / 2) * 0.985 + (y0 + y1) / 2, zt) for (x, y) in outline],
         [(x * 0.6, (y - (y0 + y1) / 2) * 0.8 + (y0 + y1) / 2, zt + 0.018) for (x, y) in outline]]
loft(bm, rings, cap=False, mi=0)
last = [v for v in bm.verts if abs(v.co.z - (zt + 0.018)) < 1e-6]
f = bm.faces.new(sorted(last, key=lambda v: atan2(v.co.y - (y0 + y1) / 2, v.co.x)))
f.material_index = 0
# grey underside ("podsufitka") inside the skirt + stiffening ribs
inner = rrect2d(2 * hw - 0.03, y1 - y0 - 0.03, 0.06, 3, 0.0, (y0 + y1) / 2)
plate(bm, [(x, y, zt - 0.03) for (x, y) in inner], 0.012, (0, 0, 1), mi=1)
for k in range(4):
    yy = y0 + 0.30 + k * (y1 - y0 - 0.6) / 3
    box(bm, (-hw + 0.04, yy - 0.02, zt - 0.055), (hw - 0.04, yy + 0.02, zt - 0.03), 1)
make_obj("z050_canopyRoof", bm, [CREAM, GRAY], C, TAG, bevel=0.004)

# ---------------------------------------------------------- seat and console
bm = bmesh.new()
sy, sz = -0.60, FZ + 0.46
box(bm, (-0.10, sy - 0.12, FZ), (0.10, sy + 0.12, sz - 0.10), 1)                    # pedestal
cyl(bm, (0, sy, sz - 0.10), (0, sy, sz - 0.06), 0.14, 16, 1)
cush = rrect2d(0.48, 0.44, 0.08, 3)
loft(bm, [[(x, sy + y, sz - 0.06) for (x, y) in cush], [(x * 1.02, sy + y * 1.02, sz) for (x, y) in cush],
          [(x * 0.93, sy + y * 0.93, sz + 0.035) for (x, y) in cush]], mi=0)
back = rrect2d(0.46, 0.46, 0.08, 3)
bv = []
R0 = Matrix.Rotation(radians(-12), 4, 'X')
for (dz, sc, th) in ((0.0, 1.0, 0.0), (0.0, 1.0, 0.06), (0.0, 0.94, 0.085)):
    ring = []
    for (x, z) in back:
        p = R0 @ Vector((x * sc, th, z * sc + 0.26))
        ring.append((p.x, sy + 0.20 + p.y, sz + p.z))
    bv.append(ring)
loft(bm, bv, mi=0)
# right-hand lever console (grey) with levers and knobs
box(bm, (-0.56, -1.10, FZ), (-0.30, -0.72, FZ + 0.38), 2)
box(bm, (-0.57, -1.11, FZ + 0.38), (-0.29, -0.71, FZ + 0.40), 2)
for i, (x, y, ang) in enumerate(((-0.34, -1.02, 8), (-0.40, -1.02, -6), (-0.46, -1.02, 10), (-0.52, -1.02, 0),
                                 (-0.40, -0.80, 12), (-0.50, -0.80, -8))):
    p0 = Vector((x, y, FZ + 0.40))
    p1 = p0 + Matrix.Rotation(radians(ang), 3, 'X') @ Vector((0, 0, 0.36 if i < 4 else 0.28))
    cyl(bm, p0, p1, 0.009, 8, 3)
    sphere(bm, p1, 0.024, 12, 6, 0)
    box(bm, (x - 0.02, y - 0.03, FZ + 0.40), (x + 0.02, y + 0.03, FZ + 0.41), 3)
make_obj("z050_seat", bm, [RUB, DARK, GRAY, STEEL], C, TAG, bevel=0.006)

# ------------------------------------------------------ steering column + dash
col_base = Vector((0.0, -1.42, FZ))
col_top = Vector((0.0, -1.22, FZ + 0.80))
col_dir = (col_top - col_base).normalized()
bm = bmesh.new()
box(bm, (-0.13, -1.56, FZ), (0.13, -1.30, FZ + 0.22), 1)                  # steering box cover
cyl(bm, col_base + col_dir * 0.2, col_top - col_dir * 0.03, 0.038, 16, 1)
# instrument box on the column, gauges facing the operator
ib_c = col_base + col_dir * 0.55
vs, _ = box_c(bm, ib_c, (0.34, 0.12, 0.20), 2)
rotate_verts(bm, vs, -atan2(col_dir.y, col_dir.z), 'X', ib_c)
nrm = Matrix.Rotation(-atan2(col_dir.y, col_dir.z), 3, 'X') @ Vector((0, 1, 0))
for dx, rr in ((-0.10, 0.042), (0.0, 0.05), (0.10, 0.042)):
    c = ib_c + Vector((dx, 0, 0.02)) + nrm * 0.06
    cyl(bm, c, c + nrm * 0.012, rr, 18, 3)
    cyl(bm, c + nrm * 0.012, c + nrm * 0.016, rr * 0.8, 18, 4)
# pedals
for x in (-0.18, 0.18):
    tube(bm, [(x, -1.38, FZ + 0.12), (x, -1.52, FZ + 0.22), (x, -1.58, FZ + 0.16)], 0.012, 8, mi=1)
    vs, _ = box_c(bm, (x, -1.60, FZ + 0.15), (0.09, 0.03, 0.12), 3)
    rotate_verts(bm, vs, radians(-35), 'X', (x, -1.60, FZ + 0.15))
make_obj("z050_steeringColumn", bm, [RED, DARK, GRAY, STEEL, GLASS], C, TAG, bevel=0.004)

# steering wheel in its own frame (local Z = column axis) for FS animation
bm = bmesh.new()
R = 0.225
sweep(bm, [(R * cos(a), R * sin(a), 0.0) for a in [2 * pi * k / 48 for k in range(48)]],
      circle2d(0.016, 10), closed=True, mi=0)
cyl(bm, (0, 0, -0.05), (0, 0, 0.03), 0.04, 16, 1)
for k in range(3):
    a = pi / 2 + 2 * pi * k / 3
    tube(bm, [(0.03 * cos(a), 0.03 * sin(a), 0.0), (0.12 * cos(a), 0.12 * sin(a), -0.01),
              ((R - 0.01) * cos(a), (R - 0.01) * sin(a), 0.0)], 0.011, 8, mi=1)
sw = make_obj("steeringWheel", bm, [RUB, DARK], C, TAG)
sw.location = col_top
sw.rotation_euler = (-atan2(col_dir.y, col_dir.z), 0.0, 0.0)

# ------------------------------------------------------ headlights & signals
bm = bmesh.new()
for s in (1, -1):
    c = Vector((s * 0.70, PLAT_Y0 - 0.10, 1.99))
    revolve(bm, [(0.0, -0.09), (0.07, -0.09), (0.095, -0.06), (0.10, -0.01), (0.10, 0.0)], 24,
            center=c, axis='Y', mi=0)
    revolve(bm, [(0.098, -0.012), (0.106, -0.016), (0.106, -0.028), (0.090, -0.03)], 24,
            center=c, axis='Y', mi=1)
    box(bm, (s * 0.70 - 0.02, PLAT_Y0 - 0.10, 1.84), (s * 0.70 + 0.02, PLAT_Y0 - 0.02, 1.91), 0)
    # side marker / turn lamp at the beam end
    box(bm, (s * 0.905 - 0.035, PLAT_Y0 - 0.16, 2.08), (s * 0.905 + 0.035, PLAT_Y0 - 0.10, 2.15), 0)
make_obj("z050_headlightBodies", bm, [DARK, CHROME], C, TAG)
bm = bmesh.new()
for s in (1, -1):
    c = Vector((s * 0.70, PLAT_Y0 - 0.10, 1.99))
    revolve(bm, [(0.0, -0.045), (0.05, -0.040), (0.09, -0.030), (0.092, -0.022), (0.0, -0.022)], 24,
            center=c, axis='Y', mi=0, closed=True)
    box(bm, (s * 0.905 - 0.03, PLAT_Y0 - 0.17, 2.085), (s * 0.905 + 0.03, PLAT_Y0 - 0.16, 2.145), 1)
make_obj("z050_headlightGlass", bm, [GLASS, ORANGE], C, TAG)

# work lights on the canopy front, beacon, mirrors
bm = bmesh.new()
for s in (1, -1):
    x = s * 0.55
    box(bm, (x - 0.01, PLAT_Y0 - 0.14, CANOPY_Z - 0.10), (x + 0.01, PLAT_Y0 - 0.06, CANOPY_Z - 0.07), 0)
    c = Vector((x, PLAT_Y0 - 0.18, CANOPY_Z - 0.14))
    vs, _ = box_c(bm, c, (0.14, 0.10, 0.10), 0)
    rotate_verts(bm, vs, radians(-12), 'X', c)
    # mirror arm from the front post + mirror head
    p0 = Vector((s * 0.80, PLAT_Y0 + 0.08, FZ + 1.18))
    p1 = Vector((s * 1.12, PLAT_Y0 + 0.02, FZ + 1.24))
    tube(bm, [p0, p1, p1 + Vector((0, 0, 0.06))], 0.011, 8, mi=0, round_r=0.03)
    mc = p1 + Vector((s * 0.03, 0, 0.14))
    vs, _ = box_c(bm, mc, (0.03, 0.17, 0.25), 0)
    rotate_verts(bm, vs, radians(-s * 12), 'Z', mc)
    vs, _ = box_c(bm, mc + Vector((0, 0.017, 0)), (0.024, 0.006, 0.23), 1)
    rotate_verts(bm, vs, radians(-s * 12), 'Z', mc)
# beacon base
bc = Vector((0.52, TANK_Y0 + 0.02, CANOPY_Z + 0.018))
cyl(bm, bc, bc + Vector((0, 0, 0.05)), 0.075, 20, 0)
make_obj("z050_lampsMisc", bm, [DARK, CHROME], C, TAG, bevel=0.003)
bm = bmesh.new()
for s in (1, -1):
    x = s * 0.55
    c = Vector((x, PLAT_Y0 - 0.235, CANOPY_Z - 0.147))
    vs, _ = box_c(bm, c, (0.12, 0.01, 0.08), 0)
    rotate_verts(bm, vs, radians(-12), 'X', c)
revolve(bm, [(0.065, 0.05), (0.066, 0.12), (0.05, 0.16), (0.0, 0.175)], 20, center=bc, axis='Z', mi=1)
make_obj("z050_lampsGlass", bm, [GLASS, ORANGE], C, TAG)

# ---------------------------------------------------------------- ladder (L)
bm = bmesh.new()
b_y, b_z, t_y, t_z = -0.99, 0.42, -0.74, FZ - 0.02
for x in (0.975, 1.355):
    prism(bm, [(b_y - 0.025, b_z), (b_y + 0.025, b_z), (t_y + 0.025, t_z), (t_y - 0.025, t_z)], 'X',
          x - 0.006, x + 0.006, 0)
for i in range(6):
    t = (i + 0.4) / 6.0
    yy, zz = b_y + (t_y - b_y) * t, b_z + (t_z - b_z) * t
    box(bm, (0.981, yy - 0.07, zz - 0.012), (1.349, yy + 0.07, zz + 0.012), 0)
    for k in range(5):
        box(bm, (1.02 + k * 0.07, yy - 0.05, zz + 0.012), (1.05 + k * 0.07, yy + 0.05, zz + 0.016), 1)
# landing step bridging to the platform
box(bm, (PLAT_HW, t_y - 0.14, FZ - 0.04), (1.36, t_y + 0.30, FZ), 0)
for (y, z) in ((t_y - 0.10, FZ - 0.04), (t_y + 0.26, FZ - 0.04)):
    tube(bm, [(0.98, y, z), (0.95, y, z - 0.35)], 0.016, 8)
# handrails
for x in (0.975, 1.355):
    tube(bm, [(x, t_y - 0.05, FZ + 0.02), (x, t_y + 0.02, FZ + 0.90), (x, t_y + 0.30, FZ + 0.92),
              (x, t_y + 0.33, FZ + 0.02)], RAIL_R, 10, round_r=0.07)
make_obj("ladder", bm, [RED, STEEL], C, TAG, bevel=0.003)

print("operator objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
