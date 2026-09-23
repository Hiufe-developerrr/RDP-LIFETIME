# 02 - thresher body, grain tank + engine bay, feeder house, platform frame,
# front drive axle with final drives, rear steering axle.
TAG = "chassis"
purge_part(TAG)
C = coll("Z050_combine")
RED, CREAM, GRAY, DARK, STEEL, RUB = ("Z050_paint_red", "Z050_paint_cream", "Z050_paint_gray",
                                      "Z050_metal_dark", "Z050_steel", "Z050_rubber_black")

# ---------------------------------------------------------------- lower body
bm = bmesh.new()
side = [(-0.62, 1.00), (0.28, 0.98), (0.45, 0.66), (2.55, 0.66), (3.05, 1.02), (4.60, 1.15),
        (REAR_Y, 1.50), (REAR_Y, 2.40), (4.55, REAR_TOP), (2.10, REAR_TOP), (2.10, 2.06), (-0.62, 2.06)]
prism(bm, side, 'X', -HB, HB, mi=0)
make_obj("z050_bodyLower", bm, [RED], C, TAG, bevel=0.018)

# body side furniture: belt-line ribs, vertical U-ribs, doors, rear sieve covers
bm = bmesh.new()
for s in (1, -1):
    x0, x1 = s * HB, s * (HB + 0.028)
    lo, hi = min(x0, x1), max(x0, x1)
    box(bm, (lo, -0.58, 1.60), (hi, 4.55, 1.66), 0)                   # belt line
    box(bm, (lo, 2.14, 2.66), (hi, 4.50, 2.71), 0)                    # upper rear rib
    for y in (0.46, 2.10, 3.30):
        zb = 0.70 if y < 2.6 else 1.08
        zt = 2.02 if y < 2.1 else REAR_TOP - 0.06
        box(bm, (lo, y - 0.035, zb), (hi, y + 0.035, zt), 0)
    # rear sieve side cover (cream, like the Z050 in the photos)
    x2 = s * (HB + 0.012)
    box(bm, (min(x0, x2), 3.62, 1.22), (max(x0, x2), 4.86, 1.56), 1)
    # access doors with hinges + handles
    for (y0, y1, z0, z1) in ((0.56, 2.00, 0.76, 1.52), (2.22, 3.20, 1.14, 1.52), (2.22, 3.20, 1.74, 2.58)):
        xd = s * (HB + 0.010)
        box(bm, (min(x0, xd), y0, z0), (max(x0, xd), y1, z1), 0)
        for z in (z0 + 0.08, z1 - 0.08):
            cyl(bm, (xd + s * 0.012, y0 - 0.005, z - 0.05), (xd + s * 0.012, y0 - 0.005, z + 0.05), 0.012, 8, 2)
        yh = y1 - 0.09
        zc = (z0 + z1) / 2
        cyl(bm, (xd, yh, zc), (xd + s * 0.045, yh, zc), 0.010, 8, 2)
        cyl(bm, (xd + s * 0.045, yh, zc - 0.05), (xd + s * 0.045, yh, zc + 0.05), 0.011, 8, 2)
make_obj("z050_bodyRibs", bm, [RED, CREAM, STEEL], C, TAG, bevel=0.004)

# ------------------------------------------------ grain tank + engine bay box
bm = bmesh.new()
tank = [(TANK_Y0, 2.02), (TANK_Y0, 3.16), (TANK_Y0 + 0.24, TANK_TOP), (TANK_Y1 - 0.10, TANK_TOP),
        (TANK_Y1, TANK_TOP - 0.10), (TANK_Y1, 2.02)]
prism(bm, tank, 'X', -TANK_HW, TANK_HW, mi=0)
# drip lip where the tank sits on the body
for s in (1, -1):
    a, b = s * TANK_HW, s * (TANK_HW + 0.02)
    box(bm, (min(a, b), TANK_Y0 - 0.02, 2.02), (max(a, b), TANK_Y1 + 0.02, 2.08), 0)
# seam trim between grain tank and engine bay (wraps over the top)
seam = [(-TANK_HW - 0.012, 2.08), (-TANK_HW - 0.012, TANK_TOP + 0.012),
        (TANK_HW + 0.012, TANK_TOP + 0.012), (TANK_HW + 0.012, 2.08)]
prof = [(-0.03, -0.012), (0.03, -0.012), (0.03, 0.012), (-0.03, 0.012)]
sweep(bm, [(x, ENG_Y0, z) for (x, z) in seam], [(v, u) for (u, v) in prof], mi=0, up=(0, 1, 0))
make_obj("z050_grainTank", bm, [RED], C, TAG, bevel=0.02)

