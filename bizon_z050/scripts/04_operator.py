# 04 - open operator station after the Z050 Super cockpit photos: railings
# with bolted feet, sun canopy (cream top, grey underside), round headlights
# on the red front wall, dash box with gauges on the steering column, lever
# console with gear gate, sprung vinyl seat, pedals, fuel tank, toolbox,
# plank, extinguisher, mirrors, work lights, beacon, anti-slip ladder.
TAG = "operator"
purge_part(TAG)
C = coll("Z050_combine")
RED, CREAM, GRAY, DARK, STEEL = ("Z050_paint_red", "Z050_paint_cream", "Z050_paint_gray",
                                 "Z050_metal_dark", "Z050_steel")
RUB, CHROME, GLASS, ORANGE, LRED = ("Z050_rubber_black", "Z050_chrome", "Z050_glass",
                                    "Z050_lamp_orange", "Z050_lamp_red")
ZINC, KB, KR, VINYL, WOOD = "Z050_zinc", "Z050_knob_black", "Z050_knob_red", "Z050_vinyl", "Z050_wood"
GAUGE, WHITE, BLACK, CLEAR = "Z050_gauge", "Z050_decal_white", "Z050_decal_black", "Z050_lamp_clear"
FZ = PLAT_Z
RAIL_R = 0.0165


def lights_obj(name, bm, mats):
    ob = make_obj(name, bm, mats, C, TAG)
    ob["grp"] = "lights"
    return ob


lens = bmesh.new()      # every lamp lens / gauge glass of this script

# ------------------------------------------------------------------ railings
bm = bmesh.new()
top, mid = FZ + 0.92, FZ + 0.50
xl, xr, yf, yr = PLAT_HW - 0.03, -PLAT_HW + 0.03, PLAT_Y0 + 0.05, PLAT_Y1 - 0.05
tube(bm, [(xl, -1.00, FZ), (xl, -1.00, top), (xl, yf, top), (xr, yf, top), (xr, yr, top),
          (xr, yr, TANK_TOP - 0.55)], RAIL_R, 12, round_r=0.08)
tube(bm, [(xl, -1.00, mid), (xl, yf, mid), (xr, yf, mid), (xr, yr, mid)], RAIL_R, 12, round_r=0.08)
for (x, y) in ((xl, yf), (xr, yf), (xr, -1.0), (xl, -1.0)):
    tube(bm, [(x, y, FZ + 0.01), (x, y, top)], RAIL_R, 12)
for (x, y) in ((xl, yf), (xr, yf), (xr, -1.0), (xl, -1.0), (xr, yr)):
    box_c(bm, (x, y, FZ + 0.004), (0.07, 0.07, 0.008), 0)                      # welded foot plate
    for dx in (-0.024, 0.024):
        nut(bm, (x + dx, y + 0.024, FZ + 0.008), (0, 0, 1), af=0.013, h=0.006, mi=1, washer=False)
box(bm, (xr - 0.05, yr - 0.02, TANK_TOP - 0.62), (xr + 0.05, TANK_Y0, TANK_TOP - 0.50), 0)
make_obj("z050_railings", bm, [RED, ZINC], C, TAG)

# ---------------------------------------------------------------- sun canopy
bm = bmesh.new()
cz = CANOPY_Z - 0.06
posts_f = [(0.80, PLAT_Y0 + 0.08), (-0.80, PLAT_Y0 + 0.08)]
posts_r = [(0.74, TANK_Y0 - 0.05), (-0.74, TANK_Y0 - 0.05)]
for (x, y) in posts_f:
    tube(bm, [(x, y, FZ), (x, y, cz)], 0.021, 12, mi=1)
    box_c(bm, (x, y, FZ + 0.005), (0.08, 0.08, 0.01), 1)
    for dy in (-0.028, 0.028):
        nut(bm, (x + 0.028, y + dy, FZ + 0.01), (0, 0, 1), af=0.013, h=0.006, mi=2, washer=False)
