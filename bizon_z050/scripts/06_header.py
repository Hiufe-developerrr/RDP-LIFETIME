# 06 - 4.20 m grain header: trough with feeder opening, end plates, crop
# dividers, cutter bar with 55 guards (76.2 mm pitch) and knife, auger with
# opposed flights + centre fingers, 6-bat tine reel on hydraulic arms, drives.
TAG = "header"
purge_part(TAG)
C = coll("Z050_header420")
RED, CREAM, GRAY, DARK, STEEL, RUB = ("Z050_paint_red", "Z050_paint_cream", "Z050_paint_gray",
                                      "Z050_metal_dark", "Z050_steel", "Z050_rubber_black")
CHROME = "Z050_chrome"
W2 = 2.10                    # half cutting width (4.20 m)
EP = 2.135                   # end plate inner face
KNIFE = Vector((0.0, -3.00, 0.10))
AUG = Vector((0.0, -2.30, 0.42))
AUG_R = 0.155
REEL = Vector((0.0, -3.02, 0.94))
REEL_R = 0.50
ARM_PIV = Vector((0.0, -1.80, 1.34))
HROOT = Vector((0.0, -1.86, 0.74))


def thick_outline(pts, t):
    """Closed outline of a polyline offset by thickness t (to its left)."""
    P = [Vector(p) for p in pts]
    off = []
    for i in range(len(P)):
        if i == 0:
            d = P[1] - P[0]
        elif i == len(P) - 1:
            d = P[-1] - P[-2]
        else:
            d = (P[i + 1] - P[i]).normalized() + (P[i] - P[i - 1]).normalized()
        d.normalize()
        n = Vector((-d.y, d.x))
        off.append(P[i] + n * t)
    return [tuple(p) for p in P] + [tuple(p) for p in reversed(off)]


root = empty("header420", tuple(HROOT), C, TAG, size=0.6, kind='ARROWS')

# ------------------------------------------------------------- trough sheet
arc = [(AUG.y + 0.33 * cos(radians(a)), AUG.z + 0.33 * sin(radians(a))) for a in (-90, -70, -50, -30, -12)]
floor = [(-3.06, 0.135), (-2.95, 0.110), (-2.62, 0.095)] + arc
back_lo = [(-1.955, 0.40)]
back_hi = [(-1.90, 0.98), (-1.74, 1.24), (-1.82, 1.31), (-2.06, 1.31)]
full = floor + back_lo + back_hi
bm = bmesh.new()
for (x0, x1) in ((-EP, -0.58), (0.58, EP)):
    prism(bm, thick_outline(full, -0.005), 'X', x0, x1, 0)
# centre section: floor + lower lip, opening, then the upper back wall
prism(bm, thick_outline(floor[:-2], -0.005), 'X', -0.58, 0.58, 0)
prism(bm, thick_outline(back_hi, -0.005), 'X', -0.58, 0.58, 0)
# opening frame (flanged)
for x in (-0.60, 0.58):
    prism(bm, [(-2.05, 0.20), (-1.99, 0.20), (-1.86, 1.02), (-1.92, 1.02)], 'X', x, x + 0.02, 1)
# stiffeners and the top-back beam
box(bm, (-EP - 0.02, -1.84, 1.24), (EP + 0.02, -1.72, 1.34), 0)
for x in (-1.45, -0.80, 0.80, 1.45):
    prism(bm, [(-1.955, 0.40), (-1.93, 0.40), (-1.73, 1.22), (-1.76, 1.22)], 'X', x - 0.03, x + 0.03, 0)
# coupling hooks onto the feeder house
for x in (-0.45, 0.45):
    box(bm, (x - 0.04, -1.80, 1.16), (x + 0.04, -1.64, 1.22), 1)
    box(bm, (x - 0.04, -1.68, 1.08), (x + 0.04, -1.64, 1.22), 1)