# tank lids (hinged covers) + engine hood grate on top
bm = bmesh.new()
box(bm, (-0.86, TANK_Y0 + 0.30, TANK_TOP), (0.86, ENG_Y0 - 0.08, TANK_TOP + 0.035), 0)   # lid frame
for (x0, x1) in ((-0.82, -0.02), (0.02, 0.82)):
    box(bm, (x0, TANK_Y0 + 0.34, TANK_TOP + 0.035), (x1, ENG_Y0 - 0.12, TANK_TOP + 0.06), 0)
    xc = (x0 + x1) / 2
    tube(bm, [(xc - 0.12, ENG_Y0 - 0.16, TANK_TOP + 0.06), (xc - 0.12, ENG_Y0 - 0.20, TANK_TOP + 0.11),
              (xc + 0.12, ENG_Y0 - 0.20, TANK_TOP + 0.11), (xc + 0.12, ENG_Y0 - 0.16, TANK_TOP + 0.06)],
         0.011, 8, mi=2, round_r=0.03)
    for yy in (TANK_Y0 + 0.40, ENG_Y0 - 0.30):
        cyl(bm, (x0 + 0.05, yy, TANK_TOP + 0.06), (x0 + 0.05, yy + 0.09, TANK_TOP + 0.06), 0.014, 8, 2)
# engine hood with a perforated air grate (slats)
box(bm, (-0.90, ENG_Y0 + 0.06, TANK_TOP), (0.90, TANK_Y1 - 0.16, TANK_TOP + 0.03), 0)
box(bm, (-0.62, ENG_Y0 + 0.16, TANK_TOP + 0.03), (0.10, TANK_Y1 - 0.26, TANK_TOP + 0.036), 1)
for i in range(9):
    y = ENG_Y0 + 0.20 + i * 0.065
    box(bm, (-0.60, y, TANK_TOP + 0.036), (0.08, y + 0.022, TANK_TOP + 0.07), 0)
# grain level window facing the operator
box(bm, (-0.30, TANK_Y0 - 0.025, 2.70), (0.30, TANK_Y0, 2.98), 1)
box(bm, (-0.26, TANK_Y0 - 0.03, 2.74), (0.26, TANK_Y0 - 0.02, 2.94), 3)
make_obj("z050_tankTop", bm, [RED, DARK, STEEL, "Z050_glass"], C, TAG, bevel=0.005)

# louvered radiator grille (left side) + smaller intake grille (right side)
bm = bmesh.new()


def louvers(bm, x, s, y0, y1, z0, z1, n, depth=0.05, fw=0.045, tilt=radians(38)):
    xo = x + s * depth
    lo, hi = min(x, xo), max(x, xo)
    box(bm, (lo, y0, z1 - fw), (hi, y1, z1), 0)
    box(bm, (lo, y0, z0), (hi, y1, z0 + fw), 0)
    box(bm, (lo, y0, z0), (hi, y0 + fw, z1), 0)
    box(bm, (lo, y1 - fw, z0), (hi, y1, z1), 0)
    xb = x + s * 0.004
    box(bm, (min(x, xb), y0 + fw, z0 + fw), (max(x, xb), y1 - fw, z1 - fw), 1)
    h = (z1 - z0 - 2 * fw) / n
    for i in range(n):
        zc = z0 + fw + h * (i + 0.5)
        vs, _ = box_c(bm, (x + s * depth * 0.55, (y0 + y1) / 2, zc), (0.004, y1 - y0 - 2 * fw, h * 1.28), 0)
        rotate_verts(bm, vs, -s * tilt, 'Y', (x + s * depth * 0.55, 0, zc))


louvers(bm, TANK_HW, 1, ENG_Y0 + 0.10, TANK_Y1 - 0.12, 2.38, 3.26, 13)
louvers(bm, -TANK_HW, -1, ENG_Y0 + 0.30, TANK_Y1 - 0.20, 2.70, 3.18, 7)
make_obj("z050_radiatorGrille", bm, [RED, DARK], C, TAG, bevel=0.003)

