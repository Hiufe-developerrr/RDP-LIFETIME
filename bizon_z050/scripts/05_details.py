# 05 - unloading auger (transport position, left side), grain elevator, belt
# drives (right side), engine bay equipment, rear lights / SMV sign / straw
# curtain, hydraulic hoses and decals (fmż disc, BIZON plates).
TAG = "details"
purge_part(TAG)
C = coll("Z050_combine")
RED, CREAM, GRAY, DARK, STEEL = ("Z050_paint_red", "Z050_paint_cream", "Z050_paint_gray",
                                 "Z050_metal_dark", "Z050_steel")
RUB, CHROME, WHITE, BLACK = "Z050_rubber_black", "Z050_chrome", "Z050_decal_white", "Z050_decal_black"
LRED, ORANGE, SMV = "Z050_lamp_red", "Z050_lamp_orange", "Z050_smv_orange"

# ------------------------------------------------------ unloading auger (pipe)
PIV = Vector((TANK_HW + 0.13, TANK_Y0 + 0.20, 3.18))
bm = bmesh.new()
# vertical auger housing on the tank corner with the swivel gearbox on top
cyl(bm, (PIV.x, PIV.y, 2.22), (PIV.x, PIV.y, PIV.z - 0.10), 0.115, 24, 0)
for z in (2.30, 2.75):
    cyl(bm, (PIV.x, PIV.y, z), (PIV.x, PIV.y, z + 0.025), 0.135, 24, 0)
box(bm, (TANK_HW - 0.01, PIV.y - 0.10, 2.20), (PIV.x, PIV.y + 0.10, 2.40), 0)
box(bm, (TANK_HW - 0.01, PIV.y - 0.06, 2.92), (PIV.x - 0.08, PIV.y + 0.06, 3.02), 0)
make_obj("z050_unloadRiser", bm, [RED], C, TAG, bevel=0.006)

pipe_root = empty("pipe", tuple(PIV), C, TAG, size=0.4, kind='SINGLE_ARROW')
bm = bmesh.new()
end = Vector((PIV.x, 3.30, 2.90))
d = (end - PIV).normalized()
# swivel housing
revolve(bm, [(0.0, -0.10), (0.15, -0.10), (0.16, -0.08), (0.16, 0.06), (0.13, 0.10), (0.0, 0.10)], 28,
        center=PIV, axis='Z', mi=0)
cyl(bm, PIV + Vector((0, 0, 0.10)), PIV + Vector((0, 0, 0.16)), 0.05, 16, 2)
# elbow from the swivel into the tube
start = PIV + d * 0.12
cyl(bm, PIV, start, 0.13, 24, 0)
cyl(bm, start, end, 0.12, 28, 0, cap=True)
for t in (0.02, 0.36, 0.70, 0.985):
    c = start.lerp(end, t)
    cyl(bm, c - d * 0.02, c + d * 0.02, 0.138, 28, 0)
    bolt_ring(bm, c + d * 0.02, d, 0.13, 8, 0.008, 0.01, mi=2)
# spout: 90 deg elbow down + rubber sock
elb = [end + d * 0.02]
for k in range(1, 7):
    a = (pi / 2) * k / 6
    elb.append(end + d * (0.02 + 0.16 * sin(a)) + Vector((0, 0, -0.16 * (1 - cos(a)))))
sweep(bm, elb, circle2d(0.12, 24), mi=0)
tip = elb[-1]
cyl(bm, tip, tip + Vector((0, 0, -0.16)), 0.115, 24, 1, r1=0.10)
# gas-strut style support arm on the tube
tube(bm, [PIV + d * 0.9 + Vector((0, 0, -0.12)), PIV + d * 1.6 + Vector((0, 0, -0.15))], 0.018, 8, mi=2)
make_obj("pipeTube", bm, [RED, RUB, STEEL], C, TAG, origin=tuple(PIV), parent=pipe_root, bevel=0.005)

# transport cradle on the rear hood
bm = bmesh.new()
yc = 2.95
zc = PIV.z + (end.z - PIV.z) * ((yc - PIV.y) / (end.y - PIV.y)) - 0.125
tube(bm, [(HB, yc - 0.10, 2.52), (PIV.x, yc - 0.10, zc - 0.04)], 0.02, 8)
tube(bm, [(HB, yc + 0.10, 2.52), (PIV.x, yc + 0.10, zc - 0.04)], 0.02, 8)
revolve(bm, [(0.13, -0.08), (0.15, -0.08), (0.15, 0.08), (0.13, 0.08)], 12,
        center=(PIV.x, yc, zc + 0.125), axis='Y', mi=1, closed=True, phase=pi * 1.15, arc=pi * 0.7)