# skid shoes
for x in (-1.55, 0.0, 1.55):
    tube(bm, [(x, -3.00, 0.075), (x, -2.70, 0.06), (x, -2.35, 0.07), (x, -2.10, 0.13)], 0.012, 6, mi=2,
         round_r=0.15)
    prism(bm, [(-2.98, 0.05), (-2.12, 0.08), (-2.12, 0.12), (-2.98, 0.08)], 'X', x - 0.035, x + 0.035, 2)
make_obj("z050h_trough", bm, [RED, DARK, STEEL], C, TAG, parent=root, bevel=0.004)

# ------------------------------------------------ end plates + crop dividers
bm = bmesh.new()
plate_out = [(-3.10, 0.10), (-2.96, 0.06), (-2.30, 0.045), (-1.955, 0.36), (-1.72, 1.24),
             (-1.82, 1.36), (-2.34, 1.16), (-2.98, 0.34)]
for s in (1, -1):
    x0, x1 = s * EP, s * (EP + 0.012)
    prism(bm, plate_out, 'X', min(x0, x1), max(x0, x1), 0)
    # folded edge flange + vertical stiffener
    xf0, xf1 = s * (EP + 0.012), s * (EP + 0.045)
    lo, hi = min(xf0, xf1), max(xf0, xf1)
    prism(bm, [(-2.98, 0.34), (-2.34, 1.16), (-2.30, 1.12), (-2.94, 0.32)], 'X', lo, hi, 0)
    prism(bm, [(-2.35, 0.10), (-2.29, 0.10), (-2.29, 1.10), (-2.35, 1.13)], 'X', lo, hi, 0)
    # crop divider: pointed sheet-metal nose ahead of the end plate
    xi = s * (EP - 0.14)
    xo = s * (EP + 0.012)
    tip = (s * (EP - 0.02), -3.62, 0.17)
    rings = [[(xo, -3.02, 0.06), (xo, -3.00, 0.46), (xi, -3.00, 0.30), (xi, -3.02, 0.08)],
             [(xo, -3.25, 0.08), (xo, -3.23, 0.36), (s * (EP - 0.09), -3.23, 0.25), (s * (EP - 0.09), -3.25, 0.09)],
             [(s * (EP + 0.005), -3.45, 0.12), (s * (EP + 0.005), -3.44, 0.25),
              (s * (EP - 0.05), -3.44, 0.20), (s * (EP - 0.05), -3.45, 0.12)]]
    loft(bm, rings, cap=True, mi=0)
    last = rings[-1]
    tv = bm.verts.new(tip)
    ring_v = [v for v in bm.verts if any((v.co - Vector(p)).length < 1e-6 for p in last)]
    ring_v = sorted(ring_v, key=lambda v: [((v.co - Vector(p)).length < 1e-6) for p in last].index(True))
    for i in range(4):
        try:
            bm.faces.new((ring_v[i], ring_v[(i + 1) % 4], tv))
        except ValueError:
            pass
    # long divider rod
    tube(bm, [(s * (EP - 0.03), -3.42, 0.24), (s * (EP - 0.03), -3.00, 0.62), (s * (EP - 0.03), -2.55, 0.98)],
         0.014, 8, mi=1, round_r=0.2)
make_obj("z050h_endPlates", bm, [RED, STEEL], C, TAG, parent=root, bevel=0.004)

# --------------------------------------------------- cutter bar + guards
bm = bmesh.new()
box(bm, (-W2 - 0.03, -3.03, 0.080), (W2 + 0.03, -2.95, 0.112), 0)
box(bm, (-W2 - 0.03, -2.97, 0.112), (W2 + 0.03, -2.93, 0.140), 0)
n_g = 55
pitch = 0.0762
g0 = -pitch * (n_g - 1) / 2
for i in range(n_g):
    x = g0 + i * pitch
    rings = []
    for (yy, w, h, dz) in ((-2.96, 0.040, 0.030, 0.0), (-3.04, 0.034, 0.028, 0.0), (-3.10, 0.024, 0.022, 0.004),
                           (-3.15, 0.016, 0.016, 0.010), (-3.185, 0.008, 0.009, 0.018)):
        z = 0.090 + dz
        rings.append([(x - w / 2, yy, z - h / 2), (x + w / 2, yy, z - h / 2), (x + w * 0.35, yy, z + h / 2),
                      (x - w * 0.35, yy, z + h / 2)])
    loft(bm, rings, cap=True, mi=1)
    box(bm, (x - 0.012, -2.99, 0.112), (x + 0.012, -2.95, 0.128), 1)