# ----------------------------------------------------- operator platform frame
bm = bmesh.new()
# steel floor plate (own material: paint worn through by boots)
box(bm, (-PLAT_HW, PLAT_Y0, PLAT_Z - 0.05), (PLAT_HW, PLAT_Y1, PLAT_Z), 3)
for x in (-PLAT_HW + 0.045, PLAT_HW - 0.045):
    fasteners(bm, (x, PLAT_Y0 + 0.07, PLAT_Z), (x, PLAT_Y1 - 0.07, PLAT_Z), (0, 0, 1), 0.19, 'rivet', 3,
              r=0.0085, h=0.0022)
for y in (PLAT_Y0 + 0.045, PLAT_Y0 + 0.62, PLAT_Y1 - 0.045):
    fasteners(bm, (-PLAT_HW + 0.14, y, PLAT_Z), (PLAT_HW - 0.14, y, PLAT_Z), (0, 0, 1), 0.21, 'rivet', 3,
              r=0.0085, h=0.0022)
cyl(bm, (0.52, -1.02, PLAT_Z - 0.052), (0.52, -1.02, PLAT_Z + 0.001), 0.018, 12, 1)       # drain hole plug
# longitudinal beams + diagonal struts down to the body front
for s in (1, -1):
    x = s * 0.78
    box(bm, (x - 0.04, PLAT_Y0 + 0.05, PLAT_Z - 0.17), (x + 0.04, -0.60, PLAT_Z - 0.05), 1)
    tube(bm, [(x, PLAT_Y0 + 0.35, PLAT_Z - 0.16), (x * 0.95, -0.64, 1.30)], 0.035, 10, mi=1)
    for (y, z) in ((PLAT_Y0 + 0.35, PLAT_Z - 0.16), (-0.64, 1.30)):
        box(bm, (x * (0.95 if z < 2 else 1.0) - 0.05, y - 0.04, z - 0.05), (x * (0.95 if z < 2 else 1.0) + 0.05, y + 0.04, z + 0.02), 1)
# red front wall under the railing (carries the headlights), rolled top edge, bottom flange
box(bm, (-0.93, PLAT_Y0 - 0.11, 1.78), (0.93, PLAT_Y0 - 0.01, PLAT_Z + 0.06), 0)
cyl(bm, (-0.935, PLAT_Y0 - 0.06, PLAT_Z + 0.06), (0.935, PLAT_Y0 - 0.06, PLAT_Z + 0.06), 0.022, 12, 0)
box(bm, (-0.94, PLAT_Y0 - 0.14, 1.76), (0.94, PLAT_Y0 - 0.01, 1.79), 0)
for x in (-0.62, 0.0, 0.62):
    bead(bm, (x - 0.22, PLAT_Y0 - 0.11, 1.90), (x + 0.22, PLAT_Y0 - 0.11, 1.90), (0, -1, 0), 0.04, 0.006, 0)
fasteners(bm, (-0.90, PLAT_Y0 - 0.14, 1.775), (0.90, PLAT_Y0 - 0.14, 1.775), (0, -1, 0), 0.15, 'bolt', 4,
          af=0.015, h=0.006, washer=False)
# toe board along the platform sides
for s in (1, -1):
    a, b = s * PLAT_HW, s * (PLAT_HW + 0.02)
    box(bm, (min(a, b), PLAT_Y0, PLAT_Z - 0.12), (max(a, b), PLAT_Y1, PLAT_Z + 0.06), 0)
make_obj("z050_platform", bm, [RED, DARK, CREAM, "Z050_paint_red_floor", "Z050_zinc"], C, TAG, bevel=0.006)

# --------------------------------------------------- feeder house (movable)
bm = bmesh.new()
fh = [(-0.58, 1.90), (-1.66, 1.06), (-1.84, 0.36), (-0.60, 1.08)]
prism(bm, fh, 'X', -0.60, 0.60, mi=0)
# top lip + side ribs + wear strips
for s in (1, -1):
    x0, x1 = s * 0.60, s * 0.625
    lo, hi = min(x0, x1), max(x0, x1)
    for t in (0.25, 0.55, 0.85):
        ya, za = -0.58 + (-1.66 + 0.58) * t, 1.90 + (1.06 - 1.90) * t
        yb, zb = -0.60 + (-1.84 + 0.60) * t, 1.08 + (0.36 - 1.08) * t
        prism(bm, [(ya - 0.03, za), (ya + 0.03, za), (yb + 0.03, zb), (yb - 0.03, zb)], 'X', lo, hi, 0)
