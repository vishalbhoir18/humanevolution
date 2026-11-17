"""Compose skin / hair PBR textures for a shaped body.

Everything here is *inferred* soft tissue: skin tone, hair colour and hair
cover do not fossilise.  The per-species choices live in looks.py together
with the reasoning behind them.
"""
import os

import bpy
import numpy as np

from . import masks as M
from . import texture as tx
from .sculpt import sstep, g


def _lin(rgb255):
    return tx.srgb_to_linear(np.array(rgb255, dtype=np.float32) / 255.0)


def vertex_regions(body):
    """Per-vertex masks (R, G, B) = (palm / sole, hand / foot, ventral torso)."""
    me = body.obj.data
    me.calc_loop_triangles()
    tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("vertices", tris)
    tris = tris.reshape(-1, 3)
    N = M.vertex_normals(body.Vm, tris)             # canonical A-pose normals
    W, bones = body.W, body.bones

    def wsum(pred):
        cols = [i for i, b in enumerate(bones) if pred(b)]
        return W[:, cols].sum(1)

    hand = wsum(lambda b: b.startswith(("hand", "thumb", "index", "middle", "ring", "pinky")))
    foot = wsum(lambda b: b.startswith(("foot", "ball")))
    torso = wsum(lambda b: b.startswith(("spine", "pelvis")))
    # in the A-pose palms and soles face the ground
    palm = sstep(0.25, 0.75, hand) * sstep(-0.05, -0.45, N[:, 2])
    sole = sstep(0.25, 0.75, foot) * sstep(-0.35, -0.75, N[:, 2])
    ventral = sstep(0.3, 0.8, torso) * sstep(0.15, 0.6, -N[:, 1])
    return np.stack([np.clip(palm + sole, 0, 1), np.clip(hand + foot, 0, 1), ventral], axis=1)


