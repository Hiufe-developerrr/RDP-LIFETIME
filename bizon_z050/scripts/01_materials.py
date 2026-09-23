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

    sin_("Paint", 'NodeSocketColor', srgb('#BA2E1D'))
    sin_("Faded", 'NodeSocketColor', srgb('#C8634A'))
    sin_("Primer", 'NodeSocketColor', srgb('#6E3226'))
    sin_("Rust", 'NodeSocketColor', srgb('#6B3A1E'))
    sin_("Dirt", 'NodeSocketColor', srgb('#9C8D74'))
    sin_("Grime", 'NodeSocketColor', srgb('#3F372D'))
    sin_("Fade", 'NodeSocketFloat', 0.5)
    sin_("DirtAmount", 'NodeSocketFloat', 0.6)
    sin_("Chips", 'NodeSocketFloat', 0.5)
    sin_("RustAmount", 'NodeSocketFloat', 0.5)
    sin_("PaintRough", 'NodeSocketFloat', 0.42)
    sin_("Metal", 'NodeSocketFloat', 0.0)
    sin_("Scale", 'NodeSocketFloat', 1.0)
    sin_("Traffic", 'NodeSocketFloat', 0.0)
    sin_("Oil", 'NodeSocketFloat', 0.0)
    sin_("Mud", 'NodeSocketFloat', 0.0)
    sin_("Wavy", 'NodeSocketFloat', 1.0)
    for n, t in (("Color", 'NodeSocketColor'), ("Roughness", 'NodeSocketFloat'),
                 ("Metallic", 'NodeSocketFloat'), ("Height", 'NodeSocketFloat')):
        itf.new_socket(name=n, in_out='OUTPUT', socket_type=t)

    g = G(ng)
    gi = g.node('NodeGroupInput')
    go = g.node('NodeGroupOutput')
    go.location = (2200, 0)
    I = gi.outputs
    geo = g.node('ShaderNodeNewGeometry')
    pos, nrm = geo.outputs['Position'], geo.outputs['Normal']
    nz = g.sepz(nrm)
    up = g.mr(nz, 0.25, 1.0)
    up2 = g.mul(up, up)
    low = g.mr(g.sepz(pos), 1.9, 0.1)            # 1 at the ground, 0 above 1.9 m
    low2 = g.mul(low, low)

    sc = I["Scale"]
    n_large = g.noise(pos, g.mul(sc, 0.45), 3.0, 0.5)
    n_med = g.noise(pos, g.mul(sc, 2.8), 6.0, 0.6)
    n_fine = g.noise(pos, g.mul(sc, 24.0), 8.0, 0.66)
    n_fine2 = g.noise(pos, g.mul(sc, 41.0), 4.0, 0.55)
    n_speck = g.noise(pos, g.mul(sc, 70.0), 2.0, 0.5)
    n_wave = g.noise(pos, g.mul(sc, 1.6), 2.0, 0.4)
    n_oil = g.noise(pos, g.mul(sc, 3.8), 3.0, 0.55, 0.6)
    thin = g.node('ShaderNodeMapping')
    thin.inputs['Scale'].default_value = (22.0, 22.0, 0.55)
    g.set(thin.inputs['Vector'], pos)
    n_streak = g.noise(thin.outputs['Vector'], sc, 3.0, 0.5)

    # sun fade: mainly on up-facing faces, soft mottling
    fade = g.mul(g.mul(g.add(g.mul(up, 0.7), 0.3), g.mr(n_large, 0.25, 0.7, 0.45, 1.0)), I["Fade"], True)

    # chips: edges (Bevel - Cycles/bake) plus a few random chips on flat areas
    bev = g.node('ShaderNodeBevel', samples=6)
    bev.inputs['Radius'].default_value = 0.012
    dot = g.node('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.set(dot.inputs[0], bev.outputs['Normal'])
    g.set(dot.inputs[1], nrm)
    edge = g.mr(dot.outputs['Value'], 0.985, 0.80)
    field = g.add(g.add(g.mul(edge, 0.85), g.mul(n_fine, 0.5)), g.mul(n_med, 0.25))
    thr = g.math('SUBTRACT', 1.5, g.mul(I["Chips"], 0.62))
    flat_chip = g.mul(g.mr(n_fine2, 0.70, 0.735), g.mul(I["Chips"], 0.7))
    chip_edge = g.add(g.mr(g.math('SUBTRACT', field, thr), -0.05, 0.0), g.mul(flat_chip, 0.6), True)
    chip_core = g.add(g.mr(g.math('SUBTRACT', field, thr), 0.02, 0.07), g.mul(g.mr(n_fine2, 0.725, 0.74), g.mul(I["Chips"], 0.6)), True)

    # foot-traffic wear on up-facing surfaces (floor, steps)
    traffic = g.mul(g.mul(up2, g.mr(g.noise(pos, g.mul(sc, 1.2), 4.0, 0.6), 0.28, 0.62)), I["Traffic"], True)

    # cavities
    ao = g.node('ShaderNodeAmbientOcclusion', samples=8, only_local=False)
    ao.inputs['Distance'].default_value = 0.3
    occl = g.mr(ao.outputs['AO'], 0.95, 0.4)

    # rust: in chips, in cavities, sparse thin runs on vertical faces
    streak = g.mul(g.mr(n_streak, 0.63, 0.78), g.math('SUBTRACT', 1.0, up))
    rust = g.add(g.mul(chip_core, g.mr(n_med, 0.35, 0.55, 0.4, 1.0)),
                 g.mul(g.add(g.mul(streak, 0.35), g.mul(g.mul(occl, g.mr(n_med, 0.4, 0.7)), 0.8)), I["RustAmount"]), True)
    rust = g.mul(rust, g.mr(I["RustAmount"], 0.0, 0.2), True)

    # dust on horizontal faces, grime in cavities, mud splash low down, oil
    dust = g.mul(g.mul(up2, g.mr(n_med, 0.25, 0.7, 0.35, 1.1)), I["DirtAmount"], True)
    grime = g.mul(g.add(g.mul(occl, 0.95), g.mul(low2, 0.35)), g.mul(g.mr(n_med, 0.3, 0.7, 0.4, 1.1), I["DirtAmount"]), True)
    mud = g.mul(g.add(g.mul(low2, g.mr(n_speck, 0.56, 0.62)), g.mul(g.mul(low2, low), g.mr(n_med, 0.4, 0.7, 0.0, 0.8))),
                I["Mud"], True)
    oil = g.mul(g.mul(g.mr(n_oil, 0.62, 0.70), g.add(g.mul(occl, 0.8), 0.2)), I["Oil"], True)

    col = g.mix(fade, I["Paint"], I["Faded"])
    col = g.mix(g.mul(chip_edge, g.math('SUBTRACT', 1.0, I["Metal"])), col, I["Primer"])
    bare = g.node('ShaderNodeRGB')
    bare.outputs[0].default_value = srgb('#8A8983')
    worn = g.node('ShaderNodeRGB')
    worn.outputs[0].default_value = srgb('#6E6D68')
    col = g.mix(chip_core, col, bare.outputs[0])
    col = g.mix(traffic, col, worn.outputs[0])
    rust_col = g.mix(g.mr(n_fine, 0.35, 0.65), I["Rust"], g.mix(0.45, I["Rust"], I["Grime"]))
    col = g.mix(rust, col, rust_col)
    oil_c = g.node('ShaderNodeRGB')
    oil_c.outputs[0].default_value = srgb('#17130F')
    col = g.mix(g.mul(oil, 0.85), col, oil_c.outputs[0])
    col = g.mix(g.mul(grime, 0.8), col, I["Grime"])
    mud_c = g.node('ShaderNodeRGB')
    mud_c.outputs[0].default_value = srgb('#5C4E3C')
    col = g.mix(g.mul(mud, 0.9), col, mud_c.outputs[0])
    col = g.mix(g.mul(dust, 0.8), col, I["Dirt"])

    rough = g.add(I["PaintRough"], g.mul(fade, 0.25))
    rough = g.mixf(chip_core, rough, 0.4)
    rough = g.mixf(traffic, rough, 0.3)
    rough = g.mixf(rust, rough, 0.88)
    rough = g.mixf(oil, rough, 0.22)
    rough = g.mixf(grime, rough, 0.78)
    rough = g.mixf(mud, rough, 0.95)
    rough = g.mixf(dust, rough, 0.94)
    rough = g.add(rough, g.mul(g.math('SUBTRACT', n_fine, 0.5), 0.1), True)

    metal = g.add(I["Metal"], g.mul(g.add(chip_core, traffic, True), g.math('SUBTRACT', 1.0, I["Metal"])), True)
    for m_ in (rust, g.mul(dust, 0.9), mud, g.mul(grime, 0.6), g.mul(oil, 0.3)):
        metal = g.mul(metal, g.math('SUBTRACT', 1.0, m_), True)

    height = g.add(g.mul(chip_core, -0.6), g.mul(chip_edge, -0.22))
    height = g.add(height, g.mul(rust, g.mul(n_fine, 0.5)))
    height = g.add(height, g.mul(n_fine, 0.05))
    height = g.add(height, g.mul(g.mul(g.math('SUBTRACT', n_wave, 0.5), 0.9), I["Wavy"]))
    height = g.add(height, g.mul(mud, g.mul(n_speck, 0.6)))

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
              metal=0.0, dirt_col='#9C8D74', grime='#3F372D', bump=0.35, scale=1.0, viewport=None,
              traffic=0.0, oil=0.0, mud=0.0, wavy=1.0):
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
    grp.inputs["Traffic"].default_value = traffic
    grp.inputs["Oil"].default_value = oil
    grp.inputs["Mud"].default_value = mud
    grp.inputs["Wavy"].default_value = wavy
    m["bump"] = bump
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