for (x, y) in posts_r:
    tube(bm, [(x, y, TANK_TOP - 0.64), (x, y, cz)], 0.021, 12, mi=1)
    box(bm, (x - 0.05, TANK_Y0 - 0.075, TANK_TOP - 0.70), (x + 0.05, TANK_Y0, TANK_TOP - 0.55), 1)
    for dz in (-0.12, -0.04):
        nut(bm, (x + 0.03, TANK_Y0 - 0.075, TANK_TOP + dz - 0.55), (0, -1, 0), af=0.013, h=0.006, mi=2)
for (x, y) in posts_f + posts_r:                                                # top gussets
    box_c(bm, (x, y, cz - 0.03), (0.06, 0.06, 0.05), 1)
tube(bm, [(0.80, PLAT_Y0 + 0.08, cz), (0.80, TANK_Y0 - 0.05, cz), (-0.80, TANK_Y0 - 0.05, cz),
          (-0.80, PLAT_Y0 + 0.08, cz)], 0.018, 10, mi=1, closed=True)
tube(bm, [(0.80, -1.02, cz), (-0.80, -1.02, cz)], 0.015, 8, mi=1)
make_obj("z050_canopyFrame", bm, [RED, GRAY, ZINC], C, TAG)

bm = bmesh.new()
y0, y1, hw, zt = PLAT_Y0 - 0.12, TANK_Y0 + 0.14, 0.88, CANOPY_Z
yc = (y0 + y1) / 2
outline = rrect2d(2 * hw, y1 - y0, 0.07, 3, 0.0, yc)
rings = []
for (k, zz) in ((1.0, zt - 0.004), (0.97, zt + 0.004), (0.75, zt + 0.02), (0.45, zt + 0.03)):
    rings.append([(x * k, yc + (y - yc) * k, zz) for (x, y) in outline])
R_, _ = loft(bm, rings, cap=False, mi=0)
f = bm.faces.new(R_[-1])
f.material_index = 0
sweep(bm, [(x, y, zt - 0.008) for (x, y) in outline], circle2d(0.011, 8), closed=True, mi=0)   # rolled edge
inner = rrect2d(2 * hw - 0.05, y1 - y0 - 0.05, 0.05, 3, 0.0, yc)
plate(bm, [(x, y, zt - 0.036) for (x, y) in inner], 0.006, (0, 0, 1), mi=1)                    # grey underside
for (x, y) in outline[::3]:
    rivet(bm, (x * 0.985, yc + (y - yc) * 0.985, zt - 0.037), (0, 0, -1), r=0.006, mi=1)
for k in range(4):
    yy = y0 + 0.28 + k * (y1 - y0 - 0.56) / 3
    prism(bm, [(yy - 0.025, zt - 0.036), (yy + 0.025, zt - 0.036), (yy + 0.015, zt - 0.062),
               (yy - 0.015, zt - 0.062)], 'X', -hw + 0.05, hw - 0.05, 1)
make_obj("z050_canopyRoof", bm, [CREAM, GRAY], C, TAG, bevel=0.003)

# ------------------------------------------- work lights, beacon, mirrors
bm = bmesh.new()
TILT = radians(-14)
for (x, y, z) in WORKLAMPS:
    c = Vector((x, y, z))
    box(bm, (x - 0.012, y + 0.03, z + 0.06), (x + 0.012, y + 0.11, zt - 0.03), 1)           # hanger
    vs, _ = box_c(bm, c, (0.16, 0.085, 0.105), 0)                                          # housing
    rotate_verts(bm, vs, TILT, 'X', c)
    vs, _ = box_c(bm, c + Vector((0, -0.044, 0)), (0.17, 0.012, 0.115), 2)                  # chrome rim
    rotate_verts(bm, vs, TILT, 'X', c)
    for s in (1, -1):
        box(bm, (x + s * 0.083 - (0.01 if s > 0 else 0.0), y - 0.01, z - 0.01),
            (x + s * 0.083 + (0.0 if s > 0 else 0.01), y + 0.03, z + 0.07), 1)            # U bracket
        cyl(bm, (x + s * 0.09, y + 0.005, z + 0.01), (x + s * 0.11, y + 0.005, z + 0.01), 0.013, 10, 1)
