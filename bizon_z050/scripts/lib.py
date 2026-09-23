"""Shared helpers for the Bizon Z050 Super build.

The MCP client prepends this file to every build script, so each
execute_blender_code call is self-contained. Units: metres. The machine faces
-Y (Blender front view shows its front), +X is the machine's LEFT side,
Z is up, ground at Z=0, front (drive) axle at Y=0.
"""
import bpy
import bmesh
import math
from math import pi, sin, cos, tan, radians, sqrt, atan2
from mathutils import Vector, Matrix, Quaternion

D = bpy.data

# ------------------------------------------------------------ key dimensions
# Sources: Z050 Super spec sheets (length with 4.2 m header ~8.2 m, width
# without header 3.2 m, height without cab 3.63 m, tyres 18.4-30 / 10.00-15,
# reel dia 1.0 m) and photo proportions of Z050/Z056 machines.
HB = 0.95                      # half width of the thresher body
FW_R, FW_W, FW_X = 0.775, 0.47, 1.34          # front drive wheels 18.4-30
RW_R, RW_W, RW_X, RW_Y = 0.40, 0.26, 1.00, 3.55  # rear steer wheels 10.00-15
PLAT_Z, PLAT_Y0, PLAT_Y1, PLAT_HW = 2.12, -1.75, -0.30, 0.86
TANK_Y0, TANK_Y1, TANK_TOP, TANK_HW = -0.30, 2.12, 3.40, 0.975
ENG_Y0 = 1.22                  # engine bay starts behind the grain tank
REAR_TOP, REAR_Y = 2.75, 4.92
CANOPY_Z = 3.63
FEEDER_PIVOT = (0.0, -0.66, 1.66)


# ---------------------------------------------------------------- scene utils
def coll(name, parent=None):
    c = D.collections.get(name)
    if c is None:
        c = D.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def purge_part(tag):
    """Delete everything a build step created before (idempotent re-runs)."""
    for o in list(D.objects):
        if o.get("z050_part") == tag:
            data = o.data
            D.objects.remove(o, do_unlink=True)
            if data is not None and data.users == 0:
                if isinstance(data, bpy.types.Mesh):
                    D.meshes.remove(data)
                elif isinstance(data, bpy.types.Curve):
                    D.curves.remove(data)


def mat(name):
    m = D.materials.get(name)
    if m is None:
        raise KeyError("material missing: " + name)
    return m


def empty(name, loc, collection, tag, parent=None, size=0.3, kind='PLAIN_AXES'):
    ob = D.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = loc
    collection.objects.link(ob)
    ob["z050_part"] = tag
    if parent is not None:
        set_parent(ob, parent)
    return ob


def world_matrix(ob):
    """World matrix computed from the hierarchy (matrix_world may be stale
    until the depsgraph updates)."""
    m = ob.matrix_basis.copy()
    if ob.parent is not None:
        m = world_matrix(ob.parent) @ ob.matrix_parent_inverse @ m
    return m


def set_parent(child, parent):
    """Parent while keeping the world transform and an identity parent-inverse
    (clean local transforms for the i3d/FBX export)."""
    mw = world_matrix(child)
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.matrix_basis = world_matrix(parent).inverted() @ mw


def make_obj(name, bm, mats, collection, tag, origin=None, parent=None,
             smooth=35.0, bevel=None, bevel_segs=2, bevel_angle=35.0, wnormal=True):
    """bmesh -> mesh object. With `bevel`, edges above bevel_angle get a
    chamfer and a Weighted Normal modifier keeps large faces crisp."""
    if origin is not None:
        bmesh.ops.translate(bm, verts=bm.verts, vec=-Vector(origin))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = D.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(mat(m) if isinstance(m, str) else m)
    ob = D.objects.new(name, me)
    collection.objects.link(ob)
    if origin is not None:
        ob.location = origin
    ob["z050_part"] = tag
    me.shade_smooth()
    if bevel:
        md = ob.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = bevel_segs
        md.limit_method = 'ANGLE'
        md.angle_limit = radians(bevel_angle)
        md.use_clamp_overlap = True
        md.harden_normals = True
        md.miter_outer = 'MITER_ARC'
    elif smooth is not None:
        me.set_sharp_from_angle(angle=radians(smooth))
    if wnormal and bevel:
        wn = ob.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
        wn.keep_sharp = True
        wn.weight = 50
    if parent is not None:
        set_parent(ob, parent)
    return ob


# ------------------------------------------------------------ bmesh builders
def _faces_of(verts):
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    return list(fs)


def _mi(faces, mi):
    for f in faces:
        f.material_index = mi
    return faces


