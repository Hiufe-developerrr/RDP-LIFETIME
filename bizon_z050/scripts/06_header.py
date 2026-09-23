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
for s in (1, -1):
    x = s * (EP + 0.075)
    prof = [(-0.03, -0.045), (0.03, -0.045), (0.03, 0.045), (-0.03, 0.045)]
    sweep(bm, [(x, ARM_PIV.y, ARM_PIV.z), (x, REEL.y - 0.02, REEL.z + 0.06)], prof, mi=0, up=(0, 0, 1))
    cyl(bm, (x - 0.05, ARM_PIV.y, ARM_PIV.z), (x + 0.05, ARM_PIV.y, ARM_PIV.z), 0.04, 14, 1)
    # bearing housing at the reel shaft
    cyl(bm, (x - 0.05, REEL.y, REEL.z), (x + 0.05, REEL.y, REEL.z), 0.07, 18, 1)
    # truss brace down to the lift cylinder lug
    t_top = Vector((x, ARM_PIV.y + (REEL.y - ARM_PIV.y) * 0.55, ARM_PIV.z + (REEL.z - ARM_PIV.z) * 0.55))
    tube(bm, [t_top, t_top + Vector((0, 0.10, -0.22))], 0.022, 8, mi=0)
make_obj("reelArmsMesh", bm, [RED, DARK], C, TAG, origin=tuple(ARM_PIV), parent=arms, bevel=0.004)

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
make_obj("reelMesh", bm, [RED, GRAY, STEEL], C, TAG, origin=tuple(REEL), parent=reel_root)

# -------------------------------------------------------- header drives (L)


def pulley_x(bm, c, r, x0, x1, mi=0):
    xm = (x0 + x1) / 2
    w = x1 - x0
    revolve(bm, [(0.0, x0), (r * 0.30, x0), (r * 0.30, x0 + 0.005), (r * 0.85, x0 + 0.005), (r, x0),
                 (r * 0.88, xm), (r, x1), (r * 0.85, x1 - 0.005), (r * 0.30, x1 - 0.005), (r * 0.30, x1),
                 (0.0, x1)], 36, center=(0, c[0], c[1]), axis='X', mi=mi)
    cyl(bm, (x0 - 0.015, c[0], c[1]), (x1 + 0.015, c[0], c[1]), max(0.03, r * 0.2), 14, 1)


bm = bmesh.new()
XD0, XD1 = EP + 0.14, EP + 0.19
big = (-2.25, 0.88, 0.28)
pulley_x(bm, big[:2], big[2], XD0, XD1)
small_in = (-1.98, 1.02, 0.09)
pulley_x(bm, small_in[:2], small_in[2], XD0, XD1)
pts = belt_path([(y, z, r * 0.95) for (y, z, r) in (big, small_in)], 10)
sweep(bm, [(XD0 + 0.025, y, z) for (y, z) in pts[:-1]],
      [(-0.011, -0.006), (0.011, -0.006), (0.011, 0.006), (-0.011, 0.006)], closed=True, mi=2, up=(1, 0, 0))
# auger chain drive: sprocket on auger shaft + chain loop to the big pulley shaft
spr = (AUG.y, AUG.z, 0.13)
pulley_x(bm, spr[:2], spr[2], EP + 0.07, EP + 0.09, mi=1)
pulley_x(bm, (big[0], big[1]), 0.08, EP + 0.07, EP + 0.09, mi=1)
cpts = belt_path([(spr[0], spr[1], spr[2]), (big[0], big[1], 0.08)], 12)
chain_prof = [(-0.006, -0.012), (0.006, -0.012), (0.006, 0.012), (-0.006, 0.012)]
sweep(bm, [(EP + 0.08, y, z) for (y, z) in cpts[:-1]], chain_prof, closed=True, mi=1, up=(1, 0, 0))
# drive shield plate behind the pulleys
prism(bm, [(-2.58, 0.60), (-2.00, 0.66), (-1.90, 1.14), (-2.20, 1.22), (-2.56, 1.12)], 'X', EP + 0.105, EP + 0.115, 0)
make_obj("z050h_drives", bm, [RED, STEEL, RUB], C, TAG, parent=root)

print("header objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