bc = Vector(BEACON)
cyl(bm, bc - Vector((0, 0, 0.02)), bc + Vector((0, 0, 0.045)), 0.07, 20, 0)
nut(bm, bc + Vector((0.05, 0, 0.045)), (0, 0, 1), af=0.012, h=0.006, mi=1)
for s in (1, -1):
    p0 = Vector((s * 0.80, PLAT_Y0 + 0.08, FZ + 1.10))
    p1 = Vector((s * 1.14, PLAT_Y0 + 0.02, FZ + 1.16))
    cyl(bm, p0 - Vector((0, 0, 0.03)), p0 + Vector((0, 0, 0.03)), 0.03, 12, 1)             # clamp
    tube(bm, [p0, p1, p1 + Vector((0, 0, 0.07))], 0.011, 8, mi=1, round_r=0.03)
    rot = Matrix.Rotation(radians(-s * 12), 3, 'Z')
    mc = p1 + Vector((s * 0.02, 0, 0.18))
    rim_pts = [mc + rot @ Vector((0.09 * cos(a), 0.0, 0.13 * sin(a))) for a in [2 * pi * k / 20 for k in range(20)]]
    sweep(bm, rim_pts, circle2d(0.009, 6), closed=True, mi=1)
    plate(bm, rim_pts, 0.012, rot @ Vector((0, 1, 0)), mi=0)
    plate(bm, [mc + rot @ Vector((0, -0.002, 0)) + (p - mc) * 0.93 for p in rim_pts], 0.002, rot @ Vector((0, -1, 0)),
          mi=3)
make_obj("z050_lampsMisc", bm, [DARK, STEEL, CHROME, CHROME], C, TAG, bevel=0.002)
for (x, y, z) in WORKLAMPS:
    c = Vector((x, y, z))
    vs, _ = box_c(lens, c + Vector((0, -0.052, 0)), (0.145, 0.006, 0.09), 2)
    rotate_verts(lens, vs, TILT, 'X', c)
revolve(lens, [(0.064, 0.045), (0.065, 0.12), (0.052, 0.155), (0.0, 0.17)], 20, center=tuple(bc), axis='Z', mi=1)

# --------------------------------------------- headlights on the front wall
bm = bmesh.new()
for (x, y, z) in HEADLAMPS:
    c = Vector((x, y, z))
    round_lamp(bm, c, (0, -1, 0), r=0.083, depth=0.105, mi_body=0, mi_rim=1, lens=lens, mi_lens=2)
    box(bm, (x - 0.025, y + 0.06, z - 0.14), (x + 0.025, PLAT_Y0 - 0.11, z - 0.05), 0)       # bracket
    nut(bm, (x, PLAT_Y0 - 0.11, z - 0.12), (0, -1, 0), af=0.015, h=0.007, mi=1)
for s in (1, -1):                                                              # front turn indicators
    c = Vector((s * 0.885, PLAT_Y0 - 0.15, 2.07))
    box_c(bm, c + Vector((0, 0.02, 0)), (0.09, 0.05, 0.07), 0)
    box(lens, (c.x - 0.04, c.y - 0.012, c.z - 0.03), (c.x + 0.04, c.y + 0.0, c.z + 0.03), 1)
sh = [(0.0, -0.05), (0.036, -0.02), (0.036, 0.04), (-0.036, 0.04), (-0.036, -0.02)]
plate(bm, [(u, PLAT_Y0 - 0.113, 2.02 + v) for (u, v) in sh], 0.004, (0, -1, 0), mi=3)
make_obj("z050_headlightBodies", bm, [DARK, CHROME, RED, WHITE], C, TAG)

