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
for z in (2.30, 2.75):
    bolt_ring(bm, (PIV.x, PIV.y, z + 0.025), (0, 0, 1), 0.124, 8, 0.0075, 0.008, mi=2)
# bevel gearbox under the riser, input shaft, clutch lever with a rod to the platform
box_c(bm, (PIV.x, PIV.y, 2.155), (0.20, 0.20, 0.13), 1)
fasteners(bm, (PIV.x - 0.09, PIV.y - 0.10, 2.22), (PIV.x + 0.09, PIV.y - 0.10, 2.22), (0, -1, 0), 0.06, 'bolt', 2,
          af=0.013, h=0.005, washer=False)
cyl(bm, (PIV.x, PIV.y - 0.10, 2.14), (PIV.x, PIV.y - 0.24, 2.14), 0.028, 12, 2)
flange_bearing(bm, (PIV.x, PIV.y - 0.10, 2.14), (0, -1, 0), 0.05, 1, 2)
tube(bm, [(PIV.x + 0.10, PIV.y + 0.02, 2.16), (PIV.x + 0.16, PIV.y + 0.02, 2.30), (PIV.x + 0.14, -0.62, 2.52)],
     0.009, 8, mi=2, round_r=0.06)
sphere(bm, (PIV.x + 0.14, -0.625, 2.53), 0.022, 10, 5, 3)
make_obj("z050_unloadRiser", bm, [RED, DARK, "Z050_zinc", "Z050_knob_black"], C, TAG, bevel=0.006)

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
fasteners(bm, (ex0, ey0 + 0.02, 0.84), (ex0, ey0 + 0.02, 2.98), (-1, 0, 0), 0.16, 'rivet', 0)
fasteners(bm, (ex0, ey1 - 0.02, 0.84), (ex0, ey1 - 0.02, 2.98), (-1, 0, 0), 0.16, 'rivet', 0)
flange_bearing(bm, (ex0, (ey0 + ey1) / 2, 3.05), (-1, 0, 0), 0.045, 2, 1)
make_obj("z050_grainElevator", bm, [RED, STEEL, "Z050_metal_dark"], C, TAG, bevel=0.006)

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
for yy in (ENG_Y0 + 0.45, TANK_Y1 - 0.55):
    revolve(bm, [(0.10, yy - 0.012), (0.106, yy - 0.012), (0.106, yy + 0.012), (0.10, yy + 0.012)], 20,
            center=(-0.60, 0, mz), axis='Y', mi=1, closed=True)
revolve(bm, [(0.045, 3.72), (0.051, 3.72), (0.051, 3.745), (0.045, 3.745)], 16, center=(-0.60, TANK_Y1 - 0.22, 0),
        axis='Z', mi=1, closed=True)
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

lb = bmesh.new()
lz = bmesh.new()
for s in (1, -1):
    x = s * 0.80
    box(lb, (x - 0.12, REAR_Y + 0.155, 1.655), (x + 0.12, REAR_Y + 0.215, 1.765), 0)            # housing
    box(lb, (x - 0.125, REAR_Y + 0.212, 1.65), (x + 0.125, REAR_Y + 0.222, 1.77), 1)           # chrome rim
    box(lz, (x - 0.11, REAR_Y + 0.222, 1.665), (x - 0.005, REAR_Y + 0.232, 1.755), 0)          # tail / stop
    box(lz, (x + 0.005, REAR_Y + 0.222, 1.665), (x + 0.11, REAR_Y + 0.232, 1.755), 1)          # indicator
    revolve_v(lb, [(0.038, 0.0), (0.045, 0.0), (0.045, 0.01)], 18, (x, REAR_Y + 0.05, 1.58), (0, 1, 0), 0)
    revolve_v(lz, [(0.0, 0.012), (0.039, 0.009), (0.039, 0.0)], 18, (x, REAR_Y + 0.05, 1.58), (0, 1, 0), 0)
    nut(lb, (x, REAR_Y + 0.215, 1.71), (0, 1, 0), af=0.01, h=0.004, mi=1, washer=False)
make_obj("z050_rearLampBodies", lb, ["Z050_plastic_black", "Z050_chrome"], C, TAG)
ob = make_obj("z050_rearLights", lz, [LRED, ORANGE], C, TAG)
ob["grp"] = "lights"

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
for (x, y, z, face, s_) in ((-(HB + 0.029), 2.20, 2.55, FACE_RIGHT, -1), (-(HB + 0.029), 3.95, 1.95, FACE_RIGHT, -1),
                           (HB + 0.029, 3.95, 1.95, FACE_LEFT, 1)):
    c = Vector((x, y, z))
    plate(bm, [c + face @ Vector((u, v, 0)) for (u, v) in ((-0.05, -0.07), (0.05, -0.07), (0.05, 0.07), (-0.05, 0.07))],
          0.002, (s_, 0, 0), mi=3)
    plate(bm, [c + Vector((s_ * 0.002, 0, 0)) + face @ Vector((u, v, 0)) for (u, v) in ((-0.036, -0.02), (0.036, -0.02),
                                                                                      (0.0, 0.045))],
          0.001, (s_, 0, 0), mi=1)
make_obj("z050_decals", bm, [WHITE, BLACK, RED, "Z050_decal_yellow"], C, TAG)

print("details objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
