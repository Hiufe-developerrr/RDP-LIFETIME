# 05b - drive train outside the body: belts on cast pulleys, variators for the
# drum and travel drive, roller chains on toothed sprockets, spring loaded
# tensioners, flange bearings with grease nipples, fan volutes, cross augers,
# frame rails, feeder house drive and the header drive belt.
TAG = "drives"
purge_part(TAG)
C = coll("Z050_combine")
RED, DARK, STEEL, ZINC, BELT, CHAIN, CREAM = ("Z050_paint_red", "Z050_metal_dark", "Z050_steel", "Z050_zinc",
                                              "Z050_belt", "Z050_chain", "Z050_paint_cream")
MATS = [RED, DARK, STEEL, ZINC, BELT, CHAIN]


def detail(name, bm, mats=MATS, attach=None, bevel=None):
    ob = make_obj(name, bm, mats, C, TAG, bevel=bevel)
    ob["grp"] = "detail"
    if attach:
        ob["attach"] = attach
    return ob


def vbelt(bm, pulleys, x, width=0.013, th=0.011, mi=4):
    pts = belt_path([(y, z, r * 0.93) for (y, z, r) in pulleys], 12)
    prof = [(-th / 2, -width / 2), (th / 2, -width / 2), (th / 2, width / 2), (-th / 2, width / 2)]
    sweep(bm, [(x, y, z) for (y, z) in pts[:-1]], prof, closed=True, mi=mi, up=(1, 0, 0))


def shaft(bm, y, z, x0, x1, r=0.022, mi=2):
    cyl(bm, (x0, y, z), (x1, y, z), r, 12, mi)


def tensioner(bm, pivot, idler, anchor, x, r_idler, side):
    """Idler pulley in the belt plane on an arm (pivot outboard), spring to an anchor."""
    xa = x + side * 0.032
    pv, idl, an = Vector((xa, pivot[0], pivot[1])), Vector((xa, idler[0], idler[1])), Vector((xa, anchor[0], anchor[1]))
    d = idl - pv
    vs, _ = box_c(bm, (pv + idl) / 2, (0.01, d.length + 0.06, 0.045), 0)
    rotate_verts(bm, vs, atan2(d.z, d.y), 'X', (pv + idl) / 2)
    cyl(bm, (x - side * 0.01, pivot[0], pivot[1]), (xa + side * 0.012, pivot[0], pivot[1]), 0.022, 12, 1)
    nut(bm, (xa + side * 0.006, pivot[0], pivot[1]), (side, 0, 0), af=0.022, h=0.01, mi=3)
    spoked_pulley(bm, idler, r_idler, x, 0.04, 1, 0, 2, 3)
    cyl(bm, (x, idler[0], idler[1]), (xa + side * 0.012, idler[0], idler[1]), 0.016, 10, 3)
    mid = pv.lerp(idl, 0.6)
    spring(bm, mid + Vector((side * 0.012, 0, 0)), an + Vector((side * 0.012, 0, 0)), 0.013, 0.0028, 11, mi=5)
    box_c(bm, an, (0.02, 0.04, 0.04), 1)
    cyl(bm, (x - side * 0.02, anchor[0], anchor[1]), (xa, anchor[0], anchor[1]), 0.012, 8, 1)