# ------------------------------------------------ dash box + steering column
bm = bmesh.new()
dash = [(PLAT_Y0 - 0.01, FZ), (-1.52, FZ), (-1.52, 2.42), (-1.62, 2.54), (PLAT_Y0 - 0.01, 2.54)]
prism(bm, dash, 'X', -0.21, 0.21, 0)
sl_c = Vector((0.0, -1.57, 2.48))
sl_n = Vector((0.0, 0.12, 0.10)).normalized()
su, sv, _ = frame(sl_n)
for k, dx in enumerate((-0.155, -0.065, 0.065, 0.155)):
    c = sl_c + Vector((dx, 0, 0))
    revolve_v(bm, [(0.028, 0.0), (0.037, 0.0), (0.037, 0.010), (0.031, 0.012)], 18, c, sl_n, 2, closed=True)
    revolve_v(bm, [(0.0, 0.003), (0.030, 0.003)], 18, c, sl_n, 3)
    nd = su * cos(radians(30 + 55 * k)) + sv * sin(radians(30 + 55 * k))
    side = nd.cross(sl_n) * 0.0025
    plate(bm, [c + sl_n * 0.004 - side, c + sl_n * 0.004 + nd * 0.024 - side * 0.3,
               c + sl_n * 0.004 + nd * 0.024 + side * 0.3, c + sl_n * 0.004 + side], 0.001, sl_n, mi=4)
    revolve_v(lens, [(0.0, 0.009), (0.029, 0.008), (0.029, 0.004), (0.0, 0.004)], 18, c, sl_n, 0, closed=True)
for k, dx in enumerate((-0.11, 0.11)):                                          # warning lamps
    c = Vector((dx, -1.66, 2.54))
    revolve_v(bm, [(0.012, 0.0), (0.016, 0.0), (0.016, 0.006)], 12, c, (0, 0, 1), 2)
    revolve_v(lens, [(0.0, 0.016), (0.012, 0.012), (0.012, 0.004)], 12, c, (0, 0, 1), 3 if k == 0 else 1)
for dx in (-0.14, -0.06, 0.02, 0.10):                                           # key + toggle switches
    c = Vector((dx, -1.52, 2.32))
    nut(bm, c, (0, 1, 0), af=0.016, h=0.006, mi=2, washer=False)
    if dx < -0.1:
        cyl(bm, c + Vector((0, 0.006, 0)), c + Vector((0, 0.03, 0)), 0.006, 8, 2)
        box_c(bm, c + Vector((0, 0.038, 0.012)), (0.018, 0.006, 0.03), 1)
    else:
        tube(bm, [c + Vector((0, 0.006, 0)), c + Vector((0, 0.03, 0.012))], 0.0035, 6, mi=2)
fasteners(bm, (-0.19, -1.52, 2.16), (0.19, -1.52, 2.16), (0, 1, 0), 0.095, 'bolt', 2, af=0.012, h=0.005,
          washer=False)
col_base = Vector((0.0, -1.69, 2.54))
col_top = Vector((0.0, -1.40, 3.00))
col_dir = (col_top - col_base).normalized()
cyl(bm, col_base, col_base + col_dir * 0.22, 0.05, 16, 1)
cyl(bm, col_base + col_dir * 0.22, col_top - col_dir * 0.035, 0.034, 16, 1)
cyl(bm, col_top - col_dir * 0.12, col_top - col_dir * 0.08, 0.04, 16, 1)
stalk = col_top - col_dir * 0.10
tube(bm, [stalk + Vector((-0.04, 0, 0)), stalk + Vector((-0.12, 0.01, -0.01))], 0.006, 8, mi=1)
sphere(bm, stalk + Vector((-0.125, 0.01, -0.01)), 0.012, 10, 5, 1)
for x, w in ((0.15, 0.08), (-0.11, 0.07), (-0.20, 0.07)):                        # pedals
    top_p = Vector((x, -1.44, FZ + 0.20))
    tube(bm, [(x, -1.54, FZ - 0.12), (x, -1.52, FZ + 0.04), top_p], 0.011, 8, mi=1, round_r=0.04)
    vs, _ = box_c(bm, top_p + Vector((0, 0.01, 0.03)), (w, 0.022, 0.11), 5)
    rotate_verts(bm, vs, radians(-38), 'X', top_p)
    revolve_v(bm, [(0.03, 0.0), (0.022, 0.03), (0.014, 0.05)], 10, (x, -1.52, FZ), (0, 0, 1), 5)