# front mounting frame for the header
prism(bm, [(-1.62, 1.12), (-1.70, 1.12), (-1.90, 0.32), (-1.82, 0.32)], 'X', -0.68, 0.68, 1)
# lift cylinder lugs under the feeder
for s in (1, -1):
    box(bm, (s * 0.42 - 0.03, -1.30, 0.58), (s * 0.42 + 0.03, -1.12, 0.66), 1)
fh_ob = make_obj("feederHouse", bm, [RED, DARK], C, TAG, origin=FEEDER_PIVOT, bevel=0.012)
fh_ob["keep"] = True

# header lift cylinders (from front axle to feeder house)
bm = bmesh.new()
for s in (1, -1):
    p0 = Vector((s * 0.42, -0.30, 0.72))
    p1 = Vector((s * 0.42, -1.21, 0.62))
    mid = p0.lerp(p1, 0.55)
    cyl(bm, p0, mid, 0.045, 14, 0)
    cyl(bm, mid, p1, 0.022, 10, 1)
    cyl(bm, (s * 0.42 - 0.04, p0.y, p0.z), (s * 0.42 + 0.04, p0.y, p0.z), 0.05, 12, 0)
make_obj("z050_liftCylinders", bm, [DARK, "Z050_chrome"], C, TAG)["keep"] = True

# ------------------------------------------ front drive axle and final drives
bm = bmesh.new()
cyl(bm, (-1.02, 0, FW_R), (1.02, 0, FW_R), 0.085, 20, 0)
box(bm, (-0.30, -0.22, FW_R - 0.20), (0.30, 0.24, FW_R + 0.22), 0)          # gearbox / diff
cyl(bm, (0.0, 0.24, FW_R + 0.05), (0.0, 0.42, FW_R + 0.05), 0.07, 14, 0)     # input shaft housing
for s in (1, -1):
    # final drive housing (round gear case) against the body side
    revolve(bm, [(0.0, s * 0.955), (0.23, s * 0.955), (0.25, s * 0.975), (0.25, s * 1.055),
                 (0.20, s * 1.075), (0.0, s * 1.075)], 28, center=(0, 0, FW_R), axis='X', mi=0)
    bolt_ring(bm, (s * 1.075, 0, FW_R), (s, 0, 0), 0.215, 12, 0.012, 0.012, mi=1)
    # brake drum
    revolve(bm, [(0.0, s * 0.80), (0.16, s * 0.80), (0.16, s * 0.93), (0.0, s * 0.93)], 24,
            center=(0, 0, FW_R), axis='X', mi=0)
make_obj("z050_frontAxle", bm, [DARK, STEEL], C, TAG, bevel=0.006)

# ------------------------------------------------ rear steering axle (pendulum)
rear_pivot = (0.0, RW_Y, 0.47)
bm = bmesh.new()
box(bm, (-0.74, RW_Y - 0.065, 0.40), (0.74, RW_Y + 0.065, 0.54), 0)         # beam
box(bm, (-0.16, RW_Y - 0.10, 0.54), (0.16, RW_Y + 0.10, 0.62), 0)          # pivot block
cyl(bm, (0, RW_Y - 0.20, 0.585), (0, RW_Y + 0.20, 0.585), 0.045, 14, 1)     # pendulum pin
for s in (1, -1):
    cyl(bm, (s * 0.78, RW_Y, 0.34), (s * 0.78, RW_Y, 0.60), 0.052, 16, 0)   # kingpin boss
make_obj("rearAxle", bm, [DARK, STEEL], C, TAG, origin=rear_pivot, bevel=0.008)["keep"] = True

# pendulum bracket on the body
bm = bmesh.new()
for yy in (RW_Y - 0.22, RW_Y + 0.14):
    box(bm, (-0.14, yy, 0.55), (0.14, yy + 0.08, 1.12), 0)
box(bm, (-0.30, RW_Y - 0.30, 1.05), (0.30, RW_Y + 0.30, 1.14), 0)
make_obj("z050_rearAxleMount", bm, [DARK], C, TAG, bevel=0.008)

# towing hitch at the rear
bm = bmesh.new()
box(bm, (-0.22, 4.55, 1.02), (0.22, 4.88, 1.14), 0)
box(bm, (-0.05, 4.80, 0.86), (0.05, 5.02, 1.06), 0)
revolve(bm, [(0.035, -0.03), (0.07, -0.03), (0.07, 0.03), (0.035, 0.03)], 16,
        center=(0, 5.06, 0.95), axis='X', mi=0, closed=True)
make_obj("z050_hitch", bm, [DARK], C, TAG, bevel=0.005)

print("chassis objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
