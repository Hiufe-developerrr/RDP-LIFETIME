# 05c - electrical installation: wiring looms with band clips and grommets to
# every lamp, battery box with red/black cables, horn, grain-tank-full lamp,
# rear harness along the left side, work lights / beacon up the canopy posts.
TAG = "electrics"
purge_part(TAG)
C = coll("Z050_combine")
MATS = ["Z050_wire", "Z050_plastic_black", "Z050_zinc", "Z050_wire_red", "Z050_wire_yellow",
        "Z050_paint_gray", "Z050_metal_dark", "Z050_battery" if D.materials.get("Z050_battery") else "Z050_plastic_black"]
W, CLIP, ZN, WR, WY, GRAY, DARK, BAT = range(8)
bm = bmesh.new()
FZ = PLAT_Z


def loom(path, r=0.0055, clips=0.26, mi=W, rr=0.05):
    cable(bm, path, r, mi, round_r=rr, clip_pitch=clips, clip_mi=CLIP)


def grommet(p, n, r=0.012):
    revolve_v(bm, [(r * 0.55, 0.0), (r, 0.0), (r, 0.006), (r * 0.55, 0.008)], 10, p, n, CLIP, closed=True)


# ---------------------------------------------------- front: headlights, indicators, horn
yw = PLAT_Y0 - 0.125                       # just in front of the front wall
for (x, y, z) in HEADLAMPS:
    s = 1 if x > 0 else -1
    loom([(x, y + 0.07, z - 0.06), (x, yw, z - 0.12), (x, yw, 1.83), (s * 0.10, yw, 1.83), (s * 0.10, yw, 1.80),
          (s * 0.10, PLAT_Y0 + 0.08, PLAT_Z - 0.06)], 0.005, 0.22)
    grommet(Vector((x, y + 0.075, z - 0.06)), (0, -1, 0))
    loom([(s * 0.885, PLAT_Y0 - 0.13, 2.04), (s * 0.885, yw, 1.95), (s * 0.80, yw, 1.84), (s * 0.64, yw, 1.83)],
         0.0032, 0.0, WY, 0.03)
hc = Vector((0.30, yw - 0.02, 1.86))                 # trumpet horn under the front wall
cyl(bm, hc + Vector((-0.06, 0, 0)), hc + Vector((0.02, 0, 0)), 0.03, 12, DARK)
cyl(bm, hc + Vector((0.02, 0, 0)), hc + Vector((0.12, 0, 0)), 0.018, 12, DARK, r1=0.05)
box(bm, (0.23, yw - 0.005, 1.84), (0.25, yw + 0.02, 1.90), DARK)
loom([(0.24, yw - 0.02, 1.86), (0.24, yw, 1.83), (0.18, yw, 1.83)], 0.0032, 0.0, WR, 0.02)

# ------------------------------------- canopy: work lights and beacon cable
post = (PLAT_HW - 0.06 + 0.0, PLAT_Y0 + 0.08)
px, py = 0.80 + 0.028, PLAT_Y0 + 0.08
loom([(0.18, -1.70, 2.54), (0.30, -1.70, 2.56), (px, py + 0.02, 2.56), (px, py + 0.02, CANOPY_Z - 0.09),
      (0.55, py + 0.02, CANOPY_Z - 0.085), (0.55, -1.86, CANOPY_Z - 0.085), (0.55, -1.90, 3.52)], 0.0055, 0.28)
loom([(0.55, py + 0.02, CANOPY_Z - 0.085), (-0.55, py + 0.02, CANOPY_Z - 0.085), (-0.55, -1.86, CANOPY_Z - 0.085),
      (-0.55, -1.90, 3.52)], 0.0045, 0.3)
loom([(-0.55, py + 0.02, CANOPY_Z - 0.085), (-0.80 + 0.03, py + 0.02, CANOPY_Z - 0.085),
      (-0.80 + 0.03, -0.40, CANOPY_Z - 0.085), (BEACON[0], -0.40, CANOPY_Z - 0.085),
      (BEACON[0], BEACON[1] - 0.03, CANOPY_Z + 0.02)], 0.0045, 0.3)
grommet(Vector((BEACON[0], BEACON[1] - 0.03, CANOPY_Z - 0.035)), (0, 0, -1))

# --------------------------------- grain tank full lamp (faces the operator)
tl = Vector((0.45, TANK_Y0 - 0.02, 3.06))
box(bm, (tl.x - 0.035, TANK_Y0 - 0.02, tl.z - 0.035), (tl.x + 0.035, TANK_Y0, tl.z + 0.035), DARK)
lens = bmesh.new()
revolve_v(lens, [(0.0, 0.045), (0.022, 0.04), (0.03, 0.02), (0.03, 0.0)], 16, tl, (0, -1, 0), 0)
revolve_v(bm, [(0.034, -0.004), (0.036, 0.004), (0.031, 0.006)], 16, tl, (0, -1, 0), ZN)
loom([(tl.x + 0.03, TANK_Y0 - 0.012, tl.z), (0.62, TANK_Y0 - 0.012, tl.z), (0.66, TANK_Y0 - 0.012, 2.95),
      (0.66, TANK_Y0 - 0.012, FZ + 0.30), (0.66, -0.66, FZ + 0.02)], 0.0045, 0.25)