box(bm, (0.38, PLAT_Y0 - 0.01, 2.24), (0.70, -1.68, 2.49), 6)                            # switch / fuse box
box(bm, (0.40, -1.68, 2.26), (0.68, -1.676, 2.47), 6)
plate(bm, [(0.44, -1.676, 2.30), (0.60, -1.676, 2.30), (0.60, -1.676, 2.40), (0.44, -1.676, 2.40)], 0.0015,
      (0, 1, 0), mi=7)
for x in (0.64, 0.66):
    tube(bm, [(x, -1.676, 2.44), (x, -1.66, 2.45)], 0.003, 6, mi=2)
make_obj("z050_dashBox", bm, [RED, DARK, CHROME, GAUGE, WHITE, RUB, GRAY, WHITE], C, TAG, bevel=0.004)

# steering wheel (own object, local Z = column axis) with spinner knob
bm = bmesh.new()
R = 0.225
sweep(bm, [(R * cos(a), R * sin(a), 0.0) for a in [2 * pi * k / 56 for k in range(56)]],
      circle2d(0.0165, 10), closed=True, mi=0)
cyl(bm, (0, 0, -0.06), (0, 0, 0.025), 0.042, 18, 1)
revolve(bm, [(0.0, 0.035), (0.034, 0.030), (0.040, 0.025)], 18, axis='Z', mi=0)
for k in range(3):
    a = pi / 2 + 2 * pi * k / 3
    tube(bm, [(0.035 * cos(a), 0.035 * sin(a), 0.0), (0.13 * cos(a), 0.13 * sin(a), -0.012),
              ((R - 0.012) * cos(a), (R - 0.012) * sin(a), 0.0)], 0.0115, 8, mi=1)
ka = radians(-35)
kp = Vector((R * cos(ka), R * sin(ka), 0.0))
cyl(bm, kp, kp + Vector((0, 0, 0.05)), 0.009, 8, 1)
cyl(bm, kp + Vector((0, 0, 0.03)), kp + Vector((0, 0, 0.085)), 0.017, 12, 2)
sw = make_obj("steeringWheel", bm, [RUB, DARK, KB], C, TAG)
sw.location = col_top
sw.rotation_euler = (-atan2(col_dir.y, col_dir.z), 0.0, 0.0)
sw["keep"] = True

# ----------------------------------------------- lever console with gear gate
bm = bmesh.new()
cx0, cx1, cy0, cy1, ch = -0.80, -0.50, -1.20, -0.78, 2.86
box(bm, (cx0, cy0, FZ), (cx1, cy1, ch), 0)
box(bm, (cx0 - 0.008, cy0 - 0.008, ch - 0.02), (cx1 + 0.008, cy1 + 0.008, ch + 0.004), 0)
for (ya, yb, za, zb) in ((-1.06, -1.04, 2.52, 2.70), (-0.96, -0.94, 2.52, 2.70), (-1.06, -0.94, 2.60, 2.62)):
    box(bm, (cx1, ya, za), (cx1 + 0.003, yb, zb), 1)                                  # H gear gate
gear_base = Vector((cx1 + 0.003, -1.05, 2.66))
tube(bm, [gear_base, gear_base + Vector((0.06, 0.0, 0.02)), (-0.36, -1.06, 2.95)], 0.009, 8, mi=2, round_r=0.05)
sphere(bm, (-0.36, -1.06, 2.975), 0.024, 12, 6, 3)
for (x, y, L, knob, ang) in ((-0.58, -1.10, 0.30, 3, 6), (-0.70, -1.10, 0.28, 4, -4),
                              (-0.58, -0.88, 0.26, 3, 10), (-0.72, -0.88, 0.42, 3, -12)):
    p0 = Vector((x, y, ch))
    p1 = p0 + Matrix.Rotation(radians(ang), 3, 'X') @ Vector((0, 0, L))
    revolve_v(bm, [(0.028, 0.0), (0.022, 0.03), (0.012, 0.055)], 10, p0, (0, 0, 1), 5)      # rubber boot
    cyl(bm, p0, p1, 0.009, 8, 2)
    sphere(bm, p1, 0.025, 12, 6, knob)