make_obj("z050h_cutterBar", bm, [DARK, STEEL], C, TAG, parent=root)

bm = bmesh.new()
box(bm, (-W2, -3.00, 0.098), (W2, -2.965, 0.108), 0)
for i in range(n_g):
    x = g0 + i * pitch
    plate(bm, [(x - 0.037, -2.99, 0.104), (x + 0.037, -2.99, 0.104), (x + 0.006, -3.085, 0.104),
               (x - 0.006, -3.085, 0.104)], 0.003, (0, 0, 1), mi=1)
# knife head + wobble box drive at the left end
box(bm, (W2 - 0.02, -3.01, 0.10), (W2 + 0.10, -2.94, 0.15), 0)
knife = make_obj("knife", bm, [DARK, STEEL], C, TAG, origin=tuple(KNIFE), parent=root)
bm = bmesh.new()
box(bm, (EP + 0.05, -2.95, 0.12), (EP + 0.20, -2.60, 0.36), 0)
cyl(bm, (EP + 0.20, -2.78, 0.30), (EP + 0.26, -2.78, 0.30), 0.08, 18, 1)
tube(bm, [(EP + 0.12, -2.95, 0.20), (EP + 0.12, -3.00, 0.15), (W2 + 0.06, -3.00, 0.15)], 0.018, 8, mi=0,
     round_r=0.03)
make_obj("z050h_knifeDrive", bm, [DARK, RED], C, TAG, parent=root, bevel=0.004)

# ------------------------------------------------------------------ auger
aug_root = empty("auger", tuple(AUG), C, TAG, parent=root, size=0.35, kind='SINGLE_ARROW')
bm = bmesh.new()
cyl(bm, (-2.10, AUG.y, AUG.z), (2.10, AUG.y, AUG.z), AUG_R, 32, 0)
for x in (-2.10, 2.10):
    cyl(bm, (x - 0.004, AUG.y, AUG.z), (x + 0.004, AUG.y, AUG.z), AUG_R + 0.01, 32, 0)
cyl(bm, (-EP - 0.06, AUG.y, AUG.z), (EP + 0.06, AUG.y, AUG.z), 0.035, 16, 2)
helix_flight(bm, AUG.y, AUG.z, 0.58, 2.06, AUG_R - 0.005, 0.30, 0.56, 0.006, hand=1, mi=0)
helix_flight(bm, AUG.y, AUG.z, -0.58, -2.06, AUG_R - 0.005, 0.30, 0.56, 0.006, hand=1, mi=0)
for j, x in enumerate((-0.46, -0.28, -0.09, 0.09, 0.28, 0.46)):
    for k in range(2):
        a = radians(30 + 180 * k + 60 * j)
        d = Vector((0, cos(a), sin(a)))
        p0 = AUG + Vector((x, 0, 0)) + d * (AUG_R - 0.01)
        cyl(bm, p0, p0 + d * 0.20, 0.011, 8, 1)
        cyl(bm, p0 - d * 0.004, p0 + d * 0.02, 0.022, 10, 1)
make_obj("augerMesh", bm, [RED, STEEL, DARK], C, TAG, origin=tuple(AUG), parent=aug_root)