def box(bm, lo, hi, mi=0):
    lo, hi = Vector(lo), Vector(hi)
    c, s = (lo + hi) / 2, hi - lo
    m = Matrix.Translation(c) @ Matrix.Diagonal((s.x, s.y, s.z, 1.0))
    vs = bmesh.ops.create_cube(bm, size=1.0, matrix=m)['verts']
    return vs, _mi(_faces_of(vs), mi)


def box_c(bm, c, s, mi=0):
    c, s = Vector(c), Vector(s)
    return box(bm, c - s / 2, c + s / 2, mi)


def prism(bm, pts, axis='X', a0=0.0, a1=1.0, mi=0, cap=True):
    """Extrude a closed 2D outline between a0..a1 along `axis`.
    axis X: pts=(y,z); Y: (x,z); Z: (x,y)."""
    def P(u, v, a):
        if axis == 'X':
            return (a, u, v)
        if axis == 'Y':
            return (u, a, v)
        return (u, v, a)
    n = len(pts)
    A = [bm.verts.new(P(u, v, a0)) for u, v in pts]
    B = [bm.verts.new(P(u, v, a1)) for u, v in pts]
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    if cap:
        fs.append(bm.faces.new(list(reversed(A))))
        fs.append(bm.faces.new(B))
    return A + B, _mi(fs, mi)


def loft(bm, rings, closed=False, cap=True, mi=0):
    """Skin a list of equal-length closed vertex-position rings."""
    R = [[bm.verts.new(Vector(p)) for p in ring] for ring in rings]
    n = len(R[0])
    fs = []
    last = len(R) if closed else len(R) - 1
    for i in range(last):
        a, b = R[i], R[(i + 1) % len(R)]
        for k in range(n):
            k1 = (k + 1) % n
            fs.append(bm.faces.new((a[k], a[k1], b[k1], b[k])))
    if cap and not closed:
        fs.append(bm.faces.new(list(reversed(R[0]))))
        fs.append(bm.faces.new(R[-1]))
    return R, _mi(fs, mi)


def cyl(bm, p0, p1, r, segs=24, mi=0, cap=True, r1=None):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation((p0 + p1) / 2) @ rot
    vs = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                               radius1=r, radius2=(r if r1 is None else r1),
                               depth=d.length, matrix=m)['verts']
    return vs, _mi(_faces_of(vs), mi)


def sphere(bm, c, r, segs=16, rings=8, mi=0):
    m = Matrix.Translation(Vector(c))
    vs = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r, matrix=m)['verts']
    return vs, _mi(_faces_of(vs), mi)


def revolve(bm, prof, segs, center=(0, 0, 0), axis='X', mi=0, closed=False,
            phase=0.0, arc=2 * pi):
    """Revolve profile points (radius, axial) around an axis through center."""
    c = Vector(center)
    full = abs(arc - 2 * pi) < 1e-6
    nring = segs if full else segs + 1

    def P(r, a, th):
        ca, sa = cos(th), sin(th)
        if axis == 'X':
            return c + Vector((a, r * ca, r * sa))
        if axis == 'Y':
            return c + Vector((r * ca, a, r * sa))
        return c + Vector((r * ca, r * sa, a))

    rings = []
    for (r, a) in prof:
        if r < 1e-7:
            v = bm.verts.new(P(0.0, a, 0.0))
            rings.append([v] * nring)
        else:
            rings.append([bm.verts.new(P(r, a, phase + arc * k / segs)) for k in range(nring)])
    fs = []
    npr = len(prof)
    last = npr if closed else npr - 1
    for i in range(last):
        R0, R1 = rings[i], rings[(i + 1) % npr]
        for k in range(segs):
            k1 = (k + 1) % nring if full else k + 1
            quad = []
            for v in (R0[k], R0[k1], R1[k1], R1[k]):
                if v not in quad:
                    quad.append(v)
            if len(quad) >= 3:
                try:
                    fs.append(bm.faces.new(quad))
                except ValueError:
                    pass
    return rings, _mi(fs, mi)


def circle2d(r, n, phase=0.0):
    return [(r * cos(phase + 2 * pi * i / n), r * sin(phase + 2 * pi * i / n)) for i in range(n)]


def rect2d(w, h):
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


def rrect2d(w, h, r, segs=4, cx=0.0, cy=0.0):
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    pts = []
    for (qx, qy, a0) in ((w / 2 - r, -h / 2 + r, -pi / 2), (w / 2 - r, h / 2 - r, 0.0),
                         (-w / 2 + r, h / 2 - r, pi / 2), (-w / 2 + r, -h / 2 + r, pi)):
        for k in range(segs + 1):
            a = a0 + (pi / 2) * k / segs
            pts.append((cx + qx + r * cos(a), cy + qy + r * sin(a)))
    return pts