q_c = Vector((cx1 + 0.004, -0.84, 2.70))                                           # hand throttle quadrant
arc = [(q_c.y + 0.11 * cos(radians(a)), q_c.z + 0.11 * sin(radians(a))) for a in range(-20, 111, 10)]
prism(bm, [(q_c.y, q_c.z)] + arc, 'X', cx1 + 0.003, cx1 + 0.009, 1)
tube(bm, [(cx1 + 0.012, q_c.y, q_c.z), (cx1 + 0.02, q_c.y + 0.03, q_c.z + 0.16)], 0.007, 8, mi=2)
sphere(bm, (cx1 + 0.02, q_c.y + 0.03, q_c.z + 0.17), 0.018, 10, 5, 3)
gc = Vector((cx0 + 0.07, cy1 - 0.07, ch + 0.004))
gn = Vector((0.0, 0.5, 1.0)).normalized()
box_c(bm, gc + Vector((0, 0, 0.02)), (0.09, 0.07, 0.04), 0)
g_c = gc + Vector((0, 0.01, 0.04))
revolve_v(bm, [(0.028, 0.0), (0.037, 0.0), (0.037, 0.012), (0.031, 0.014)], 18, g_c, gn, 2, closed=True)
revolve_v(bm, [(0.0, 0.004), (0.030, 0.004)], 18, g_c, gn, 6)
revolve_v(lens, [(0.0, 0.010), (0.029, 0.009), (0.029, 0.005), (0.0, 0.005)], 18, g_c, gn, 0, closed=True)
fasteners(bm, (cx1, cy0 + 0.03, FZ + 0.05), (cx1, cy1 - 0.03, FZ + 0.05), (1, 0, 0), 0.1, 'bolt', 2, af=0.012,
          h=0.005, washer=False)
make_obj("z050_console", bm, [RED, DARK, STEEL, KB, KR, RUB, GAUGE], C, TAG, bevel=0.004)

# ------------------------------------------------------------------ seat
bm = bmesh.new()
sy, sz = -0.82, FZ + 0.44
box_c(bm, (0, sy, FZ + 0.006), (0.30, 0.26, 0.012), 1)
for (dx, dy) in ((-0.12, -0.10), (0.12, -0.10), (-0.12, 0.10), (0.12, 0.10)):
    nut(bm, (dx, sy + dy, FZ + 0.012), (0, 0, 1), af=0.013, h=0.006, mi=2, washer=False)
cyl(bm, (0, sy, FZ + 0.012), (0, sy, sz - 0.05), 0.036, 14, 1)
spring(bm, (0, sy, FZ + 0.05), (0, sy, sz - 0.07), 0.062, 0.0085, 5.5, mi=1, hooks=False)
box_c(bm, (0, sy, sz - 0.04), (0.22, 0.20, 0.03), 1)
pan = rrect2d(0.47, 0.43, 0.09, 3)
loft(bm, [[(x * 0.96, sy + y * 0.96, sz - 0.025) for (x, y) in pan], [(x, sy + y, sz) for (x, y) in pan]], mi=1)
cush = rrect2d(0.46, 0.42, 0.09, 3)
loft(bm, [[(x, sy + y, sz) for (x, y) in cush], [(x * 1.02, sy + y * 1.02, sz + 0.05) for (x, y) in cush],
          [(x * 0.94, sy + y * 0.94, sz + 0.085) for (x, y) in cush]], mi=0)
sweep(bm, [(x * 1.02, sy + y * 1.02, sz + 0.05) for (x, y) in cush], circle2d(0.006, 6), closed=True, mi=0)
back = rrect2d(0.44, 0.36, 0.09, 3)
Rb = Matrix.Rotation(radians(-14), 3, 'X')
base_b = Vector((0, sy + 0.22, sz + 0.10))
rings = []
for (th, sc_) in ((0.0, 1.0), (0.05, 1.02), (0.075, 0.94)):
    rings.append([base_b + Rb @ Vector((x * sc_, th, z * sc_ + 0.20)) for (x, z) in back])