# ------------------------------------------------------------ reel + arms
arms = empty("reelArms", tuple(ARM_PIV), C, TAG, parent=root, size=0.35)
bm = bmesh.new()
for s_ in (1, -1):
    x = s_ * (EP + 0.075)
    a0 = Vector((x, ARM_PIV.y, ARM_PIV.z))
    a1 = Vector((x, REEL.y - 0.02, REEL.z + 0.06))
    b0 = a0 + Vector((0, -0.04, -0.16))
    b1 = a1 + Vector((0, 0.10, -0.04))
    sq = [(-0.022, -0.022), (0.022, -0.022), (0.022, 0.022), (-0.022, 0.022)]
    sweep(bm, [a0, a1], sq, mi=0, up=(1, 0, 0))
    sweep(bm, [b0, b1], [(u * 0.8, v * 0.8) for (u, v) in sq], mi=0, up=(1, 0, 0))
    for k in range(5):
        t0, t1 = k / 5, (k + 1) / 5
        p = a0.lerp(a1, t0) if k % 2 == 0 else b0.lerp(b1, t0)
        q = b0.lerp(b1, t1) if k % 2 == 0 else a0.lerp(a1, t1)
        tube(bm, [p, q], 0.011, 8, mi=0)
    tube(bm, [a0, b0], 0.014, 8, mi=0)
    cyl(bm, (x - 0.05, ARM_PIV.y, ARM_PIV.z), (x + 0.05, ARM_PIV.y, ARM_PIV.z), 0.04, 14, 1)
    flange_bearing(bm, (x + s_ * 0.022, REEL.y, REEL.z), (s_, 0, 0), 0.06, 1, 2, bolts=4)
    for t in (0.3, 0.62):                                          # adjustment holes plate
        c_ = a0.lerp(a1, t) + Vector((s_ * 0.024, 0, 0))
        nut(bm, c_, (s_, 0, 0), af=0.016, h=0.007, mi=2)
    t_top = Vector((x, ARM_PIV.y + (REEL.y - ARM_PIV.y) * 0.55, ARM_PIV.z + (REEL.z - ARM_PIV.z) * 0.55))
    tube(bm, [t_top, t_top + Vector((0, 0.10, -0.22))], 0.02, 8, mi=0)
ARM_MESH = make_obj("reelArmsMesh", bm, [RED, DARK, "Z050_zinc"], C, TAG, origin=tuple(ARM_PIV), parent=arms,
                    bevel=0.003)

# reel lift cylinders (header -> arms), static approximation
bm = bmesh.new()
for s in (1, -1):
    x = s * (EP + 0.075)
    p0 = Vector((x, -2.12, 0.62))
    p1 = Vector((x, ARM_PIV.y + (REEL.y - ARM_PIV.y) * 0.55 + 0.10, ARM_PIV.z + (REEL.z - ARM_PIV.z) * 0.55 - 0.22))
    m = p0.lerp(p1, 0.55)
    cyl(bm, p0, m, 0.032, 14, 0)
    cyl(bm, m, p1, 0.016, 10, 1)
    box(bm, (min(s * EP, x) - 0.0, -2.18, 0.56), (max(s * EP, x), -2.06, 0.66), 0)
make_obj("z050h_reelLift", bm, [DARK, CHROME], C, TAG, parent=root)

reel_root = empty("reel", tuple(REEL), C, TAG, parent=arms, size=0.5, kind='CIRCLE')
bm = bmesh.new()
cyl(bm, (-EP - 0.05, REEL.y, REEL.z), (EP + 0.05, REEL.y, REEL.z), 0.045, 16, 0)
n_bats = 6
for xs in (-2.02, 0.0, 2.02):
    cyl(bm, (xs - 0.05, REEL.y, REEL.z), (xs + 0.05, REEL.y, REEL.z), 0.085, 18, 0)
    for k in range(n_bats):
        a = 2 * pi * k / n_bats
        d = Vector((0, cos(a), sin(a)))
        prof = [(-0.006, -0.025), (0.006, -0.025), (0.006, 0.025), (-0.006, 0.025)]
        p0 = REEL + Vector((xs, 0, 0)) + d * 0.07
        p1 = REEL + Vector((xs, 0, 0)) + d * (REEL_R - 0.01)
        sweep(bm, [p0, p1], [(v, u) for (u, v) in prof], mi=0, up=(1, 0, 0))
        # diagonal brace between spider arms
        if xs == 0.0:
            a2 = a + 2 * pi / n_bats
            q = REEL + d * 0.32
            q2 = REEL + Vector((0, cos(a2), sin(a2))) * 0.32
            tube(bm, [q, q2], 0.01, 6, mi=0)