def compose(body, look, out_dir, size=2048, log=print):
    """Bake and write <id>_color.jpg, <id>_normal.jpg, <id>_orm.jpg.
    Returns the Blender material."""
    obj = body.obj
    sid = body.spec["id"]
    root = body.data.root
    can = body._can(body.Vm) / 100.0
    lo, hi = can.min(0), can.max(0)
    tx.set_point_attr(obj, "can", (can - lo) / (hi - lo))
    tx.set_point_attr(obj, "stance", body.V_stance)
    tx.set_point_attr(obj, "reg", vertex_regions(body))

    bk = tx.Baker(obj, size=size)
    cmap = bk.attribute("can")
    cover = cmap.sum(2) > 1e-6
    C = (cmap * (hi - lo) + lo) * 100.0            # canonical head-frame cm
    X, F, U = C[:, :, 0], C[:, :, 1], C[:, :, 2]
    AX = np.abs(X)
    reg = bk.attribute("reg")
    palm, extrem, ventral = reg[:, :, 0], reg[:, :, 1], reg[:, :, 2]
    k = look.get("strand", 1.0)
    nA = bk.noise("stance", [dict(scale=(520, 520, 520), detail=2.0),
                             dict(scale=(26, 26, 26), detail=4.0),
                             dict(scale=(430 / k, 430 / k, 24 / k), detail=3.0)])
    nB = bk.noise("stance", [dict(scale=(170 / k, 170 / k, 11 / k), detail=3.0),
                             dict(scale=(150, 150, 150), detail=3.0),
                             dict(scale=(5.5, 5.5, 5.5), detail=2.0)])
    ao = bk.ao(look.get("ao_samples", 24))
    ao = np.clip(tx.blur(ao, 1), 0, 1)
    pores, mottle, strand = nA[:, :, 0], nA[:, :, 1], nA[:, :, 2]
    clump, crease, broad = nB[:, :, 0], nB[:, :, 1], nB[:, :, 2]

    def norm(a):                                   # stretch noise to ~0..1
        m = a[cover]
        p1, p99 = np.percentile(m, [1, 99])
        return np.clip((a - p1) / (p99 - p1 + 1e-6), 0, 1)

    pores, mottle, strand, clump, crease, broad = map(norm, (pores, mottle, strand, clump, crease, broad))

    lips = tx.load_mask(root, "lips", size)
    nails = np.clip(tx.load_mask(root, "fingernails", size) + tx.load_mask(root, "toenails", size), 0, 1)
    ears = tx.load_mask(root, "ears", size)
    lids = tx.load_mask(root, "eyelids", size)
    areola = tx.load_mask(root, "aureolae", size)
    mouth_in = tx.load_mask(root, "inside-mouth", size)

    is_head = U > -17.0
    jit = (clump - 0.5) * 1.3 + (mottle - 0.5) * 0.8          # cm, breaks up region edges

    # ------------------------------------------------------------ hair regions
    scalp = M.scalp(X, F, U, look.get("hairline"), jit) * is_head * (1 - ears)
    beard = M.beard(X, F, U, jit) * is_head * (1 - lips) * (1 - ears)
    brows = M.brows(X, F, U, jit)

    face_bare = sstep(-3.2, -0.6, F + jit * 0.5) * sstep(-10.6, -8.6, U + jit * 0.4) * sstep(3.9, 2.9, U + jit * 0.3) * is_head
    face_bare = np.clip(face_bare + lids + ears * look.get("ear_bare", 1.0), 0, 1)

    cov = look.get("cover", {})
    body_cov = cov.get("body", 0.1) + (cov.get("ventral", cov.get("body", 0.1)) - cov.get("body", 0.1)) * ventral
    body_cov = body_cov * (1 - 0.75 * extrem) + cov.get("hands", 0.0) * extrem
    head_cov = cov.get("head", cov.get("body", 0.1))
    fur_cov = np.where(is_head, head_cov, body_cov)
    fur_cov = fur_cov * (1 - face_bare * (1 - cov.get("face", 0.0))) * (1 - palm) * (1 - lips) * (1 - nails)
    hair_cov = np.clip(scalp * look.get("scalp", 0.0) + beard * look.get("beard", 0.0), 0, 1)
    brow_cov = brows * look.get("brows", 0.0)

    def strands(c, fine, coarse):
        """Coverage 0..1 -> per-texel hair presence, strand-shaped at the low end."""
        t = 0.6 * fine + 0.4 * coarse
        return sstep(1.0 - c - 0.32, 1.0 - c + 0.22, t) * sstep(0.0, 0.06, c)

    fur_a = strands(fur_cov, strand, clump)
    # scalp / beard edges are stippled with isotropic noise so they do not "drip"
    hair_a = sstep(0.30, 0.62, hair_cov + (pores - 0.5) * 0.35 + (crease - 0.5) * 0.25) * sstep(0.0, 0.06, hair_cov)
    brow_a = strands(brow_cov, strand, pores)

    # ------------------------------------------------------------------ colour
    skin = _lin(look["skin"])
    col = np.ones((size, size, 3), np.float32) * skin
    mv = look.get("mottle", 1.0)
    col *= (1 - 0.09 * mv + 0.18 * mv * mottle)[:, :, None] * (0.95 + 0.10 * broad)[:, :, None]
    # the eye sockets and the hollows beside the nose sit in shadow and read darker
    orbit = g(AX, 2.9, 2.1) * g(U, 0.1, 1.5) * sstep(-2.0, 0.5, F) * is_head
    col *= (1 - 0.16 * orbit)[:, :, None]
    flush = _lin(look.get("flush", (150, 70, 60)))
    f_amt = look.get("flush_amt", 0.16)
    cheeks = g(AX, 4.6, 2.0) * g(U, -3.0, 1.9) * sstep(-3.0, 0.5, F)
    nose_tip = g(X, 0, 1.6) * g(U, -3.8, 1.3) * sstep(2.0, 3.6, F)
    fl = np.clip((cheeks * 0.8 + nose_tip * 0.7) * is_head + ears * 0.8 + lids * 0.35, 0, 1) * f_amt
    col = col * (1 - fl[:, :, None]) + flush * fl[:, :, None]
    pm = palm * 0.9
    col = col * (1 - pm[:, :, None]) + _lin(look.get("palm", look["skin"])) * pm[:, :, None]
    lm = lips * look.get("lip_amt", 0.75)
    col = col * (1 - lm[:, :, None]) + _lin(look.get("lips", (120, 70, 66))) * lm[:, :, None]
    nm = nails * 0.85
    col = col * (1 - nm[:, :, None]) + _lin(look.get("nails", (196, 170, 150))) * nm[:, :, None]
    ar = areola * 0.5
    col = col * (1 - ar[:, :, None]) + _lin(look.get("lips", (120, 70, 66))) * ar[:, :, None]
    col = col * (1 - mouth_in[:, :, None]) + _lin((70, 30, 30)) * mouth_in[:, :, None]

    def lay(col, alpha, dark, light):
        tone = _lin(dark)[None, None, :] + (_lin(light) - _lin(dark))[None, None, :] * (0.55 * strand + 0.45 * clump)[:, :, None]
        tone = tone * (0.85 + 0.3 * broad)[:, :, None]
        return col * (1 - alpha[:, :, None]) + tone * alpha[:, :, None]

    fur = look.get("fur", ((40, 30, 24), (88, 66, 50)))
    hair = look.get("hair", fur)
    # skin under dense hair reads darker (shadowing between strands)
    shade = 1 - 0.35 * np.clip(fur_cov + hair_cov, 0, 1) * (1 - np.maximum(fur_a, hair_a))
    col *= shade[:, :, None]
    col = lay(col, fur_a, *fur)
    col = lay(col, hair_a, *hair)
    col = lay(col, brow_a, *hair)
    col *= (1 - look.get("ao_amt", 0.55) * (1 - ao))[:, :, None]
    col[~cover] = skin

    # --------------------------------------------------------------- roughness
    any_hair = np.clip(fur_a + hair_a + brow_a, 0, 1)
    rough = 0.52 + 0.10 * pores
    rough -= 0.10 * (nose_tip + g(AX, 0, 3.5) * g(U, 4.5, 2.2) * sstep(-2, 1, F)) * is_head
    rough = rough * (1 - lips * 0.9) + 0.36 * lips * 0.9
    rough = rough * (1 - nails) + 0.3 * nails
    rough = rough * (1 - palm * 0.7) + 0.66 * palm * 0.7
    rough = rough * (1 - any_hair) + (0.74 + 0.12 * strand) * any_hair
    rough = np.clip(rough, 0.2, 1.0)
    rough[~cover] = 0.6

    # ------------------------------------------------------------------ height
    wr = look.get("wrinkle", 1.0)
    h = 0.10 * pores + 0.16 * wr * np.abs(crease - 0.5) * 2 * (1 - any_hair)
    h += any_hair * (0.75 * strand + 0.55 * clump) * look.get("hair_relief", 1.0)
    h *= (1 - nails) * (1 - 0.6 * lips)
    h += lips * 0.07 * np.abs(np.sin(X * 5.0 + crease * 3.0))
    h[~cover] = 0
    nrm = tx.height_to_normal(tx.blur(h, 0) if False else h, look.get("bump", 3.2) * size / 2048.0)
    nrm[~cover] = (0.5, 0.5, 1.0)

    orm = np.stack([np.ones_like(rough), rough, np.zeros_like(rough)], axis=2)
    os.makedirs(out_dir, exist_ok=True)
    files = {}
    from PIL import Image
    for name, arr, q in (("color", tx.linear_to_srgb(col), 88), ("normal", nrm, 84), ("orm", orm, 84)):
        p = os.path.join(out_dir, f"{sid}_{name}.jpg")
        a8 = (np.clip(arr[::-1], 0, 1) * 255.0 + 0.5).astype(np.uint8)
        im = Image.fromarray(a8)
        if name == "orm" and size > 1024:
            im = im.resize((1024, 1024), Image.LANCZOS)
        im.save(p, quality=q, subsampling=2, optimize=True)
        files[name] = p
    imgs = {}
    for name, p in files.items():
        img = bpy.data.images.load(p)
        img.colorspace_settings.name = "sRGB" if name == "color" else "Non-Color"
        imgs[name] = img

    m = bpy.data.materials.new(f"{sid}_skin")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage")
    tc.image = imgs["color"]
    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = imgs["normal"]
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    to = nt.nodes.new("ShaderNodeTexImage")
    to.image = imgs["orm"]
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(to.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    obj.data.materials.clear()
    obj.data.materials.append(m)
    for a in ("can", "stance", "reg"):
        ca = obj.data.color_attributes.get(a)
        if ca:
            obj.data.color_attributes.remove(ca)
    bpy.data.materials.remove(bk.mat)
    return m, files


def eye_material(body, look, out_dir, size=256):
    """Iris / sclera texture for the polar-mapped eyeballs."""
    from PIL import Image
    sid = body.spec["id"]
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (xx + 0.5) / size - 0.5
    v = (yy + 0.5) / size - 0.5
    r = np.sqrt(u * u + v * v) * 2          # 0 centre .. 1 back pole
    ang = np.arctan2(v, u)
    ir = look.get("iris_r", 0.19)           # ~34 deg half-angle
    sclera = _lin(look.get("sclera", (232, 226, 214)))
    iris_in, iris_out = _lin(look.get("iris", ((120, 78, 38), (58, 36, 18)))[0]), _lin(look.get("iris", ((120, 78, 38), (58, 36, 18)))[1])
    col = np.ones((size, size, 3), np.float32) * sclera
    col *= (1 - 0.25 * sstep(0.45, 1.0, r))[:, :, None]
    veins = 0.5 + 0.5 * np.sin(ang * 23 + np.sin(ang * 7) * 2)
    col[:, :, 1:] *= (1 - 0.05 * veins * sstep(0.3, 0.8, r))[:, :, None]
    t = np.clip(r / ir, 0, 1)
    fib = 0.5 + 0.5 * np.sin(ang * 60 + np.sin(ang * 11) * 1.5)
    ic = iris_in[None, None, :] + (iris_out - iris_in)[None, None, :] * sstep(0.35, 1.0, t)[:, :, None]
    ic = ic * (0.8 + 0.3 * fib)[:, :, None]
    a = sstep(ir * 1.05, ir * 0.93, r)
    col = col * (1 - a[:, :, None]) + ic * a[:, :, None]
    limb = np.exp(-((r - ir) / (ir * 0.12)) ** 2) * 0.55
    col *= (1 - limb)[:, :, None]
    pupil = sstep(ir * 0.46, ir * 0.38, r)
    col *= (1 - pupil * 0.97)[:, :, None]
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f"{sid}_eye.jpg")
    Image.fromarray((tx.linear_to_srgb(col)[::-1] * 255 + 0.5).astype(np.uint8)).save(p, quality=90)
    img = bpy.data.images.load(p)
    m = bpy.data.materials.new(f"{sid}_eye")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage")
    tc.image = img
    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.12
    bsdf.inputs["Metallic"].default_value = 0.0
    return m