RED, RED_FADED = '#BA2E1D', '#C8634A'
weathered("Z050_paint_red", RED, RED_FADED, fade=0.55, dirt=0.75, chips=0.8, rust=0.68, rough=0.4, mud=0.65, oil=0.3)
weathered("Z050_paint_red_floor", RED, RED_FADED, fade=0.5, dirt=0.8, chips=0.95, rust=0.6, rough=0.45,
          traffic=1.0, mud=0.25, oil=0.2, wavy=0.4)
weathered("Z050_paint_cream", '#E1D7C1', '#D2C6AA', fade=0.4, dirt=0.85, chips=0.6, rust=0.6, rough=0.46,
          dirt_col='#A08D6E', mud=0.5)
weathered("Z050_paint_gray", '#A6A9A5', '#B7B7B0', fade=0.3, dirt=0.7, chips=0.5, rust=0.45, rough=0.5, mud=0.4)
weathered("Z050_metal_dark", '#2B2A28', '#46433F', fade=0.3, dirt=0.9, chips=0.45, rust=0.8, rough=0.58,
          oil=0.6, mud=0.6)
weathered("Z050_steel", '#8F8E8A', '#9C9A95', fade=0.0, dirt=0.6, chips=0.0, rust=0.55, rough=0.36,
          metal=1.0, bump=0.2, oil=0.5, wavy=0.2)