make_obj("z050_pipeCradle", bm, [DARK, RUB], C, TAG)

# -------------------------------------------------- grain elevator (right)
bm = bmesh.new()
ex0, ex1, ey0, ey1 = -1.055, -0.955, 0.98, 1.20
box(bm, (ex0, ey0, 0.80), (ex1, ey1, 3.05), 0)
revolve(bm, [(0.0, ex0), (0.11, ex0), (0.11, ex1), (0.0, ex1)], 20, center=(0, (ey0 + ey1) / 2, 3.05),
        axis='X', mi=0, phase=0.0, arc=pi)
box(bm, (ex0, ey0 - 0.01, 0.72), (ex1, ey1 + 0.01, 0.82), 0)
box(bm, (ex0 - 0.01, ey0 + 0.03, 1.10), (ex0, ey1 - 0.03, 1.45), 1)               # inspection door
for z in (1.12, 1.43):
    cyl(bm, (ex0 - 0.012, ey0 + 0.05, z), (ex0 - 0.012, ey1 - 0.05, z), 0.008, 6, 1)
make_obj("z050_grainElevator", bm, [RED, STEEL], C, TAG, bevel=0.006)

# ------------------------------------------------------ belt drives (right)


def pulley(bm, y, z, r, x, w=0.045, grooves=1, mi=0):
    g = w / (grooves * 2 + 1)
    xs = x - w / 2
    prof = [(0.0, xs), (r * 0.30, xs), (r * 0.30, xs + 0.004)]
    prof += [(r * 0.86, xs + 0.004), (r, xs)]
    for k in range(grooves):
        a = xs + g * (2 * k + 1)
        prof += [(r, a), (r * 0.9, a + g * 0.5), (r, a + g)]
    prof += [(r, x + w / 2), (r * 0.86, x + w / 2 - 0.004), (r * 0.30, x + w / 2 - 0.004),
             (r * 0.30, x + w / 2), (0.0, x + w / 2)]
    revolve(bm, prof, 36 if r > 0.15 else 24, center=(0, y, z), axis='X', mi=mi)
    cyl(bm, (x - w / 2 - 0.02, y, z), (x + w / 2 + 0.02, y, z), max(0.03, r * 0.18), 14, 1)


def belt(bm, pulleys, x, width=0.022, th=0.012):
    pts = belt_path([(y, z, r * 0.95) for (y, z, r) in pulleys], 10)
    path = [(x, y, z) for (y, z) in pts]
    prof = [(-th / 2, -width / 2), (th / 2, -width / 2), (th / 2, width / 2), (-th / 2, width / 2)]
    sweep(bm, path[:-1], prof, closed=True, mi=2, up=(1, 0, 0))


bm = bmesh.new()
XA, XB = -1.083, -1.028
E, Dr = (1.80, 2.72, 0.16), (-0.40, 1.42, 0.28)
pulley(bm, E[0], E[1], E[2], XA, grooves=2)
pulley(bm, Dr[0], Dr[1], Dr[2], XA, grooves=2)
belt(bm, [E, Dr], XA)
T = (0.62, 2.12, 0.07)
pulley(bm, T[0], T[1], T[2], XA)
tube(bm, [(XA + 0.03, T[0], T[1]), (-0.955, T[0] + 0.25, T[1] - 0.18)], 0.018, 8, mi=1)
D2, F = (-0.40, 1.42, 0.12), (0.62, 0.98, 0.14)
pulley(bm, D2[0], D2[1], D2[2], XB)
pulley(bm, F[0], F[1], F[2], XB)
belt(bm, [D2, F], XB)
E2, W = (1.80, 2.72, 0.10), (2.62, 2.22, 0.22)
pulley(bm, E2[0], E2[1], E2[2], XB)
pulley(bm, W[0], W[1], W[2], XB)
belt(bm, [E2, W], XB)
W2, S = (2.62, 2.22, 0.10), (3.30, 1.30, 0.16)
pulley(bm, W2[0], W2[1], W2[2], XA)
pulley(bm, S[0], S[1], S[2], XA)
belt(bm, [W2, S], XA)
# fan housing drum on the right side + belt guard over the engine pulley
revolve(bm, [(0.0, -HB), (0.30, -HB), (0.30, -HB - 0.03), (0.0, -HB - 0.03)], 32,
        center=(0, F[0], F[1]), axis='X', mi=0)