loft(bm, rings, mi=0)
for s in (1, -1):
    tube(bm, [(s * 0.16, sy + 0.18, sz - 0.02), (s * 0.16, sy + 0.26, sz + 0.05),
              base_b + Rb @ Vector((s * 0.16, 0.0, 0.14))], 0.009, 8, mi=1, round_r=0.03)
tube(bm, [(0.2, sy - 0.2, sz - 0.03), (0.26, sy - 0.24, sz - 0.02)], 0.006, 6, mi=1)
sphere(bm, (0.265, sy - 0.245, sz - 0.02), 0.014, 8, 4, 3)
make_obj("z050_seat", bm, [VINYL, DARK, ZINC, KB], C, TAG)

# ------------------------------- fuel tank, toolbox, plank, fire extinguisher
bm = bmesh.new()
box(bm, (-0.84, -0.68, FZ), (-0.54, -0.36, 2.52), 0)
for yy in (-0.62, -0.42):
    box(bm, (-0.845, yy - 0.015, FZ), (-0.535, yy + 0.015, 2.525), 1)                     # hold-down straps
cyl(bm, (-0.62, -0.52, 2.52), (-0.62, -0.52, 2.58), 0.035, 16, 1)
cyl(bm, (-0.62, -0.52, 2.58), (-0.62, -0.52, 2.60), 0.048, 16, 1)
for k in range(6):
    a = 2 * pi * k / 6
    box_c(bm, (-0.62 + 0.048 * cos(a), -0.52 + 0.048 * sin(a), 2.59), (0.012, 0.012, 0.02), 1)
box(bm, (-0.535, -0.64, 2.24), (-0.53, -0.52, 2.44), 2)                                      # sight gauge
make_obj("z050_fuelTank", bm, [RED, DARK, "Z050_glass"], C, TAG, bevel=0.01)

bm = bmesh.new()
box(bm, (0.28, -0.62, FZ), (0.62, -0.34, 2.38), 0)
box(bm, (0.275, -0.625, 2.36), (0.625, -0.335, 2.40), 0)
hinge(bm, (0.30, -0.335, 2.40), (0.60, -0.335, 2.40), 0.007, 4, 1)
tube(bm, [(0.40, -0.625, 2.30), (0.40, -0.645, 2.30), (0.50, -0.645, 2.30), (0.50, -0.625, 2.30)], 0.006, 6, mi=1,
     round_r=0.01)
box(bm, (0.44, -0.628, 2.345), (0.46, -0.62, 2.39), 1)
make_obj("z050_toolbox", bm, [GRAY, STEEL], C, TAG, bevel=0.006)

bm = bmesh.new()
vs, _ = box(bm, (-0.50, -0.47, FZ), (0.26, -0.34, FZ + 0.03), 0)
rotate_verts(bm, vs, radians(1.5), 'Z', (-0.12, -0.40, 0))
for x in (-0.44, 0.20):
    nut(bm, (x, -0.405, FZ + 0.03), (0, 0, 1), af=0.012, h=0.004, mi=1, washer=False)
make_obj("z050_plank", bm, [WOOD, STEEL], C, TAG, bevel=0.004)

bm = bmesh.new()
ec = Vector((-0.74, -1.52, FZ))
revolve_v(bm, [(0.0, 0.01), (0.07, 0.01), (0.075, 0.03), (0.075, 0.38), (0.06, 0.42), (0.03, 0.44), (0.0, 0.445)], 20,
          ec, (0, 0, 1), 0)
cyl(bm, ec + Vector((0, 0, 0.44)), ec + Vector((0, 0, 0.48)), 0.02, 10, 1)
tube(bm, [ec + Vector((0.02, 0, 0.47)), ec + Vector((0.07, 0.02, 0.46)), ec + Vector((0.085, 0.03, 0.30))], 0.008, 6,
     mi=2, round_r=0.03)