# =============================================================== right side
R = bmesh.new()
XB, XA, XV, XF, XCH = -1.125, -1.18, -1.05, -0.99, -1.075
E = (1.85, 2.72)
Cs, Dr, F = CSHAFT, DRUM, FAN
W, S = (2.62, 2.22), (3.30, 1.30)
# engine crank pulleys (main + walker drive) with a solid web
spoked_pulley(R, E, 0.15, XB, 0.05, 2, 5, 0, 2)
spoked_pulley(R, E, 0.10, XA, 0.04, 1, 0, 0, 2)
shaft(R, E[0], E[1], -0.975, XA - 0.03)
# countershaft: main driven pulley, drum variator (driving half), fan pulley
spoked_pulley(R, Cs, 0.25, XB, 0.05, 2, 6, 0, 2)
variator(R, Cs, 0.19, XV, 0.07, 0, 2, side=1, cup=0.03)
spoked_pulley(R, Cs, 0.085, XF, 0.035, 1, 0, 0, 2)
shaft(R, Cs[0], Cs[1], -0.95, XB - 0.04)
# threshing drum variator (driven, spring cup outboard)
variator(R, Dr, 0.30, XV, 0.075, 0, 2, side=-1)
shaft(R, Dr[0], Dr[1], -0.95, XV - 0.16)
# cleaning fan pulley, walker crank pulley pair, sieve eccentric
spoked_pulley(R, F, 0.16, XF, 0.035, 1, 5, 0, 2)
shaft(R, F[0], F[1], -0.965, XCH - 0.02)
spoked_pulley(R, W, 0.22, XA, 0.04, 1, 5, 0, 2)
spoked_pulley(R, W, 0.10, XB, 0.04, 1, 0, 0, 2)
shaft(R, W[0], W[1], -0.95, XA - 0.03)
spoked_pulley(R, S, 0.17, XB, 0.04, 1, 5, 0, 2)
shaft(R, S[0], S[1], -0.95, XB - 0.06)
cyl(R, (XB - 0.03, S[0] + 0.05, S[1]), (XB - 0.05, S[0] + 0.05, S[1]), 0.07, 18, 1)          # eccentric disc
tube(R, [(XB - 0.06, S[0] + 0.05, S[1]), (XB - 0.06, 2.92, 1.28), (-0.96, 2.86, 1.28)], 0.014, 8, mi=1,
     round_r=0.05)                                                                          # pitman to the sieves
# belts: main (two V-belts), variator belt, walker, sieve, fan
for dx in (-0.01, 0.01):
    vbelt(R, [(E[0], E[1], 0.15), (1.30, 2.10, 0.065), (Cs[0], Cs[1], 0.25)], XB + dx, 0.011, 0.01)
vbelt(R, [(Cs[0], Cs[1], 0.19), (Dr[0], Dr[1], 0.30)], XV, 0.03, 0.013)
vbelt(R, [(E[0], E[1], 0.10), (2.22, 2.63, 0.055), (W[0], W[1], 0.22)], XA)
vbelt(R, [(W[0], W[1], 0.10), (S[0], S[1], 0.17)], XB)
vbelt(R, [(Cs[0], Cs[1], 0.085), (F[0], F[1], 0.16)], XF)
tensioner(R, (1.52, 1.96), (1.30, 2.10), (1.62, 2.30), XB, 0.065, -1)
tensioner(R, (2.48, 2.78), (2.22, 2.63), (2.52, 2.46), XA, 0.055, -1)
# roller chains: fan -> clean grain auger (elevator), sieve -> tailings auger
r1 = sprocket(R, F, XCH - 0.004, XCH + 0.004, 14, mi=5, hub_mi=2)
r2 = sprocket(R, GRAIN_AUGER, XCH - 0.004, XCH + 0.004, 22, mi=5, hub_mi=2)
roller_chain(R, belt_path([(F[0], F[1], r1), (GRAIN_AUGER[0], GRAIN_AUGER[1], r2)], 14), XCH, mi=5)
shaft(R, GRAIN_AUGER[0], GRAIN_AUGER[1], -0.95, XCH - 0.02)
r3 = sprocket(R, S, XCH - 0.004, XCH + 0.004, 12, mi=5, hub_mi=2)
r4 = sprocket(R, TAIL_AUGER, XCH - 0.004, XCH + 0.004, 20, mi=5, hub_mi=2)
roller_chain(R, belt_path([(S[0], S[1], r3), (TAIL_AUGER[0], TAIL_AUGER[1], r4)], 14), XCH, mi=5)
shaft(R, TAIL_AUGER[0], TAIL_AUGER[1], -0.95, XCH - 0.02)
# flange bearings with grease nipples on the body side
for (y, z) in (Cs, Dr, W, S, GRAIN_AUGER, TAIL_AUGER):
    flange_bearing(R, (-0.95, y, z), (-1, 0, 0), 0.06, 1, 3)