guard = [(E[0] + 0.26 * cos(a), E[1] + 0.26 * sin(a)) for a in [radians(t) for t in range(-60, 181, 15)]]
guard += [(E[0] - 0.26, E[1] - 0.12), (E[0] + 0.26 * cos(radians(-60)), E[1] - 0.20)]
prism(bm, guard, 'X', XA - 0.05, XA - 0.044, 0)
make_obj("z050_beltDrives", bm, [RED, STEEL, RUB], C, TAG, bevel=0.002)

# ------------------------------------------------------- engine bay kit
bm = bmesh.new()
# muffler + exhaust stack with rain flap
mz = TANK_TOP + 0.16
cyl(bm, (-0.60, ENG_Y0 + 0.20, mz), (-0.60, TANK_Y1 - 0.30, mz), 0.10, 20, 0)
for yy in (ENG_Y0 + 0.30, TANK_Y1 - 0.40):
    box(bm, (-0.64, yy - 0.02, TANK_TOP + 0.03), (-0.56, yy + 0.02, mz - 0.06), 1)
tube(bm, [(-0.60, TANK_Y1 - 0.30, mz), (-0.60, TANK_Y1 - 0.22, mz), (-0.60, TANK_Y1 - 0.22, mz + 0.10),
          (-0.60, TANK_Y1 - 0.22, 4.02)], 0.045, 14, mi=0, round_r=0.06)
cyl(bm, (-0.60, TANK_Y1 - 0.25, 4.02), (-0.60, TANK_Y1 - 0.19, 4.03), 0.05, 14, 1)
vs, _ = box_c(bm, (-0.60, TANK_Y1 - 0.23, 4.05), (0.11, 0.11, 0.006), 1)
rotate_verts(bm, vs, radians(-25), 'X', (-0.60, TANK_Y1 - 0.28, 4.03))
make_obj("z050_exhaust", bm, [DARK, STEEL], C, TAG)

bm = bmesh.new()
# air intake stack with a cyclone pre-cleaner bowl
ax, ay = 0.30, ENG_Y0 + 0.40
cyl(bm, (ax, ay, TANK_TOP + 0.03), (ax, ay, 3.74), 0.06, 16, 0)
revolve(bm, [(0.0, 3.72), (0.07, 3.72), (0.12, 3.78), (0.12, 3.90), (0.10, 3.94), (0.0, 3.95)], 24,
        center=(ax, ay, 0), axis='Z', mi=1)
cyl(bm, (ax, ay, 3.95), (ax, ay, 3.99), 0.03, 12, 0)
# radiator filler cap + oil bath filter side box
cyl(bm, (0.62, ENG_Y0 + 0.25, TANK_TOP + 0.03), (0.62, ENG_Y0 + 0.25, TANK_TOP + 0.10), 0.05, 16, 2)
cyl(bm, (0.62, ENG_Y0 + 0.25, TANK_TOP + 0.10), (0.62, ENG_Y0 + 0.25, TANK_TOP + 0.13), 0.065, 16, 2)
make_obj("z050_airIntake", bm, [DARK, "Z050_rubber_black", STEEL], C, TAG, bevel=0.003)

# hydraulic hoses (feeder lift, reel) along the body front
bm = bmesh.new()
for s in (1, -1):
    tube(bm, [(s * 0.25, -0.63, 1.90), (s * 0.30, -0.66, 1.30), (s * 0.40, -0.45, 0.95),
              (s * 0.42, -0.34, 0.80)], 0.013, 8, round_r=0.12)
tube(bm, [(0.55, -0.63, 1.95), (0.60, -0.70, 1.70), (0.63, -1.30, 1.25), (0.64, -1.62, 1.12)], 0.011, 8,
     round_r=0.18)
tube(bm, [(0.50, -0.63, 1.97), (0.56, -0.72, 1.72), (0.60, -1.32, 1.28), (0.60, -1.64, 1.14)], 0.011, 8,
     round_r=0.18)
make_obj("z050_hoses", bm, [RUB], C, TAG)

