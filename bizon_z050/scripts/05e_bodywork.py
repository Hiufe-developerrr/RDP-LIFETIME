# 05e - sheet metal realism: rivet rows along ribs, seams and tank corners,
# pressed stiffening beads, piano hinges and T-handle latches on the doors,
# bolted edge flanges on the front / rear faces.
TAG = "bodywork"
purge_part(TAG)
C = coll("Z050_combine")
bm = bmesh.new()
RED, ZINC, DARK = 0, 1, 2
RIB = HB + 0.028            # outer face of the side ribs / belt line

for s in (1, -1):
    n = (s, 0, 0)
    # belt line and upper rear rib
    fasteners(bm, (s * RIB, -0.52, 1.63), (s * RIB, 4.50, 1.63), n, 0.125, 'rivet', RED)
    fasteners(bm, (s * RIB, 2.18, 2.685), (s * RIB, 4.46, 2.685), n, 0.125, 'rivet', RED)
    # vertical U ribs
    for y in (0.46, 2.10, 3.30):
        zb = 0.74 if y < 2.6 else 1.12
        zt = 1.98 if y < 2.1 else REAR_TOP - 0.1
        fasteners(bm, (s * RIB, y, zb), (s * RIB, y, zt), n, 0.12, 'rivet', RED, skip_ends=True)
    # lower skin seam just above the bottom edge
    for (ya, za, yb, zb) in ((-0.55, 1.03, 0.25, 1.01), (0.50, 0.70, 2.50, 0.70), (3.08, 1.06, 4.55, 1.18)):
        fasteners(bm, (s * HB, ya, za), (s * HB, yb, zb), n, 0.14, 'rivet', RED)
    # grain tank: drip lip, vertical corners, top edge
    fasteners(bm, (s * (TANK_HW + 0.02), TANK_Y0 + 0.02, 2.05), (s * (TANK_HW + 0.02), TANK_Y1 - 0.02, 2.05), n, 0.15,
              'rivet', RED)
    for y in (TANK_Y0 + 0.035, ENG_Y0 - 0.035, TANK_Y1 - 0.035):
        fasteners(bm, (s * TANK_HW, y, 2.14), (s * TANK_HW, y, 3.34), n, 0.12, 'rivet', RED)
    fasteners(bm, (s * TANK_HW, TANK_Y0 + 0.30, 3.365), (s * TANK_HW, TANK_Y1 - 0.14, 3.365), n, 0.14, 'rivet', RED)
    # pressed beads on the tank side (below / above the logo band) and the rear upper panels
    for z in (2.28, 3.20):
        bead(bm, (s * TANK_HW, TANK_Y0 + 0.12, z), (s * TANK_HW, ENG_Y0 - 0.14, z), n, 0.045, 0.007, RED)
    for (ya, yb) in ((2.30, 3.10), (3.50, 4.40)):
        bead(bm, (s * (HB + 0.01), ya, 2.28), (s * (HB + 0.01), yb, 2.28), n, 0.04, 0.006, RED)
    # doors: piano hinge on the front edge, T-handle latch, two beads each
    for (y0, y1, z0, z1) in ((0.56, 2.00, 0.76, 1.52), (2.22, 3.20, 1.14, 1.52), (2.22, 3.20, 1.74, 2.58)):
        xd = s * (HB + 0.010)
        hinge(bm, (xd + s * 0.006, y0 + 0.012, z0 + 0.04), (xd + s * 0.006, y0 + 0.012, z1 - 0.04), 0.0075, 5, ZINC)
        zc = (z0 + z1) / 2
        cap_prism(bm, (xd, y1 - 0.07, zc), n, 0.022, 0.012, 12, ZINC)
        cyl(bm, (xd + s * 0.012, y1 - 0.07, zc), (xd + s * 0.035, y1 - 0.07, zc), 0.007, 8, ZINC)
        cyl(bm, (xd + s * 0.035, y1 - 0.07, zc - 0.045), (xd + s * 0.035, y1 - 0.07, zc + 0.045), 0.009, 8, DARK)
        if z1 - z0 > 0.5:
            for zz in (z0 + (z1 - z0) * 0.3, z0 + (z1 - z0) * 0.7):
                bead(bm, (xd, y0 + 0.14, zz), (xd, y1 - 0.18, zz), n, 0.04, 0.006, RED)
        else:
            bead(bm, (xd, y0 + 0.12, zc), (xd, y1 - 0.18, zc), n, 0.04, 0.006, RED)

# front face edges (above the feeder house) and the rear face
for x in (-0.92, 0.92):
    fasteners(bm, (x, -0.62, 1.05), (x, -0.62, 2.02), (0, -1, 0), 0.12, 'rivet', RED)
    fasteners(bm, (x, REAR_Y, 1.55), (x, REAR_Y, 2.36), (0, 1, 0), 0.12, 'rivet', RED)
fasteners(bm, (-0.90, -0.62, 2.03), (0.90, -0.62, 2.03), (0, -1, 0), 0.13, 'rivet', RED)
fasteners(bm, (-0.90, REAR_Y, 2.38), (0.90, REAR_Y, 2.38), (0, 1, 0), 0.13, 'rivet', RED)
# stiffening beads across the rear hood top
for y in (2.55, 3.05, 3.55, 4.05):
    bead(bm, (-0.80, y, REAR_TOP), (0.80, y, REAR_TOP), (0, 0, 1), 0.05, 0.007, RED)
fasteners(bm, (-0.92, 2.14, REAR_TOP), (-0.92, 4.50, REAR_TOP), (0, 0, 1), 0.15, 'rivet', RED)
fasteners(bm, (0.92, 2.14, REAR_TOP), (0.92, 4.50, REAR_TOP), (0, 0, 1), 0.15, 'rivet', RED)
# tank front face (visible from the cockpit)
for x in (-0.94, 0.94):
    fasteners(bm, (x, TANK_Y0, 2.16), (x, TANK_Y0, 3.10), (0, -1, 0), 0.12, 'rivet', RED)
bead(bm, (-0.62, TANK_Y0, 2.62), (0.22, TANK_Y0, 2.62), (0, -1, 0), 0.05, 0.007, RED)

ob = make_obj("z050_bodywork", bm, ["Z050_paint_red", "Z050_zinc", "Z050_metal_dark"], C, TAG)
print("bodywork:", len(ob.data.polygons), "faces")