flange_bearing(R, (-0.975, E[0], E[1]), (-1, 0, 0), 0.07, 1, 3, bolts=4)
# belt guard over the engine pulleys (bent sheet + side plate)
arc_pts = [(E[0] + 0.21 * cos(radians(a)), E[1] + 0.21 * sin(radians(a))) for a in range(-15, 196, 15)]
prof = [(-0.003, -0.07), (0.003, -0.07), (0.003, 0.07), (-0.003, 0.07)]
sweep(R, [(XB - 0.025, y, z) for (y, z) in arc_pts], [(v, u) for (u, v) in prof], mi=0, up=(1, 0, 0))
prism(R, arc_pts + [(E[0] - 0.05, E[1] - 0.05), (E[0] + 0.05, E[1] - 0.05)], 'X', XA - 0.035, XA - 0.03, 0)
for a in (-10, 90, 185):
    rivet(R, (XA - 0.035, E[0] + 0.19 * cos(radians(a)), E[1] + 0.19 * sin(radians(a))), (-1, 0, 0), mi=0)
# cleaning fan volute + inlet grille (right)
vol = [(F[0] + (0.24 + 0.1 * t) * cos(radians(90 + 300 * t)), F[1] + (0.24 + 0.1 * t) * sin(radians(90 + 300 * t)))
       for t in [k / 24 for k in range(25)]]
vol += [(F[0] + 0.36, F[1] + 0.10), (F[0] + 0.30, F[1] + 0.24)]
prism(R, vol, 'X', -0.972, -0.95, 0)
revolve(R, [(0.15, -0.99), (0.17, -0.99), (0.17, -0.972), (0.15, -0.972)], 32, center=(0, F[0], F[1]), axis='X', mi=0,
        closed=True)
for k in range(10):
    vs, _ = box_c(R, (-0.98, 0.09, 0), (0.008, 0.13, 0.012), 1)
    bmesh.ops.rotate(R, cent=Vector((0, 0, 0)), matrix=Matrix.Rotation(2 * pi * k / 10, 3, 'X'), verts=vs)
    bmesh.ops.translate(R, verts=vs, vec=Vector((0, F[0], F[1])))
fasteners(R, (-0.972, F[0] - 0.22, F[1] + 0.12), (-0.972, F[0] + 0.22, F[1] + 0.12), (-1, 0, 0), 0.11, 'bolt', 3,
          af=0.013, h=0.005)
detail("z050_drivesRight", R)

# =============================================================== left side
L = bmesh.new()
XL, XLC = 1.05, 1.00
V4 = (1.32, 1.22)
LOW = (0.50, 0.95)
variator(L, Cs, 0.19, XL, 0.07, 0, 2, side=1)                 # travel variator, driving half
variator(L, V4, 0.22, XL, 0.075, 0, 2, side=1)                 # driven half
vbelt(L, [(Cs[0], Cs[1], 0.19), (V4[0], V4[1], 0.22)], XL, 0.03, 0.013)
shaft(L, Cs[0], Cs[1], 0.95, XL + 0.13)
shaft(L, V4[0], V4[1], 0.95, XL + 0.13)
r5 = sprocket(L, V4, XLC - 0.004, XLC + 0.004, 13, pitch=0.0254, mi=5, hub_mi=2)
r6 = sprocket(L, LOW, XLC - 0.004, XLC + 0.004, 25, pitch=0.0254, mi=5, hub_mi=2)
roller_chain(L, belt_path([(V4[0], V4[1], r5), (LOW[0], LOW[1], r6)], 14), XLC, pitch=0.0254, width=0.015, mi=5)
shaft(L, LOW[0], LOW[1], 0.95, XLC + 0.02)
# hydraulic adjuster cylinder of the travel variator
cyl(L, (XL + 0.13, V4[0] + 0.06, V4[1] + 0.30), (XL + 0.13, V4[0] + 0.02, V4[1] + 0.06), 0.028, 12, 1)
cyl(L, (XL + 0.13, V4[0] + 0.02, V4[1] + 0.06), (XL + 0.10, V4[0], V4[1]), 0.012, 8, 2)
box_c(L, (0.97, V4[0] + 0.06, V4[1] + 0.33), (0.05, 0.05, 0.05), 1)
tube(L, [(0.99, V4[0] + 0.06, V4[1] + 0.33), (XL + 0.13, V4[0] + 0.06, V4[1] + 0.32)], 0.012, 8, mi=1)
# feeder house drive chain at the front-left corner (drum shaft -> feeder top shaft)
FP = (FEEDER_PIVOT[1], FEEDER_PIVOT[2])
r7 = sprocket(L, Dr, 0.99 - 0.004, 0.99 + 0.004, 21, pitch=0.0254, mi=5, hub_mi=2)
r8 = sprocket(L, FP, 0.99 - 0.004, 0.99 + 0.004, 27, pitch=0.0254, mi=5, hub_mi=2)
roller_chain(L, belt_path([(Dr[0], Dr[1], r7), (FP[0], FP[1], r8)], 14), 0.99, pitch=0.0254, width=0.015, mi=5)
shaft(L, Dr[0], Dr[1], 0.95, 1.02)
shaft(L, FP[0], FP[1], 0.60, 1.02, 0.028)
spoked_pulley(L, Dr, 0.11, 1.045, 0.035, 1, 0, 0, 2)          # slip clutch disc
for k in range(6):
    a = 2 * pi * k / 6
    nut(L, (1.0625, Dr[0] + 0.07 * cos(a), Dr[1] + 0.07 * sin(a)), (1, 0, 0), af=0.013, h=0.006, mi=3, stud=True)