def fillet(points, r, segs=6):
    """Round the interior corners of a polyline with arcs of radius r."""
    pts = [Vector(p) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        a, b = (p0 - p1), (p2 - p1)
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        a.normalize()
        b.normalize()
        ang = a.angle(b)
        if ang > pi - 1e-3 or ang < 1e-3:
            out.append(p1)
            continue
        t = min(r / tan(ang / 2), (p0 - p1).length * 0.5, (p2 - p1).length * 0.5)
        rr = t * tan(ang / 2)
        s = p1 + a * t
        cen = p1 + (a + b).normalized() * (rr / sin(ang / 2))
        v0, v1 = s - cen, (p1 + b * t) - cen
        axis = v0.cross(v1)
        if axis.length < 1e-12:
            out.append(p1)
            continue
        axis.normalize()
        tot = v0.angle(v1)
        for k in range(segs + 1):
            out.append(cen + Quaternion(axis, tot * k / segs) @ v0)
    out.append(pts[-1])
    return out


def sweep(bm, path, prof, closed=False, cap=True, mi=0, up=(0, 0, 1), twist=0.0):
    """Sweep a closed 2D profile along a 3D polyline (parallel-transport frames,
    mitred corners so the section keeps its thickness)."""
    P = [Vector(p) for p in path]
    n = len(P)
    T = []
    for i in range(n):
        if closed:
            t = (P[(i + 1) % n] - P[i]).normalized() + (P[i] - P[i - 1]).normalized()
        elif i == 0:
            t = P[1] - P[0]
        elif i == n - 1:
            t = P[-1] - P[-2]
        else:
            t = (P[i + 1] - P[i]).normalized() + (P[i] - P[i - 1]).normalized()
        T.append(t.normalized())
    upv = Vector(up)
    N = upv - upv.dot(T[0]) * T[0]
    if N.length < 1e-6:
        N = Vector((1, 0, 0)) - T[0].x * T[0]
    N.normalize()
    rings = []
    for i in range(n):
        if i > 0:
            N = T[i - 1].rotation_difference(T[i]) @ N
            N = (N - N.dot(T[i]) * T[i]).normalized()
        B = T[i].cross(N)
        k_dir, s = None, 1.0
        if closed or 0 < i < n - 1:
            a = (P[(i + 1) % n] - P[i]).normalized()
            b = (P[i] - P[i - 1]).normalized()
            k = a - b
            if k.length > 1e-6:
                k_dir = k.normalized()
                half = math.acos(max(-1.0, min(1.0, a.dot(b)))) / 2
                s = 1.0 / max(cos(half), 0.25)
        tw = twist * i / max(1, n - 1)
        ring = []
        for (u, v) in prof:
            if tw:
                u, v = u * cos(tw) - v * sin(tw), u * sin(tw) + v * cos(tw)
            o = N * u + B * v
            if k_dir is not None:
                ok = o.dot(k_dir)
                o = o + k_dir * ok * (s - 1.0)
            ring.append(P[i] + o)
        rings.append(ring)
    return loft(bm, rings, closed=closed, cap=cap, mi=mi)


def tube(bm, path, r, segs=12, mi=0, closed=False, cap=True, round_r=None, round_segs=5):
    if round_r:
        path = fillet(path, round_r, round_segs)
    return sweep(bm, path, circle2d(r, segs), closed=closed, cap=cap, mi=mi)


def ngon(bm, pts, mi=0):
    f = bm.faces.new([bm.verts.new(Vector(p)) for p in pts])
    f.material_index = mi
    return f


def plate(bm, pts, thickness, normal, mi=0):
    """Planar outline (3D points, CCW seen from `normal`) extruded by thickness."""
    nrm = Vector(normal).normalized()
    rings = [[Vector(p) for p in pts], [Vector(p) + nrm * thickness for p in pts]]
    return loft(bm, rings, cap=True, mi=mi)


def helix_flight(bm, cy, cz, x0, x1, r_in, r_out, pitch, thick, hand=1, segs_turn=36,
                 mi=0, phase=0.0):
    """Auger flight (helicoid strip) around an X-parallel axis at (cy, cz)."""
    L = x1 - x0
    turns = L / pitch
    nst = max(2, int(abs(turns) * segs_turn))
    rings = []
    for k in range(nst + 1):
        t = k / nst
        x = x0 + L * t
        th = phase + hand * 2 * pi * turns * t
        c, s = cos(th), sin(th)
        rings.append([(x - thick / 2, cy + r_in * c, cz + r_in * s),
                      (x - thick / 2, cy + r_out * c, cz + r_out * s),
                      (x + thick / 2, cy + r_out * c, cz + r_out * s),
                      (x + thick / 2, cy + r_in * c, cz + r_in * s)])
    return loft(bm, rings, cap=True, mi=mi)


def transform_verts(bm, verts, m):
    bmesh.ops.transform(bm, matrix=m, verts=list(verts))


def rotate_verts(bm, verts, angle, axis, center):
    m = Matrix.Rotation(angle, 3, axis)
    bmesh.ops.rotate(bm, cent=Vector(center), matrix=m, verts=list(verts))


def mirror_copy_x(bm, verts):
    """Duplicate geometry mirrored across X=0 (normals fixed by recalc later)."""
    faces = _faces_of(verts)
    ret = bmesh.ops.duplicate(bm, geom=list(verts) + faces)
    nv = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    for v in nv:
        v.co.x = -v.co.x
    nf = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMFace)]
    bmesh.ops.reverse_faces(bm, faces=nf)
    return nv