for k in range(n_bats):
    a = 2 * pi * k / n_bats
    d = Vector((0, cos(a), sin(a)))
    bc = REEL + d * REEL_R
    cyl(bm, (-2.06, bc.y, bc.z), (2.06, bc.y, bc.z), 0.024, 12, 1)
    # spring tines along the bat, swept back against the rotation
    tangent = Vector((0, -sin(a), cos(a)))
    for i in range(40):
        x = -1.99 + i * 0.102
        p0 = Vector((x, bc.y, bc.z))
        p1 = p0 + d * 0.06 + tangent * 0.01
        p2 = p0 + d * 0.17 - tangent * 0.035
        tube(bm, [p0, p1, p2], 0.0045, 6, mi=2)
        coil = [p0 + d * 0.012 + (Vector((1, 0, 0)) * 0.0 + d * cos(t) * 0.011 + tangent * sin(t) * 0.011)
                for t in [2 * pi * j / 6 for j in range(6)]]
        sweep(bm, coil, circle2d(0.0032, 4), closed=True, mi=2)
# eccentric spider (keeps the tines pointing down) on the right end, with cranks
ecc = Vector((0.0, 0.07, 0.0))
xe = -2.10
cyl(bm, (xe - 0.03, REEL.y + ecc.y, REEL.z + ecc.z), (xe + 0.03, REEL.y + ecc.y, REEL.z + ecc.z), 0.075, 20, 0)
for k in range(n_bats):
    a = 2 * pi * k / n_bats
    d = Vector((0, cos(a), sin(a)))
    p0 = REEL + ecc + Vector((xe, 0, 0)) + d * 0.07
    p1 = REEL + ecc + Vector((xe, 0, 0)) + d * (REEL_R - 0.01)
    sweep(bm, [p0, p1], [(0.025, -0.006), (0.025, 0.006), (-0.025, 0.006), (-0.025, -0.006)], mi=0, up=(1, 0, 0))
    bc = REEL + d * REEL_R
    crank0 = Vector((-2.075, bc.y, bc.z))
    crank1 = crank0 + ecc + Vector((-0.02, 0, 0))
    tube(bm, [crank0, crank1], 0.009, 6, mi=0)
    cyl(bm, crank1 - Vector((0.012, 0, 0)), crank1 + Vector((0.012, 0, 0)), 0.02, 10, 2)
make_obj("reelMesh", bm, [RED, GRAY, STEEL], C, TAG, origin=tuple(REEL), parent=reel_root)

# -------------------------------------------------------- header drives (L)
HIN = (-1.72, 1.10)                  # cross shaft behind the back wall (input from the feeder belt)
BIG = (-2.25, 0.88)                  # countershaft on the left end plate
XP, XC, XR = EP + 0.165, EP + 0.085, EP + 0.225
bm = bmesh.new()
cyl(bm, (0.66, HIN[0], HIN[1]), (XP + 0.04, HIN[0], HIN[1]), 0.025, 12, 1)
spoked_pulley(bm, HIN, 0.14, 0.72, 0.035, 1, 5, 0, 1)
for x in (0.86, 1.45, EP - 0.02):
    flange_bearing(bm, (x, HIN[0], HIN[1]), (-1 if x < 2 else 1, 0, 0), 0.05, 3, 1)
    box(bm, (x - 0.012, HIN[0] - 0.05, HIN[1] - 0.06), (x + 0.012, HIN[0] + 0.03, HIN[1] + 0.06), 3)
