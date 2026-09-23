# 05d - hydraulics: oil tank with filler / breather / sight glass, valve block
# with linkage rods to the console, hoses with crimped fittings to the lift
# cylinders, reel hoses with quick couplers on the feeder house, steel
# steering lines with clamps along the right frame rail.
TAG = "hydraulics"
purge_part(TAG)
C = coll("Z050_combine")
MATS = ["Z050_hose", "Z050_zinc", "Z050_paint_red", "Z050_metal_dark", "Z050_steel", "Z050_glass", "Z050_brass"]
HOSE, ZN, RED, DARK, STEEL, GLASS, BRASS = range(7)
bm = bmesh.new()

# ------------------------------------------------------------- oil tank (L)
tc_y, tc_z, tr = -0.74, 1.16, 0.10
revolve(bm, [(0.0, 0.62), (tr * 0.8, 0.625), (tr, 0.64), (tr, 0.92), (tr * 0.8, 0.935), (0.0, 0.94)], 28,
        center=(0, tc_y, tc_z), axis='X', mi=RED)
for x in (0.68, 0.88):
    revolve(bm, [(tr, x - 0.012), (tr + 0.006, x - 0.012), (tr + 0.006, x + 0.012), (tr, x + 0.012)], 28,
            center=(0, tc_y, tc_z), axis='X', mi=DARK, closed=True)
    box(bm, (x - 0.012, tc_y + tr * 0.6, tc_z - 0.02), (x + 0.012, -0.62, tc_z + 0.02), DARK)
cyl(bm, (0.84, tc_y, tc_z + tr - 0.01), (0.84, tc_y, tc_z + tr + 0.05), 0.03, 14, DARK)            # filler
cyl(bm, (0.84, tc_y, tc_z + tr + 0.05), (0.84, tc_y, tc_z + tr + 0.07), 0.042, 14, DARK)
cyl(bm, (0.72, tc_y, tc_z + tr - 0.01), (0.72, tc_y, tc_z + tr + 0.035), 0.009, 8, BRASS)          # breather
sphere(bm, (0.72, tc_y, tc_z + tr + 0.045), 0.016, 10, 5, BRASS)
cyl(bm, (0.94, tc_y, tc_z), (0.946, tc_y, tc_z), 0.032, 16, ZN)                                   # sight glass
cyl(bm, (0.946, tc_y, tc_z), (0.948, tc_y, tc_z), 0.024, 16, GLASS)
hose(bm, [(0.75, tc_y, tc_z - tr - 0.02), (0.72, tc_y + 0.02, 0.98), (0.45, -0.70, 0.95), (0.30, -0.66, 0.97)],
     0.016, HOSE, ZN, 0.08)

# ---------------------------------------------------------- valve block (R)
vx0, vx1, vy0, vy1, vz0, vz1 = -0.92, -0.66, -0.78, -0.64, 1.06, 1.30
box(bm, (vx0, vy0, vz0), (vx1, vy1, vz1), DARK)
for k, x in enumerate((-0.87, -0.79, -0.71)):
    cyl(bm, (x, vy0, 1.18), (x, vy0 - 0.07, 1.18), 0.017, 12, STEEL)                               # spools
    box_c(bm, (x, vy0 - 0.085, 1.18), (0.03, 0.03, 0.03), DARK)                                    # clevis
    tube(bm, [(x, vy0 - 0.085, 1.20), (x + 0.02, -0.90, 1.60), (-0.60 - 0.04 * k, -0.96, PLAT_Z - 0.05)], 0.0075,
         8, mi=STEEL, round_r=0.1)                                                                 # rods to levers
    for z in (vz0 + 0.04, vz1 - 0.04):
        nut(bm, (x + 0.035, vy0, z), (0, -1, 0), af=0.019, h=0.01, mi=ZN)                         # port fittings
for (x, z) in ((vx0 + 0.02, vz0 + 0.02), (vx1 - 0.02, vz0 + 0.02), (vx0 + 0.02, vz1 - 0.02), (vx1 - 0.02, vz1 - 0.02)):
    nut(bm, (x, vy0, z), (0, -1, 0), af=0.015, h=0.007, mi=ZN, stud=True)
for x in (vx0 + 0.03, vx1 - 0.03):
    box(bm, (x - 0.015, vy1, vz1 - 0.05), (x + 0.015, -0.62, vz1 + 0.04), DARK)