# ------------------------------------------ rear harness along the left side
xh = HB + 0.035
loom([(0.10, PLAT_Y0 + 0.08, PLAT_Z - 0.06), (0.10, -0.70, PLAT_Z - 0.07), (0.62, -0.66, 2.00),
      (0.90, -0.63, 1.90), (xh, -0.55, 1.72), (xh, 4.60, 1.72), (xh, 4.86, 1.70), (0.80, REAR_Y + 0.02, 1.64),
      (-0.80, REAR_Y + 0.02, 1.64), (-0.80, REAR_Y + 0.15, 1.66)], 0.0065, 0.3, rr=0.08)
loom([(0.80, REAR_Y + 0.02, 1.64), (0.80, REAR_Y + 0.15, 1.66)], 0.004, 0.0, rr=0.02)
loom([(xh, 1.22, 1.72), (xh, 1.26, 1.85), (xh, 1.26, 2.28), (TANK_HW + 0.012, 1.27, 2.32)], 0.005, 0.25)  # engine
grommet(Vector((TANK_HW, 1.27, 2.32)), (1, 0, 0), 0.014)
loom([(xh, 4.70, 1.72), (0.62, REAR_Y + 0.02, 2.28), (0.84, REAR_Y + 0.02, 2.28)], 0.0035, 0.0, WY, 0.05)

# ------------------------------------------------- battery box (right front)
bx0, bx1, by0, by1, bz0, bz1 = -0.93, -0.64, -0.86, -0.64, 1.55, 1.86
box(bm, (bx0, by0, bz0), (bx1, by1, bz1 - 0.03), GRAY)
box(bm, (bx0 - 0.006, by0 - 0.006, bz1 - 0.035), (bx1 + 0.006, by1, bz1), GRAY)                 # lid
hinge(bm, (bx0 + 0.02, by1 - 0.004, bz1), (bx1 - 0.02, by1 - 0.004, bz1), 0.007, 3, ZN)
tube(bm, [((bx0 + bx1) / 2 - 0.05, by0 - 0.006, bz1 - 0.02), ((bx0 + bx1) / 2 - 0.05, by0 - 0.03, bz1 - 0.02),
          ((bx0 + bx1) / 2 + 0.05, by0 - 0.03, bz1 - 0.02), ((bx0 + bx1) / 2 + 0.05, by0 - 0.006, bz1 - 0.02)],
     0.006, 6, mi=ZN, round_r=0.01)
for x in (bx0 + 0.02, bx1 - 0.02):
    box(bm, (x - 0.02, by1, bz0 + 0.02), (x + 0.02, -0.62, bz0 + 0.06), DARK)
    nut(bm, (x, -0.62, bz0 + 0.04), (0, 1, 0), af=0.013, h=0.005, mi=ZN)
for (x, mi) in ((bx0 + 0.06, WR), (bx0 + 0.12, W)):
    grommet(Vector((x, by0, bz0 + 0.06)), (0, -1, 0), 0.016)
cable(bm, [(bx0 + 0.06, by0 - 0.005, bz0 + 0.06), (bx0 + 0.06, by0 - 0.06, bz0 + 0.02), (-0.965, by0 - 0.02, 1.62),
           (-0.965, -0.40, 1.83), (-0.965, 0.90, 1.83), (-0.965, 0.94, 2.10), (-0.962, 0.945, 2.30)], 0.009, WR,
      round_r=0.08, clip_pitch=0.3, clip_mi=CLIP)
grommet(Vector((-0.955, 0.945, 2.30)), (-1, 0, 0), 0.016)
cable(bm, [(bx0 + 0.12, by0 - 0.005, bz0 + 0.06), (bx0 + 0.12, by0 - 0.07, bz0 - 0.02), (-0.80, -0.70, 1.36),
           (-0.741, -0.70, 1.37)], 0.009, W, round_r=0.05)
nut(bm, (-0.745, -0.70, 1.37), (1, 0, 0), af=0.017, h=0.008, mi=ZN)

ob = make_obj("z050_electrics", bm, MATS, C, TAG)
ob["grp"] = "detail"
lo = make_obj("z050_tankLampGlass", lens, ["Z050_lamp_orange"], C, TAG)
lo["grp"] = "lights"
print("electrics:", len(ob.data.polygons), "faces")