weathered("Z050_chrome", '#D9D9D6', '#D9D9D6', fade=0.0, dirt=0.35, chips=0.0, rust=0.3, rough=0.12,
          metal=1.0, bump=0.05, wavy=0.0)
weathered("Z050_zinc", '#A9A79C', '#B5B2A6', fade=0.0, dirt=0.55, chips=0.0, rust=0.5, rough=0.42,
          metal=1.0, bump=0.1, wavy=0.0)
weathered("Z050_chain", '#3A3834', '#44413C', fade=0.0, dirt=0.9, chips=0.0, rust=0.7, rough=0.42,
          metal=1.0, bump=0.1, oil=1.0, wavy=0.0)
weathered("Z050_brass", '#B08D57', '#A58A5E', fade=0.0, dirt=0.5, chips=0.0, rust=0.2, rough=0.35,
          metal=1.0, bump=0.05, wavy=0.0)
weathered("Z050_rubber_tire", '#1D1D1C', '#3A3833', fade=0.6, dirt=1.0, chips=0.0, rust=0.0, rough=0.86,
          dirt_col='#80725C', grime='#3A3328', bump=0.25, scale=1.6, mud=1.0, wavy=0.0)
weathered("Z050_rubber_black", '#171717', '#2C2B29', fade=0.4, dirt=0.55, chips=0.0, rust=0.0, rough=0.72,
          bump=0.15, mud=0.3, wavy=0.0)