# pressure / return lines from inside the body
hose(bm, [(-0.60, -0.63, 1.10), (-0.62, -0.72, 1.06), (-0.84, vy0 - 0.02, vz0 + 0.04)], 0.012, HOSE, ZN, 0.05)
hose(bm, [(-0.60, -0.63, 1.22), (-0.64, -0.76, 1.30), (-0.76, vy0 - 0.02, vz1 - 0.04)], 0.012, HOSE, ZN, 0.05)
# lift cylinder hoses (right + crossing to the left cylinder under the body)
hose(bm, [(-0.835, vy0 - 0.02, vz0 + 0.04), (-0.80, -0.70, 0.98), (-0.46, -0.45, 0.90), (-0.42, -0.33, 0.80)],
     0.011, HOSE, ZN, 0.08)
hose(bm, [(-0.755, vy0 - 0.02, vz0 + 0.04), (-0.70, -0.72, 0.96), (-0.20, -0.47, 0.93), (0.36, -0.46, 0.90),
          (0.42, -0.33, 0.80)], 0.011, HOSE, ZN, 0.1)
for x in (-0.42, 0.42):
    nut(bm, (x, -0.33, 0.80), (0, 1, 0), af=0.022, h=0.012, mi=ZN)

# ------------------------------- steering: orbitrol + steel lines to the rear
oc = Vector((0.0, -1.62, PLAT_Z - 0.10))
cyl(bm, oc, oc + Vector((0, 0, 0.05)), 0.055, 16, DARK)
for k in range(4):
    a = pi / 4 + pi / 2 * k
    nut(bm, oc + Vector((0.042 * cos(a), 0.042 * sin(a), 0.0)), (0, 0, -1), af=0.013, h=0.006, mi=ZN)
rail = [(-0.50, 1.00), (0.28, 0.98), (0.45, 0.66), (2.55, 0.66), (3.05, 1.02), (3.35, 1.06)]
for k, dx in enumerate((-0.012, 0.012)):
    hose(bm, [oc + Vector((dx, 0.0, -0.005)), oc + Vector((dx, 0.0, -0.08)), (-0.40 + dx, -1.40, 1.85),
              (-0.665 + dx, -1.00, 1.55), (-0.68 + dx, -0.70, 1.40), (-0.935, -0.52, 1.00 - 0.10 - k * 0.018)],
         0.0095, HOSE, ZN, 0.1)
    line = [(-0.935, y, z - 0.10 - k * 0.018) for (y, z) in rail]
    tube(bm, line, 0.0055, 8, mi=STEEL, round_r=0.12)
    hose(bm, [line[-1], (-0.80, 3.45, 0.96), (-0.45 + dx * 3, 3.55, 0.68), (-0.30 + dx * 3, 3.60, 0.59)], 0.0095,
         HOSE, ZN, 0.12)
for pt in resample([(-0.935, y, z - 0.10) for (y, z) in rail], 0.5)[1:-1]:
    box_c(bm, pt + Vector((0, 0, -0.009)), (0.02, 0.025, 0.05), ZN)
    nut(bm, pt + Vector((0.01, 0, -0.009)), (1, 0, 0), af=0.011, h=0.004, mi=ZN, washer=False)

ob = make_obj("z050_hydraulics", bm, MATS, C, TAG)
ob["grp"] = "detail"

# ------------------------------------ reel hoses + quick couplers (feeder house)
fb = bmesh.new()
qc = Vector((-0.66, -1.60, 1.20))
box(fb, (qc.x - 0.012, qc.y - 0.07, qc.z - 0.03), (qc.x + 0.012, qc.y + 0.07, qc.z + 0.03), DARK)
for dy in (-0.035, 0.035):
    p = qc + Vector((-0.012, dy, 0))
    cyl(fb, p, p + Vector((-0.05, 0, 0)), 0.014, 6, ZN)
    cyl(fb, p + Vector((-0.05, 0, 0)), p + Vector((-0.085, 0, 0)), 0.018, 12, ZN)
    cyl(fb, p + Vector((-0.085, 0, 0)), p + Vector((-0.10, 0, 0)), 0.02, 12, RED)                   # dust cap
for k, dz in enumerate((-0.012, 0.012)):
    hose(fb, [(-0.71 + dz, vy0 - 0.02, vz1 - 0.04), (-0.70, -0.86, 1.55 + dz), (-0.66, -1.05, 1.62 + dz),
              (-0.64, -1.30, 1.40 + dz), (qc.x + 0.012, qc.y + 0.035 - k * 0.07, qc.z)], 0.0105, HOSE, ZN, 0.12)
for t in (0.35, 0.7):                                                     # hose clips on the feeder side
    p = Vector((-0.63, -1.05, 1.60)).lerp(Vector((-0.63, -1.45, 1.28)), t)
    box_c(fb, p, (0.02, 0.03, 0.06), ZN)
fob = make_obj("z050_feederHoses", fb, MATS, C, TAG)
fob["grp"] = "detail"
fob["attach"] = "feederHouse"
print("hydraulics:", len(ob.data.polygons), "+", len(fob.data.polygons), "faces")