# ------------------------------------------------ rear: curtain, lights, SMV
bm = bmesh.new()
box(bm, (-0.82, REAR_Y, 1.52), (0.82, REAR_Y + 0.02, 2.10), 1)                    # straw outlet frame
for k in range(4):
    x0 = -0.80 + k * 0.40
    vs, _ = box(bm, (x0 + 0.005, REAR_Y + 0.03, 1.02), (x0 + 0.395, REAR_Y + 0.042, 1.52), 2)
    rotate_verts(bm, vs, radians(8), 'X', (0, REAR_Y + 0.03, 1.52))
box(bm, (-0.84, REAR_Y, 1.50), (0.84, REAR_Y + 0.05, 1.54), 0)
for s in (1, -1):
    # tail-light brackets + housings
    box(bm, (s * 0.80 - 0.015, REAR_Y, 1.62), (s * 0.80 + 0.015, REAR_Y + 0.14, 1.66), 1)
    box(bm, (s * 0.80 - 0.11, REAR_Y + 0.10, 1.66), (s * 0.80 + 0.11, REAR_Y + 0.16, 1.76), 1)
# SMV triangle bracket
box(bm, (-0.02, REAR_Y, 2.02), (0.02, REAR_Y + 0.06, 2.34), 1)
make_obj("z050_rearKit", bm, [RED, DARK, RUB], C, TAG, bevel=0.003)

bm = bmesh.new()
for s in (1, -1):
    box(bm, (s * 0.80 - 0.105, REAR_Y + 0.16, 1.665), (s * 0.80 - 0.005, REAR_Y + 0.17, 1.755), 0)
    box(bm, (s * 0.80 + 0.005, REAR_Y + 0.16, 1.665), (s * 0.80 + 0.105, REAR_Y + 0.17, 1.755), 1)
    cyl(bm, (s * 0.88, REAR_Y, 2.28), (s * 0.88, REAR_Y + 0.012, 2.28), 0.04, 16, 0)
make_obj("z050_rearLights", bm, [LRED, ORANGE], C, TAG)

bm = bmesh.new()
tc = Vector((0.0, REAR_Y + 0.065, 2.20))
tri = [(-0.20, -0.115), (0.20, -0.115), (0.0, 0.23)]
tri_in = [(-0.13, -0.075), (0.13, -0.075), (0.0, 0.15)]
plate(bm, [(tc.x + u, tc.y, tc.z + v) for (u, v) in tri], 0.01, (0, 1, 0), mi=0)
plate(bm, [(tc.x + u, tc.y + 0.01, tc.z + v) for (u, v) in tri_in], 0.003, (0, 1, 0), mi=1)
make_obj("z050_smvSign", bm, [LRED, SMV], C, TAG)

# ---------------------------------------------------------------- decals
bm = bmesh.new()
# fmż disc on the left side of the grain tank
lc = Vector((TANK_HW, 0.40, 2.74))
revolve(bm, [(0.0, 0.0), (0.165, 0.0), (0.165, 0.004), (0.0, 0.004)], 40, center=lc, axis='X', mi=0)
revolve(bm, [(0.140, 0.004), (0.155, 0.004), (0.155, 0.007), (0.140, 0.007)], 40, center=lc, axis='X',
        mi=1, closed=True)
me = text_mesh("fmż", 0.16, 0.0015)
mesh_to_bm(bm, me, Matrix.Translation(lc + Vector((0.0055, 0, -0.01))) @ FACE_LEFT, mi=1)
D.meshes.remove(me)
# BIZON plates on both rear sides + small badge on the tank
for s, face in ((1, FACE_LEFT), (-1, FACE_RIGHT)):
    pc = Vector((s * (HB + 0.028), 4.10, 2.30))
    pr = rrect2d(0.86, 0.30, 0.06, 4)
    pts = []
    for (u, v) in pr:
        pts.append(pc + (face @ Vector((u, v, 0.0))))
    plate(bm, pts, 0.004, (s, 0, 0), mi=0)
    me = text_mesh("BIZON", 0.30, 0.002)
    mesh_to_bm(bm, me, Matrix.Translation(pc + Vector((s * 0.006, 0, -0.005))) @ face, mi=2)
    D.meshes.remove(me)
me = text_mesh("super Z050", 0.085, 0.0015)
mesh_to_bm(bm, me, Matrix.Translation(Vector((TANK_HW + 0.0015, 0.40, 2.49))) @ FACE_LEFT, mi=1)
D.meshes.remove(me)
make_obj("z050_decals", bm, [WHITE, BLACK, RED], C, TAG)

print("details objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