spoked_pulley(bm, HIN, 0.09, XP, 0.035, 1, 0, 0, 1)
spoked_pulley(bm, BIG, 0.28, XP, 0.035, 1, 6, 0, 1)
pts = belt_path([(HIN[0], HIN[1], 0.09 * 0.93), (BIG[0], BIG[1], 0.28 * 0.93)], 12)
sweep(bm, [(XP, y, z) for (y, z) in pts[:-1]], [(-0.006, -0.0065), (0.006, -0.0065), (0.006, 0.0065), (-0.006, 0.0065)],
      closed=True, mi=2, up=(1, 0, 0))
cyl(bm, (EP, BIG[0], BIG[1]), (XR + 0.03, BIG[0], BIG[1]), 0.028, 12, 1)
flange_bearing(bm, (EP + 0.012, BIG[0], BIG[1]), (1, 0, 0), 0.06, 3, 1, bolts=4)
# auger chain (countershaft -> auger) with a spring loaded idler sprocket
ra = sprocket(bm, BIG, XC - 0.004, XC + 0.004, 25, mi=4, hub_mi=1)
rb = 0.01905 / (2 * sin(pi / 34))
ID = (-2.05, 0.62)
ri = sprocket(bm, ID, XC - 0.004, XC + 0.004, 11, mi=4, hub_mi=1)
roller_chain(bm, belt_path([(BIG[0], BIG[1], ra), (AUG.y, AUG.z, rb), (ID[0], ID[1], ri)], 14), XC, mi=4)
tube(bm, [(XC + 0.02, ID[0], ID[1]), (XC + 0.02, -1.99, 0.74)], 0.01, 8, mi=1)
spring(bm, (XC + 0.02, -1.99, 0.74), (XC + 0.02, -1.96, 0.92), 0.012, 0.0026, 10, mi=1)
# reel drive: countershaft -> arm pivot shaft
rr1 = sprocket(bm, BIG, XR - 0.004, XR + 0.004, 13, mi=4, hub_mi=1)
PV = (ARM_PIV.y, ARM_PIV.z)
rr2 = sprocket(bm, PV, XR - 0.004, XR + 0.004, 21, mi=4, hub_mi=1)
roller_chain(bm, belt_path([(BIG[0], BIG[1], rr1), (PV[0], PV[1], rr2)], 14), XR, mi=4)
cyl(bm, (EP + 0.03, PV[0], PV[1]), (XR + 0.03, PV[0], PV[1]), 0.022, 12, 1)
# knife drive: pulley on the wobble box, belt from the auger shaft pulley
WB = (-2.70, 0.30)
XK = EP + 0.265
spoked_pulley(bm, WB, 0.10, XK, 0.03, 1, 0, 0, 1)
cyl(bm, (EP + 0.20, WB[0], WB[1]), (XK + 0.02, WB[0], WB[1]), 0.02, 10, 1)
pts = belt_path([(AUG.y, AUG.z, 0.07 * 0.93), (WB[0], WB[1], 0.10 * 0.93)], 12)
sweep(bm, [(XK, y, z) for (y, z) in pts[:-1]], [(-0.005, -0.006), (0.005, -0.006), (0.005, 0.006), (-0.005, 0.006)],
      closed=True, mi=2, up=(1, 0, 0))
# drive shield behind the pulleys
prism(bm, [(-2.58, 0.60), (-1.90, 0.66), (-1.66, 1.10), (-1.80, 1.26), (-2.20, 1.24), (-2.56, 1.12)], 'X',
      EP + 0.125, EP + 0.131, 0)
for (y, z) in ((-2.50, 0.68), (-1.95, 0.72), (-1.78, 1.18), (-2.45, 1.14)):
    nut(bm, (EP + 0.131, y, z), (1, 0, 0), af=0.014, h=0.006, mi=1, washer=False)
make_obj("z050h_drives", bm, [RED, STEEL, "Z050_belt", DARK, "Z050_chain"], C, TAG, parent=root)