spring(L, (1.07, Dr[0], Dr[1]), (1.12, Dr[0], Dr[1]), 0.035, 0.005, 5, mi=2, hooks=False)
# bearings (left)
for (y, z) in (Cs, Dr, V4, LOW, GRAIN_AUGER, TAIL_AUGER):
    flange_bearing(L, (0.95, y, z), (1, 0, 0), 0.06, 1, 3)
flange_bearing(L, (0.96, FP[0] + 0.0, FP[1]), (1, 0, 0), 0.065, 1, 3, bolts=4)
# cleaning fan inlet (left)
revolve(L, [(0.0, 0.95), (0.26, 0.95), (0.26, 0.968), (0.0, 0.968)], 32, center=(0, F[0], F[1]), axis='X', mi=0)
revolve(L, [(0.15, 0.968), (0.17, 0.968), (0.17, 0.985), (0.15, 0.985)], 32, center=(0, F[0], F[1]), axis='X', mi=0,
        closed=True)
for k in range(10):
    vs, _ = box_c(L, (0.976, 0.09, 0), (0.008, 0.13, 0.012), 1)
    bmesh.ops.rotate(L, cent=Vector((0, 0, 0)), matrix=Matrix.Rotation(2 * pi * k / 10, 3, 'X'), verts=vs)
    bmesh.ops.translate(L, verts=vs, vec=Vector((0, F[0], F[1])))
cyl(L, (0.968, F[0], F[1]), (1.02, F[0], F[1]), 0.03, 12, 2)
# sieve adjustment lever with a notched quadrant (left rear)
qc = (4.25, 1.30)
notch = []
for k in range(13):
    a = radians(60 + 5 * k)
    rr = 0.16 if k % 2 == 0 else 0.15
    notch.append((qc[0] + rr * cos(a), qc[1] + rr * sin(a)))
prism(L, [qc] + notch, 'X', 0.975, 0.981, 1)
tube(L, [(0.99, qc[0], qc[1]), (0.99, qc[0] + 0.05, qc[1] + 0.22)], 0.009, 8, mi=2)
sphere(L, (0.99, qc[0] + 0.052, qc[1] + 0.235), 0.02, 10, 5, 1)
nut(L, (0.981, qc[0], qc[1]), (1, 0, 0), af=0.019, h=0.009, mi=3)
detail("z050_drivesLeft", L)

# =============================================================== under body
U = bmesh.new()
bottom = [(-0.50, 1.00), (0.28, 0.98), (0.45, 0.66), (2.55, 0.66), (3.05, 1.02), (4.60, 1.15), (4.86, 1.45)]
prof = [(-0.05, -0.04), (0.05, -0.04), (0.05, 0.04), (-0.05, 0.04)]
for s in (1, -1):
    path = [Vector((s * 0.87, y, z - 0.055)) for (y, z) in bottom]
    for p, q in zip(path, path[1:]):                      # straight welded segments (compact UV islands)
        d = (q - p).normalized()
        sweep(U, [p - d * 0.035, q + d * 0.035], prof, mi=1, up=(1, 0, 0))
