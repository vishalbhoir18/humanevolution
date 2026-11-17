"""Extra geometry: eyeballs (and later hair / clothing)."""
import math

import bpy
import numpy as np


def make_eyes(body, name="eyes", segments=20, rings=14):
    """Two UV spheres with the pole (iris) facing forward.  UVs are a polar
    projection of the front hemisphere so a simple disc texture maps on."""
    verts, faces, uvs = [], [], []
    R = body.head_rot
    r = body.eye_r
    for center in (body.point("eyeL"), body.point("eyeR")):
        base = len(verts)
        # local axes: pole along character-forward (-Y), carried by the head rotation
        for i in range(rings + 1):
            th = math.pi * i / rings            # 0 at the front pole
            for j in range(segments):
                ph = 2 * math.pi * j / segments
                local = np.array([math.sin(th) * math.cos(ph), -math.cos(th), math.sin(th) * math.sin(ph)])
                verts.append(center + (R @ local) * r)
                rr = th / math.pi                # 0 centre .. 1 back pole
                uvs.append((0.5 + 0.5 * rr * math.cos(ph), 0.5 + 0.5 * rr * math.sin(ph)))
        for i in range(rings):
            for j in range(segments):
                a = base + i * segments + j
                b = base + i * segments + (j + 1) % segments
                c = base + (i + 1) * segments + (j + 1) % segments
                d = base + (i + 1) * segments + j
                faces.append((a, d, c, b))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    layer = mesh.uv_layers.new(name="UVMap")
    flat = []
    for poly in mesh.polygons:
        for vi in poly.vertices:
            flat.extend(uvs[vi])
    layer.data.foreach_set("uv", flat)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _tileable_noise(size, seed, beta=1.6, aniso=1.0):
    """Tileable fractal noise in [0, 1] (filtered white noise in Fourier space)."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((size, size)))
    fy = np.fft.fftfreq(size)[:, None] * aniso
    fx = np.fft.fftfreq(size)[None, :]
    k = np.sqrt(fx * fx + fy * fy)
    k[0, 0] = 1.0
    a = np.real(np.fft.ifft2(f / k ** beta))
    a = (a - a.min()) / (a.max() - a.min())
    return a


def make_wrap(body, out_dir, top=-66.0, bottom=-101.0, color=((96, 70, 48), (150, 116, 84)),
              thickness=0.011, name="wrap", tile=5.0, seed=7):
    """A hide wrapped round the hips: body faces between two canonical
    heights (cm below eye level), lifted off the skin, with a ragged hem."""
    import os
    from PIL import Image
    from . import masks as M
    from . import texture as tx
    me = body.obj.data
    can = body._can(body.Vm)
    U, X = can[:, 2], can[:, 0]
    rng = np.random.default_rng(seed)
    # ragged hem: the cut-off height wobbles around the body
    ang = np.arctan2(can[:, 1], can[:, 0])
    hem = bottom + 3.0 * np.sin(ang * 3 + 0.7) + 2.0 * np.sin(ang * 7 + 2.0)
    waist = top + 1.5 * np.sin(ang * 2 + 1.0)
    inside = (U < waist) & (U > hem) & (np.abs(X) < 30.0)
    polys, loops_uv = [], []
    uvl = me.uv_layers.active.data
    for poly in me.polygons:
        vs = list(poly.vertices)
        if all(inside[v] for v in vs):
            polys.append(vs)
            loops_uv.append([tuple(uvl[li].uv) for li in poly.loop_indices])
    used = sorted({v for p in polys for v in p})
    remap = {v: i for i, v in enumerate(used)}
    me.calc_loop_triangles()
    tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("vertices", tris)
    N = M.vertex_normals(body.V, tris.reshape(-1, 3))
    used_a = np.array(used)
    t = (U[used_a] - waist[used_a]) / (hem[used_a] - waist[used_a])          # 0 waist .. 1 hem
    k = body.scale
    off = thickness * k * (0.9 + 1.3 * t) + 0.004 * k * np.sin(ang[used_a] * 11 + U[used_a] * 0.4)
    P = body.V[used_a] + N[used_a] * off[:, None]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in P], [], [[remap[v] for v in p] for p in polys])
    layer = mesh.uv_layers.new(name="UVMap")
    flat = []
    for uvs in loops_uv:
        for (a, b) in uvs:
            flat.extend((a * tile, b * tile))
    layer.data.foreach_set("uv", flat)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    # skin weights copied from the body
    Wl = body.W[used_a].copy()
    order = np.argsort(-Wl, axis=1)
    keepm = np.zeros_like(Wl, dtype=bool)
    np.put_along_axis(keepm, order[:, :4], True, axis=1)
    Wl[~keepm] = 0
    Wl /= Wl.sum(1, keepdims=True)
    for j, b in enumerate(body.bones):
        nz = np.nonzero(Wl[:, j] > 1e-4)[0]
        if len(nz):
            vg = obj.vertex_groups.new(name=b)
            for i in nz:
                vg.add([int(i)], float(Wl[i, j]), "REPLACE")
    # tileable hide texture
    size = 256
    n1 = _tileable_noise(size, seed, 1.7)
    n2 = _tileable_noise(size, seed + 1, 1.1, aniso=0.35)
    dark = tx.srgb_to_linear(np.array(color[0], np.float32) / 255)
    light = tx.srgb_to_linear(np.array(color[1], np.float32) / 255)
    mix = np.clip(0.55 * n1 + 0.45 * n2, 0, 1)
    col = dark[None, None, :] + (light - dark)[None, None, :] * mix[:, :, None]
    h = 0.6 * n2 + 0.4 * n1
    nrm = tx.height_to_normal(np.pad(h, 1, mode="wrap"), 5.0)[1:-1, 1:-1]
    os.makedirs(out_dir, exist_ok=True)
    sid = body.spec["id"]
    pc = os.path.join(out_dir, f"{sid}_hide.jpg")
    pn = os.path.join(out_dir, f"{sid}_hide_n.jpg")
    Image.fromarray((tx.linear_to_srgb(col) * 255 + 0.5).astype(np.uint8)).save(pc, quality=88)
    Image.fromarray((np.clip(nrm, 0, 1) * 255 + 0.5).astype(np.uint8)).save(pn, quality=88)
    m = bpy.data.materials.new(f"{sid}_hide")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage")
    tc.image = bpy.data.images.load(pc)
    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = bpy.data.images.load(pn)
    tn.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.86
    bsdf.inputs["Metallic"].default_value = 0.0
    m.use_backface_culling = False
    obj.data.materials.append(m)
    return obj