# rotating parts on the auger shaft and the reel shaft (join into those meshes)
bm = bmesh.new()
sprocket(bm, (AUG.y, AUG.z), XC - 0.004, XC + 0.004, 34, mi=1, hub_mi=0)
spoked_pulley(bm, (AUG.y, AUG.z), 0.07, XK, 0.03, 1, 0, 0, 0)
cyl(bm, (EP + 0.06, AUG.y, AUG.z), (XK + 0.02, AUG.y, AUG.z), 0.03, 12, 0)
spoked_pulley(bm, (AUG.y, AUG.z), 0.12, EP + 0.03, 0.02, 1, 0, 0, 0)          # slip clutch plate
for k in range(6):
    a = 2 * pi * k / 6
    nut(bm, (EP + 0.04, AUG.y + 0.08 * cos(a), AUG.z + 0.08 * sin(a)), (1, 0, 0), af=0.013, h=0.006, mi=0, stud=True)
ob = make_obj("z050h_augerDrive", bm, [STEEL, "Z050_chain"], C, TAG)
ob["attach"] = "augerMesh"
bm = bmesh.new()
XRC = EP + 0.13
r_a = sprocket(bm, PV, XRC - 0.004, XRC + 0.004, 15, mi=1, hub_mi=0)
r_b = 0.01905 / (2 * sin(pi / 30))
roller_chain(bm, belt_path([(PV[0], PV[1], r_a), (REEL.y, REEL.z, r_b)], 14), XRC, mi=1)
guard = [(PV[0] + 0.07, PV[1] + 0.02), (REEL.y - 0.05, REEL.z + 0.14), (REEL.y - 0.12, REEL.z + 0.06),
         (PV[0] + 0.02, PV[1] - 0.07)]
prism(bm, guard, 'X', XRC + 0.02, XRC + 0.025, 2)
ob = make_obj("z050h_reelChain", bm, [STEEL, "Z050_chain", RED], C, TAG)
ob["attach"] = "reelArmsMesh"
bm = bmesh.new()
sprocket(bm, (REEL.y, REEL.z), XRC - 0.004, XRC + 0.004, 30, mi=1, hub_mi=0)
cyl(bm, (EP + 0.05, REEL.y, REEL.z), (XRC + 0.02, REEL.y, REEL.z), 0.03, 12, 0)
ob = make_obj("z050h_reelSprocket", bm, [STEEL, "Z050_chain"], C, TAG)
ob["attach"] = "reelMesh"

# hoses from the reel cylinders to the quick couplers on the feeder house
bm = bmesh.new()
hose(bm, [(EP + 0.075, -2.10, 0.70), (EP + 0.075, -1.80, 0.92), (EP + 0.03, -1.70, 1.37), (-0.80, -1.70, 1.37),
          (-0.80, -1.64, 1.26), (-0.787, -1.635, 1.20)], 0.0105, 0, 1, 0.1)
hose(bm, [(-EP - 0.075, -2.10, 0.70), (-EP - 0.075, -1.80, 0.92), (-EP - 0.03, -1.74, 1.00), (-0.86, -1.74, 1.00),
          (-0.82, -1.60, 1.14), (-0.787, -1.565, 1.20)], 0.0105, 0, 1, 0.1)
for x in (-1.9, -1.3, 1.3, 1.9):
    for z in (1.00, 1.37):
        if (x < 0 and z < 1.2) or (x > 0 and z > 1.2):
            box_c(bm, (x, -1.70 if z > 1.2 else -1.74, z), (0.02, 0.035, 0.035), 1)
# rivets along the top-back beam and the end plate edges
for z in (1.26, 1.32):
    fasteners(bm, (-2.10, -1.84, z), (2.10, -1.84, z), (0, -1, 0), 0.15, 'rivet', 2)
for s_ in (1, -1):
    x = s_ * (EP + 0.012)
    fasteners(bm, (x, -2.96, 0.36), (x, -2.36, 1.14), (s_, 0, 0), 0.1, 'rivet', 2)
    fasteners(bm, (x, -2.28, 0.10), (x, -1.99, 0.40), (s_, 0, 0), 0.1, 'rivet', 2)
make_obj("z050h_hoses", bm, ["Z050_hose", "Z050_zinc", RED], C, TAG, parent=root)

print("header objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