weathered("Z050_hose", '#1A1A19', '#2F2E2B', fade=0.5, dirt=0.8, chips=0.0, rust=0.0, rough=0.62,
          bump=0.15, oil=0.3, mud=0.4, wavy=0.0)
weathered("Z050_wire", '#141414', '#262523', fade=0.4, dirt=0.6, chips=0.0, rust=0.0, rough=0.5,
          bump=0.05, wavy=0.0)
weathered("Z050_wire_red", '#8E1B14', '#9E3A2C', fade=0.4, dirt=0.5, chips=0.0, rust=0.0, rough=0.45,
          bump=0.05, wavy=0.0)
weathered("Z050_wire_yellow", '#B8900F', '#BFA04A', fade=0.4, dirt=0.5, chips=0.0, rust=0.0, rough=0.45,
          bump=0.05, wavy=0.0)
weathered("Z050_belt", '#232220', '#34332F', fade=0.3, dirt=0.85, chips=0.0, rust=0.0, rough=0.8,
          bump=0.1, oil=0.2, wavy=0.0)
weathered("Z050_knob_black", '#101010', '#1E1E1D', fade=0.3, dirt=0.4, chips=0.0, rust=0.0, rough=0.35,
          bump=0.03, wavy=0.0)
weathered("Z050_knob_red", '#A0160F', '#B04030', fade=0.4, dirt=0.4, chips=0.0, rust=0.0, rough=0.32,
          bump=0.03, wavy=0.0)
weathered("Z050_vinyl", '#1F1D1B', '#3B3732', fade=0.6, dirt=0.6, chips=0.25, rust=0.0, rough=0.55,
          bump=0.25, wavy=0.3)
weathered("Z050_wood", '#6B5237', '#8E7C63', fade=0.8, dirt=0.8, chips=0.0, rust=0.0, rough=0.88,
          bump=0.6, scale=1.4, mud=0.3, wavy=0.0)
weathered("Z050_plastic_black", '#1B1B1A', '#2F2E2B', fade=0.5, dirt=0.6, chips=0.0, rust=0.0, rough=0.5,
          bump=0.05, wavy=0.0)
weathered("Z050_decal_white", '#E9E5DA', '#DDD6C4', fade=0.4, dirt=0.75, chips=0.45, rust=0.45, rough=0.4)
weathered("Z050_decal_black", '#141414', '#2A2926', fade=0.3, dirt=0.4, chips=0.25, rust=0.2, rough=0.45)
weathered("Z050_decal_yellow", '#E0B21A', '#D9B85A', fade=0.5, dirt=0.6, chips=0.3, rust=0.2, rough=0.4)
weathered("Z050_smv_orange", '#F05A1E', '#E97A4C', fade=0.45, dirt=0.55, chips=0.2, rust=0.2, rough=0.3)
weathered("Z050_gauge", '#0E0E0E', '#1A1A1A', fade=0.1, dirt=0.2, chips=0.0, rust=0.0, rough=0.4,
          bump=0.0, wavy=0.0)
clear_mat("Z050_glass", '#F2F4F2', rough=0.04)
clear_mat("Z050_lamp_clear", '#FFF6E8', rough=0.08)
clear_mat("Z050_lamp_red", '#C00A08', rough=0.12)
clear_mat("Z050_lamp_orange", '#E86A0A', rough=0.12)

print("materials:", sorted(m.name for m in D.materials if m.name.startswith("Z050_")))