def mesh_to_bm(bm, me, matrix=Matrix.Identity(4), mi=0):
    """Append a Mesh datablock into bm with a transform."""
    tmp = bmesh.new()
    tmp.from_mesh(me)
    bmesh.ops.transform(tmp, matrix=matrix, verts=tmp.verts)
    for f in tmp.faces:
        f.material_index = mi
    tmp_me = D.meshes.new("_tmp_merge")
    tmp.to_mesh(tmp_me)
    tmp.free()
    n0 = len(bm.verts)
    bm.from_mesh(tmp_me)
    D.meshes.remove(tmp_me)
    bm.verts.ensure_lookup_table()
    return bm.verts[n0:]


def text_mesh(body, size, extrude, align='CENTER', bevel=0.0, font_bold=False):
    """Text converted to a mesh datablock (XY plane, facing +Z)."""
    cu = D.curves.new("_txt", 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.resolution_u = 4
    ob = D.objects.new("_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = D.meshes.new_from_object(ob.evaluated_get(dg))
    D.objects.remove(ob, do_unlink=True)
    D.curves.remove(cu)
    return me


# text orientation matrices: text X (reading dir) / Y (up) / Z (normal) -> world
FACE_LEFT = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))).to_4x4()     # on +X side
FACE_RIGHT = Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0))).to_4x4()  # on -X side
FACE_REAR = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0))).to_4x4()    # on +Y side
FACE_FRONT = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))).to_4x4()   # on -Y side


def bolt_ring(bm, center, axis, radius, count, r_bolt, h, segs=6, mi=0, phase=0.0):
    """Hex nuts arranged on a circle, sitting on a plane normal to `axis`."""
    c = Vector(center)
    ax = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(ref).normalized()
    v = ax.cross(u)
    for i in range(count):
        a = phase + 2 * pi * i / count
        p = c + (u * cos(a) + v * sin(a)) * radius
        cyl(bm, p, p + ax * h, r_bolt, segs=segs, mi=mi)


def belt_path(pulleys, n_arc=10):
    """Closed path around circles [(y, z, r), ...] listed in wrap order, all
    wrapped on the outside (open belt drive). Returns (y, z) points."""
    area = 0.0
    for i in range(len(pulleys)):
        (y1, z1, _), (y2, z2, _) = pulleys[i], pulleys[(i + 1) % len(pulleys)]
        area += y1 * z2 - y2 * z1
    if area > 0:  # the tangent maths below expects clockwise order
        pulleys = list(reversed(pulleys))
    pts = []
    m = len(pulleys)
    tang = []
    for i in range(m):
        (y1, z1, r1), (y2, z2, r2) = pulleys[i], pulleys[(i + 1) % m]
        dx, dy = y2 - y1, z2 - z1
        d = sqrt(dx * dx + dy * dy)
        ang = atan2(dy, dx)
        beta = math.acos(max(-1.0, min(1.0, (r1 - r2) / d)))
        a = ang + beta
        tang.append(((y1 + r1 * cos(a), z1 + r1 * sin(a)), (y2 + r2 * cos(a), z2 + r2 * sin(a)), a))
    for i in range(m):
        (y, z, r) = pulleys[i]
        a_in = tang[i - 1][2]
        a_out = tang[i][2]
        while a_out > a_in:
            a_out -= 2 * pi
        for k in range(n_arc + 1):
            a = a_in + (a_out - a_in) * k / n_arc
            pts.append((y + r * cos(a), z + r * sin(a)))
    return pts


def tag_all(objs, tag):
    for o in objs:
        o["z050_part"] = tag