box_c(bm, ec + Vector((-0.02, 0, 0.465)), (0.06, 0.015, 0.012), 1)
for z in (0.12, 0.32):
    sweep(bm, [ec + Vector((0.078 * cos(a), 0.078 * sin(a), z)) for a in [2 * pi * k / 20 for k in range(20)]],
          [(-0.012, -0.002), (0.012, -0.002), (0.012, 0.002), (-0.012, 0.002)], closed=True, mi=1, up=(0, 0, 1))
lab = [ec + Vector((0.0762 * cos(a), 0.0762 * sin(a), z)) for (a, z) in
       ((radians(-110), 0.18), (radians(-70), 0.18), (radians(-70), 0.28), (radians(-110), 0.28))]
plate(bm, lab, 0.002, (0, -1, 0), mi=3)
make_obj("z050_extinguisher", bm, [RED, DARK, RUB, WHITE], C, TAG)

# ---------------------------------------------------------------- ladder (L)
bm = bmesh.new()
b_y, b_z, t_y, t_z = -0.99, 0.42, -0.74, FZ - 0.02
ax_ = Vector((0, t_y - b_y, t_z - b_z)).normalized()
nrm_ = Vector((0, ax_.z, -ax_.y))
for x in (0.975, 1.355):
    pts = [Vector((0, b_y, b_z)) - nrm_ * 0.025, Vector((0, b_y, b_z)) + nrm_ * 0.025,
           Vector((0, t_y, t_z)) + nrm_ * 0.025, Vector((0, t_y, t_z)) - nrm_ * 0.025]
    prism(bm, [(p.y, p.z) for p in pts], 'X', x - 0.004, x + 0.004, 0)
for i in range(6):
    t = (i + 0.45) / 6.0
    yy, zz = b_y + (t_y - b_y) * t, b_z + (t_z - b_z) * t
    box(bm, (0.979, yy - 0.06, zz - 0.004), (1.351, yy + 0.06, zz), 3)                    # step plate
    box(bm, (0.979, yy - 0.064, zz - 0.03), (1.351, yy - 0.06, zz), 0)                    # front lip
    for kx in range(7):
        for ky in range(3):
            rivet(bm, (1.005 + kx * 0.053, yy - 0.04 + ky * 0.04, zz), (0, 0, 1), r=0.007, h=0.0028, mi=3)
    for x, s in ((0.971, -1), (1.359, 1)):
        nut(bm, (x, yy, zz - 0.015), (s, 0, 0), af=0.013, h=0.005, mi=1, washer=False)
box(bm, (PLAT_HW, t_y - 0.14, FZ - 0.04), (1.36, t_y + 0.30, FZ), 3)
fasteners(bm, (0.90, t_y - 0.10, FZ), (1.32, t_y - 0.10, FZ), (0, 0, 1), 0.1, 'rivet', 3, r=0.008, h=0.003)
for (y, z) in ((t_y - 0.10, FZ - 0.04), (t_y + 0.26, FZ - 0.04)):
    tube(bm, [(0.98, y, z), (0.95, y, z - 0.35)], 0.016, 8)
tube(bm, [(1.0, b_y + 0.02, b_z + 0.08), (0.93, -0.64, 1.02)], 0.016, 8)                   # bottom support strut
for x in (0.975, 1.355):
    tube(bm, [(x, t_y - 0.05, FZ + 0.02), (x, t_y + 0.02, FZ + 0.90), (x, t_y + 0.30, FZ + 0.92),
              (x, t_y + 0.33, FZ + 0.02)], RAIL_R, 10, round_r=0.07)
make_obj("ladder", bm, [RED, ZINC, STEEL, "Z050_paint_red_floor"], C, TAG, bevel=0.003)

lights_obj("z050_lampsGlass", lens, [GLASS, ORANGE, CLEAR, LRED])
print("operator objects:", sorted(o.name for o in D.objects if o.get("z050_part") == TAG))