for y in (0.60, 1.60, 2.40):
    box(U, (-0.87, y - 0.04, 0.56), (0.87, y + 0.04, 0.62), 1)
cyl(U, (-0.95, GRAIN_AUGER[0], GRAIN_AUGER[1]), (0.95, GRAIN_AUGER[0], GRAIN_AUGER[1]), 0.13, 28, 0)
cyl(U, (-0.95, TAIL_AUGER[0], TAIL_AUGER[1]), (0.95, TAIL_AUGER[0], TAIL_AUGER[1]), 0.10, 24, 0)
for x in (-0.6, -0.2, 0.2, 0.6):
    for (y, z, r) in ((GRAIN_AUGER[0], GRAIN_AUGER[1], 0.13), (TAIL_AUGER[0], TAIL_AUGER[1], 0.10)):
        revolve(U, [(r, x - 0.012), (r + 0.012, x - 0.012), (r + 0.012, x + 0.012), (r, x + 0.012)], 24,
                center=(0, y, z), axis='X', mi=0, closed=True, phase=pi, arc=pi)
for y in (1.05, 1.95):                                                     # grain pan drain covers
    box(U, (-0.40, y - 0.12, 0.645), (0.40, y + 0.12, 0.66), 0)
    for x in (-0.36, 0.36):
        nut(U, (x, y, 0.645), (0, 0, -1), af=0.013, h=0.005, mi=3, washer=False)
detail("z050_underbody", U)

# ================================================= feeder house (moves)
FH = bmesh.new()
for s in (1, -1):
    x = s * 0.625
    flange_bearing(FH, (x, -1.66, 0.62), (s, 0, 0), 0.055, 1, 3)
    box(FH, (min(x, x + s * 0.012), -1.60, 0.52), (max(x, x + s * 0.012), -1.30, 0.72), 1)       # slotted plate
    cyl(FH, (x + s * 0.03, -1.62, 0.66), (x + s * 0.03, -1.20, 0.80), 0.009, 8, 3)                # tension rod
    for t in (0.55, 0.85):
        p = Vector((x + s * 0.03, -1.62, 0.66)).lerp(Vector((x + s * 0.03, -1.20, 0.80)), t)
        cyl(FH, p - Vector((0, 0.008, 0.003)), p + Vector((0, 0.008, 0.003)), 0.013, 6, 3)
# top inspection door
door = [(-0.40, -1.00, 1.573), (0.40, -1.00, 1.573), (0.40, -1.38, 1.278), (-0.40, -1.38, 1.278)]
n_top = Vector((0, -0.84, 1.08)).normalized()
plate(FH, [Vector(p) + n_top * 0.003 for p in door], 0.004, n_top, mi=0)
d_c = Vector((0, -1.19, 1.4255))
for p in door:
    nut(FH, Vector(p) + n_top * 0.007 + (d_c - Vector(p)) * 0.08, n_top, af=0.014, h=0.006, mi=3)
tube(FH, [d_c + n_top * 0.007 + Vector((-0.08, 0.03, -0.03)), d_c + n_top * 0.05 + Vector((-0.08, 0.03, -0.03)),
          d_c + n_top * 0.05 + Vector((0.08, 0.03, -0.03)), d_c + n_top * 0.007 + Vector((0.08, 0.03, -0.03))],
     0.008, 8, mi=2, round_r=0.02)
# header drive: pulley on the top shaft (left, outboard of the feeder side) + belt to the header
HP_IN = (-1.72, 1.10)
spoked_pulley(FH, FP, 0.12, 0.72, 0.035, 1, 5, 0, 2)
vbelt(FH, [(FP[0], FP[1], 0.12), (HP_IN[0], HP_IN[1], 0.14)], 0.72)
detail("z050_feederDetails", FH, attach="feederHouse")

print("drives objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
