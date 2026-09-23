# 01 - PBR materials with procedural "village" weathering (sun-faded paint,
# dust/grime in crevices and low areas, chipped edges with primer, bare
# metal and rust, vertical rust streaks). Cycles-accurate; the maps are
# baked to textures later for the FS25 export.


def srgb(h):
    """'#RRGGBB' -> linear RGBA."""
    h = h.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)


class G:
    """Tiny node-graph builder."""

    def __init__(self, nt):
        self.nt = nt
        self.n = 0

    def node(self, typ, **props):
        nd = self.nt.nodes.new(typ)
        nd.location = (-1400 + 180 * (self.n // 6), 500 - 170 * (self.n % 6))
        self.n += 1
        for k, v in props.items():
            setattr(nd, k, v)
        return nd

    def set(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.nt.links.new(v, sock)
        else:
            sock.default_value = v

    def math(self, op, a, b=0.0, clamp=False):
        nd = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.set(nd.inputs[0], a)
        self.set(nd.inputs[1], b)
        return nd.outputs[0]

    def add(self, a, b, clamp=False):
        return self.math('ADD', a, b, clamp)

    def mul(self, a, b, clamp=False):
        return self.math('MULTIPLY', a, b, clamp)

    def mr(self, v, fmin, fmax, tmin=0.0, tmax=1.0):
        nd = self.node('ShaderNodeMapRange', clamp=True)
        self.set(nd.inputs[0], v)
        self.set(nd.inputs[1], fmin)
        self.set(nd.inputs[2], fmax)
        self.set(nd.inputs[3], tmin)
        self.set(nd.inputs[4], tmax)
        return nd.outputs[0]

    def mix(self, fac, a, b):
        nd = self.node('ShaderNodeMix', data_type='RGBA', blend_type='MIX', clamp_factor=True)
        self.set(nd.inputs[0], fac)
        self.set(nd.inputs[6], a)
        self.set(nd.inputs[7], b)
        return nd.outputs[2]

    def mixf(self, fac, a, b):
        nd = self.node('ShaderNodeMix', data_type='FLOAT', clamp_factor=True)
        self.set(nd.inputs[0], fac)
        self.set(nd.inputs[2], a)
        self.set(nd.inputs[3], b)
        return nd.outputs[0]

    def noise(self, vec, scale, detail=4.0, rough=0.55, distortion=0.0):
        nd = self.node('ShaderNodeTexNoise')
        self.set(nd.inputs['Vector'], vec)
        self.set(nd.inputs['Scale'], scale)
        self.set(nd.inputs['Detail'], detail)
        self.set(nd.inputs['Roughness'], rough)
        self.set(nd.inputs['Distortion'], distortion)
        return nd.outputs['Fac']

    def sepz(self, vec):
        nd = self.node('ShaderNodeSeparateXYZ')
        self.set(nd.inputs[0], vec)
        return nd.outputs[2]


def build_weathering_group():
    name = "Z050_Weathering"
    old = D.node_groups.get(name)
    if old:
        D.node_groups.remove(old)
    ng = D.node_groups.new(name, 'ShaderNodeTree')
    itf = ng.interface

    def sin_(n, t, dv):
        s = itf.new_socket(name=n, in_out='INPUT', socket_type=t)
        s.default_value = dv
        return s

    sin_("Paint", 'NodeSocketColor', srgb('#C4321F'))
    sin_("Faded", 'NodeSocketColor', srgb('#D46E58'))
    sin_("Primer", 'NodeSocketColor', srgb('#6E3226'))
    sin_("Rust", 'NodeSocketColor', srgb('#6B3A1E'))
    sin_("Dirt", 'NodeSocketColor', srgb('#8A7A63'))
    sin_("Grime", 'NodeSocketColor', srgb('#4A4034'))
    sin_("Fade", 'NodeSocketFloat', 0.5)
    sin_("DirtAmount", 'NodeSocketFloat', 0.6)
    sin_("Chips", 'NodeSocketFloat', 0.5)
    sin_("RustAmount", 'NodeSocketFloat', 0.5)
    sin_("PaintRough", 'NodeSocketFloat', 0.42)
    sin_("Metal", 'NodeSocketFloat', 0.0)
    sin_("Scale", 'NodeSocketFloat', 1.0)
    for n, t in (("Color", 'NodeSocketColor'), ("Roughness", 'NodeSocketFloat'),
                 ("Metallic", 'NodeSocketFloat'), ("Height", 'NodeSocketFloat')):
        itf.new_socket(name=n, in_out='OUTPUT', socket_type=t)

    g = G(ng)
    gi = g.node('NodeGroupInput')
    go = g.node('NodeGroupOutput')
    go.location = (1800, 0)
    I = gi.outputs
    geo = g.node('ShaderNodeNewGeometry')
    pos, nrm = geo.outputs['Position'], geo.outputs['Normal']
    up = g.mr(g.sepz(nrm), 0.15, 1.0)
    low = g.mr(g.sepz(pos), 2.0, 0.15)          # 1 near the ground

    sc = I["Scale"]
    n_large = g.noise(pos, g.mul(sc, 0.55), 3.0, 0.5)
    n_med = g.noise(pos, g.mul(sc, 3.2), 6.0, 0.6)
    n_fine = g.noise(pos, g.mul(sc, 26.0), 8.0, 0.68)
    stretch = g.node('ShaderNodeMapping')
    stretch.inputs['Scale'].default_value = (3.2, 3.2, 0.38)
    g.set(stretch.inputs['Vector'], pos)
    n_streak = g.noise(stretch.outputs['Vector'], g.mul(sc, 2.2), 5.0, 0.62)
    stretch2 = g.node('ShaderNodeMapping')
    stretch2.inputs['Scale'].default_value = (4.5, 4.5, 0.3)
    stretch2.inputs['Location'].default_value = (13.7, 5.1, 2.9)
    g.set(stretch2.inputs['Vector'], pos)
    n_grime = g.noise(stretch2.outputs['Vector'], g.mul(sc, 1.8), 5.0, 0.6)

    # sun fade: strongest on top faces, patchy
    fade = g.mul(g.mul(g.add(g.mul(up, 0.55), 0.45), g.mr(n_large, 0.28, 0.62)), g.mul(I["Fade"], 1.3), True)

    # edge wear (Bevel node -> Cycles/bake only)
    bev = g.node('ShaderNodeBevel', samples=6)
    bev.inputs['Radius'].default_value = 0.014
    dot = g.node('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.set(dot.inputs[0], bev.outputs['Normal'])
    g.set(dot.inputs[1], nrm)
    edge = g.mr(dot.outputs['Value'], 0.985, 0.82)
    chip_field = g.add(g.add(g.mul(edge, 0.8), g.mul(n_fine, 0.55)), g.mul(n_med, 0.3))
    thr = g.math('SUBTRACT', 1.55, g.mul(I["Chips"], 0.72))
    chip_edge = g.mr(g.math('SUBTRACT', chip_field, thr), -0.05, 0.0)
    chip_core = g.mr(g.math('SUBTRACT', chip_field, thr), 0.02, 0.07)

    # crevices
    ao = g.node('ShaderNodeAmbientOcclusion', samples=8, only_local=False)
    ao.inputs['Distance'].default_value = 0.35
    occl = g.mr(ao.outputs['AO'], 0.92, 0.35)

    # rust: in chips, streaking down from edges, in crevices
    streak = g.mul(g.mr(n_streak, 0.56, 0.76), g.math('SUBTRACT', 1.0, g.mul(up, 0.85)))
    rust = g.add(g.mul(chip_core, g.mr(n_med, 0.35, 0.55, 0.35, 1.0)),
                 g.mul(g.add(g.mul(streak, 0.85), g.mul(g.mul(occl, n_med), 0.9)), I["RustAmount"]), True)
    rust = g.mul(rust, g.mr(I["RustAmount"], 0.0, 0.25), True)

    # dust / grime
    dirt_base = g.add(g.add(g.mul(occl, 1.0), g.mul(low, 0.85)), g.mul(up, 0.6))
    dirt = g.mul(g.mul(dirt_base, g.mr(n_med, 0.28, 0.70, 0.3, 1.25)), I["DirtAmount"], True)
    grime_streak = g.mul(g.mr(n_grime, 0.56, 0.78), g.math('SUBTRACT', 1.0, up))
    grime = g.mul(g.add(g.mul(occl, low), g.mul(grime_streak, 0.25)), I["DirtAmount"], True)

    col = g.mix(fade, I["Paint"], I["Faded"])
    col = g.mix(g.mul(chip_edge, g.math('SUBTRACT', 1.0, I["Metal"])), col, I["Primer"])
    bare = g.node('ShaderNodeRGB')
    bare.outputs[0].default_value = srgb('#8E8C86')
    col = g.mix(chip_core, col, bare.outputs[0])
    rust_col = g.mix(g.mr(n_fine, 0.35, 0.65), I["Rust"], g.mix(0.5, I["Rust"], I["Grime"]))
    col = g.mix(rust, col, rust_col)
    col = g.mix(grime, col, I["Grime"])
    col = g.mix(g.mul(dirt, 0.9), col, I["Dirt"])

    rough = g.add(I["PaintRough"], g.mul(fade, 0.22))
    rough = g.mixf(chip_core, rough, 0.38)
    rough = g.mixf(rust, rough, 0.86)
    rough = g.mixf(dirt, rough, 0.93)
    rough = g.add(rough, g.mul(g.math('SUBTRACT', n_fine, 0.5), 0.12), True)

    metal = g.add(I["Metal"], g.mul(chip_core, g.math('SUBTRACT', 1.0, I["Metal"])), True)
    metal = g.mul(metal, g.math('SUBTRACT', 1.0, rust), True)
    metal = g.mul(metal, g.math('SUBTRACT', 1.0, g.mul(dirt, 0.85)), True)

    height = g.add(g.mul(chip_core, -0.6), g.mul(chip_edge, -0.25))
    height = g.add(height, g.mul(rust, g.mul(n_fine, 0.5)))
    height = g.add(height, g.mul(n_fine, 0.08))

    g.set(go.inputs["Color"], col)
    g.set(go.inputs["Roughness"], rough)
    g.set(go.inputs["Metallic"], metal)
    g.set(go.inputs["Height"], height)
    return ng


def new_mat(name):
    m = D.materials.get(name)
    if m is None:
        m = D.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m


def weathered(name, paint, faded, fade=0.5, dirt=0.6, chips=0.5, rust=0.5, rough=0.42,
              metal=0.0, dirt_col='#8A7A63', grime='#4A4034', bump=0.35, scale=1.0, viewport=None):
    m = new_mat(name)
    nt = m.node_tree
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (700, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    grp = nt.nodes.new('ShaderNodeGroup')
    grp.node_tree = D.node_groups["Z050_Weathering"]
    grp.name = grp.label = "Weathering"
    grp.location = (0, 0)
    grp.inputs["Paint"].default_value = srgb(paint)
    grp.inputs["Faded"].default_value = srgb(faded)
    grp.inputs["Dirt"].default_value = srgb(dirt_col)
    grp.inputs["Grime"].default_value = srgb(grime)
    grp.inputs["Fade"].default_value = fade
    grp.inputs["DirtAmount"].default_value = dirt
    grp.inputs["Chips"].default_value = chips
    grp.inputs["RustAmount"].default_value = rust
    grp.inputs["PaintRough"].default_value = rough
    grp.inputs["Metal"].default_value = metal
    grp.inputs["Scale"].default_value = scale
    bump_n = nt.nodes.new('ShaderNodeBump')
    bump_n.location = (200, -300)
    bump_n.inputs['Strength'].default_value = bump
    bump_n.inputs['Distance'].default_value = 0.004
    L = nt.links.new
    L(grp.outputs["Color"], bsdf.inputs["Base Color"])
    L(grp.outputs["Roughness"], bsdf.inputs["Roughness"])
    L(grp.outputs["Metallic"], bsdf.inputs["Metallic"])
    L(grp.outputs["Height"], bump_n.inputs["Height"])
    L(bump_n.outputs["Normal"], bsdf.inputs["Normal"])
    L(bsdf.outputs["BSDF"], out.inputs["Surface"])
    m.diffuse_color = viewport or srgb(paint)
    m.roughness = rough
    return m


def clear_mat(name, color, rough=0.05, transmission=1.0, ior=1.5, viewport_alpha=0.35):
    m = new_mat(name)
    nt = m.node_tree
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (500, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = srgb(color)
    bsdf.inputs['Transmission Weight'].default_value = transmission
    bsdf.inputs['IOR'].default_value = ior
    # dusty glass: rougher towards the bottom
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 18.0
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs[1].default_value = 0.35
    mr.inputs[2].default_value = 0.75
    mr.inputs[3].default_value = rough
    mr.inputs[4].default_value = rough + 0.25
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], mr.inputs[0])
    nt.links.new(mr.outputs[0], bsdf.inputs['Roughness'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    c = srgb(color)
    m.diffuse_color = (c[0], c[1], c[2], viewport_alpha)
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = 'DITHERED'
    return m


build_weathering_group()

RED, RED_FADED = '#BE2F1E', '#D6846C'
weathered("Z050_paint_red", RED, RED_FADED, fade=0.72, dirt=0.82, chips=0.78, rust=0.75, rough=0.42,
          dirt_col='#7C6B55')
weathered("Z050_paint_cream", '#E3D9C4', '#CFC2A6', fade=0.5, dirt=0.9, chips=0.7, rust=0.7, rough=0.48,
          dirt_col='#8A7658')
weathered("Z050_paint_gray", '#A6A9A5', '#B7B7B0', fade=0.35, dirt=0.75, chips=0.55, rust=0.5, rough=0.52)
weathered("Z050_metal_dark", '#2B2A28', '#4A4744', fade=0.35, dirt=0.95, chips=0.5, rust=0.8, rough=0.58)
weathered("Z050_steel", '#8F8E8A', '#9C9A95', fade=0.0, dirt=0.55, chips=0.0, rust=0.55, rough=0.36,
          metal=1.0, grime='#3A342C', bump=0.2)
weathered("Z050_chrome", '#D9D9D6', '#D9D9D6', fade=0.0, dirt=0.35, chips=0.0, rust=0.25, rough=0.12,
          metal=1.0, bump=0.05)
weathered("Z050_rubber_tire", '#1D1D1C', '#3A3833', fade=0.6, dirt=1.0, chips=0.0, rust=0.0, rough=0.86,
          dirt_col='#80725C', grime='#3A3328', bump=0.25, scale=1.6)
weathered("Z050_rubber_black", '#171717', '#2C2B29', fade=0.4, dirt=0.55, chips=0.0, rust=0.0, rough=0.72,
          bump=0.15)
weathered("Z050_decal_white", '#E9E5DA', '#DDD6C4', fade=0.4, dirt=0.75, chips=0.45, rust=0.45, rough=0.4)
weathered("Z050_decal_black", '#141414', '#2A2926', fade=0.3, dirt=0.4, chips=0.25, rust=0.2, rough=0.45)
weathered("Z050_smv_orange", '#F05A1E', '#E97A4C', fade=0.45, dirt=0.55, chips=0.2, rust=0.2, rough=0.3)
clear_mat("Z050_glass", '#F2F4F2', rough=0.04)
clear_mat("Z050_lamp_red", '#C00A08', rough=0.12)
clear_mat("Z050_lamp_orange", '#E86A0A', rough=0.12)

print("materials:", sorted(m.name for m in D.materials if m.name.startswith("Z050_")))
