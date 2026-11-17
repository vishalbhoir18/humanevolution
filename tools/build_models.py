#!/usr/bin/env python3
"""Build the 3D / AR models of the seven stages.

Run with Blender's Python (either works):

    blender --background --python tools/build_models.py -- [ids...] [--size 2048]
    python tools/build_models.py [ids...]          # with the `bpy` wheel installed

Needs the CC0 MakeHuman/MPFB2 base data: run tools/fetch_assets.py first.
Outputs models/<id>.glb, models/posters/<id>.webp and models/models.json.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import numpy as np  # noqa: E402

from hominin import anim, build, export, looks, parts, quadruped, skin, species  # noqa: E402
from hominin import scene as sc  # noqa: E402
from hominin.mhdata import MHData  # noqa: E402

REPO = os.path.dirname(HERE)
DATA = os.environ.get("MPFB2_DATA", os.path.join(HERE, ".cache", "mpfb2"))
OUT = os.environ.get("MODELS_OUT", os.path.join(REPO, "models"))
TMP = os.environ.get("MODELS_TMP", os.path.join(HERE, ".cache", "textures"))


def gltf(p):
    """Blender (x, y, z) -> glTF (x, z, -y)."""
    return [round(float(p[0]), 4), round(float(p[2]), 4), round(float(-p[1]), 4)]


def surface_point(V, origin, direction, radius):
    """Outermost body vertex near the ray origin + t * direction."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    rel = V - origin
    t = rel @ d
    perp = np.linalg.norm(rel - t[:, None] * d, axis=1)
    ok = (perp < radius) & (t > -radius)
    if not ok.any():
        return origin
    return origin + d * t[ok].max()


def hotspots(b):
    """Anatomical anchor points on the skin, in glTF coordinates."""
    s = b.skel
    I = s.idx
    k = b.scale
    R = b.head_rot
    quad = b.spec.get("stance", {}).get("kind") == "quadruped"
    fwd, up, left = np.array([0, -1.0, 0]), np.array([0, 0, 1.0]), np.array([1.0, 0, 0])
    spine_dir = s.tail[I["spine_02"]] - s.head[I["spine_02"]]
    spine_dir /= np.linalg.norm(spine_dir)
    back = np.cross(left, spine_dir)          # points out of the back
    if back[1] < 0 and not quad:
        back = -back
    if quad and back[2] < 0:
        back = -back
    out = {}

    def add(name, origin, direction, radius=0.035):
        d = np.asarray(direction, float)
        d /= np.linalg.norm(d)
        p = surface_point(b.V, np.asarray(origin, float), d, radius * max(k, 0.6)) + d * 0.004
        out[name] = dict(position=gltf(p), normal=gltf(d))

    add("braincase", b.point("lm_vertex") - R @ np.array([0, 0, 0.02]) * k, R @ (up * 0.9 + left * 0.45))
    add("brow", b.point("lm_brow"), R @ (fwd + left * 0.35 + up * 0.2), 0.02)
    add("face", b.point("lm_prosthion"), R @ (fwd + left * 0.3), 0.02)
    add("chin", b.point("lm_chin"), R @ (fwd * 0.8 - up * 0.5), 0.02)
    add("shoulder", s.head[I["upperarm_l"]], left + up * 0.5)
    add("chest", s.head[I["spine_03"]] + 0.5 * (s.tail[I["spine_03"]] - s.head[I["spine_03"]]), -back + left * 0.3, 0.05)
    add("arm", s.head[I["lowerarm_l"]], left + (fwd if not quad else -fwd) * 0.3)
    add("hand", 0.5 * (s.head[I["index_01_l"]] + s.head[I["pinky_01_l"]]), left + (up if quad else fwd) * 0.6, 0.025)
    add("pelvis", s.head[I["thigh_l"]], left + (up * 0.6 if quad else fwd * 0.2), 0.05)
    add("knee", s.head[I["calf_l"]], fwd + left * 0.4)
    add("foot", s.head[I["ball_l"]], up + left * 0.5, 0.03)
    return out


def poster_extent(b):
    """Height (m) covered by the poster frame; the page uses it to draw the
    posters to a common scale."""
    lo, hi = b.V.min(0), b.V.max(0)
    return float(max(hi[2] - lo[2], 0.72 * np.hypot(hi[0] - lo[0], hi[1] - lo[1]) * 1.25) * 1.12)


def poster(b, objs, path, res=(600, 800)):
    scene = bpy.context.scene
    sc.setup_render(scene, samples=96, res=res)
    scene.render.film_transparent = True
    lo, hi = b.V.min(0), b.V.max(0)
    c = (lo + hi) / 2
    ext = poster_extent(b)
    sc.studio_lights(c, max(ext, 0.8) * 0.78)
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1.4
    tmp = path + ".png"
    scene.render.image_settings.color_mode = "RGBA"
    sc.render_view(tmp, c, ext, 32, elevation_deg=6, res=res)
    from PIL import Image
    Image.open(tmp).save(path, "WEBP", quality=86, method=6)
    os.remove(tmp)


def build_one(data, sid, size=2048, log=print):
    t0 = time.time()
    spec = species.SPECIES[sid]
    look = looks.LOOKS[sid]
    sc.reset_scene()
    b = build.Body(data, spec, log=lambda *a: None).fit()
    b.commit()
    extras = [parts.make_eyes(b)]
    _, tex = skin.compose(b, look, TMP, size=size)
    extras[0].data.materials.append(skin.eye_material(b, look, TMP))
    if spec.get("wrap"):
        extras.append(parts.make_wrap(b, TMP, **spec["wrap"]))
    arm = b.rig(extras)
    quad = spec.get("stance", {}).get("kind") == "quadruped"
    g = spec.get("gait", {})
    if quad:
        idle, walk = quadruped.quad_idle(b), quadruped.quad_walk(b, **g)
    else:
        idle, walk = anim.biped_idle(b), anim.biped_walk(b, **g)
    anim.write_action(arm, b.skel, "Idle", idle, rest=b.rest)
    anim.write_action(arm, b.skel, "Walk", walk, rest=b.rest)
    anim.write_action(arm, b.skel, "Rest", [({}, {}), ({}, {})], rest=b.rest, loop=False)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "posters"), exist_ok=True)
    glb = os.path.join(OUT, f"{sid}.glb")
    objs = [arm, b.obj, *extras]
    export.export_glb(glb, objs)
    export.fix_quaternion_continuity(glb)
    export.preview(arm, "Idle")           # the poster shows the first frame the viewer will show
    bpy.context.scene.frame_set(0)
    poster(b, objs, os.path.join(OUT, "posters", f"{sid}.webp"))
    export.end_preview(arm)
    m = b.measure()
    lo, hi = b.V.min(0), b.V.max(0)
    meta = dict(
        id=sid, file=f"models/{sid}.glb", poster=f"models/posters/{sid}.webp",
        bytes=os.path.getsize(glb), vertices=int(len(b.V)), animations=["Idle", "Walk", "Rest"],
        stance=spec.get("stance", {}).get("kind", "biped"),
        height_m=round(float(hi[2] - lo[2]), 3), length_m=round(float(hi[1] - lo[1]), 3),
        upright_stature_m=spec["stature"], poster_extent_m=round(poster_extent(b), 3),
        trunk_pitch_deg=round(float(getattr(b, "trunk_pitch", 0.0)), 1),
        head_length_cm=round(m["head_length"] * 100, 1), head_breadth_cm=round(m["head_breadth"] * 100, 1),
        limb_ratio_vs_modern=dict(
            humerofemoral=round(spec.get("limbs", {}).get("humerofemoral", 71.5) / 71.5, 3),
            brachial=round(spec.get("limbs", {}).get("brachial", 77.0) / 77.0, 3),
            crural=round(spec.get("limbs", {}).get("crural", 83.5) / 83.5, 3)),
        hotspots=hotspots(b),
        inferred=look.get("basis", ""),
    )
    log(f"{sid}: {meta['bytes'] / 1e6:.2f} MB, {meta['vertices']} verts, "
        f"height {meta['height_m']} m, {time.time() - t0:.0f} s")
    return meta


def main(argv):
    size = 2048
    ids = []
    it = iter(argv)
    for a in it:
        if a == "--size":
            size = int(next(it))
        else:
            ids.append(a)
    ids = ids or list(species.ORDER)
    data = MHData(DATA)
    path = os.path.join(OUT, "models.json")
    meta = {}
    if os.path.exists(path):
        with open(path) as f:
            meta = {m["id"]: m for m in json.load(f)["models"]}
    for sid in ids:
        meta[sid] = build_one(data, sid, size)
    os.makedirs(OUT, exist_ok=True)
    with open(path, "w") as f:
        json.dump(dict(
            note="Generated by tools/build_models.py. Body mesh: MakeHuman/MPFB2 base mesh (CC0), "
                 "reshaped to published fossil measurements. Soft tissue is inferred.",
            models=[meta[s] for s in species.ORDER if s in meta]), f, indent=1)
    # the same data as a script, so the page also works without fetch()
    with open(os.path.join(OUT, "models.js"), "w") as f:
        f.write("/* generated by tools/build_models.py */\nwindow.HOMININ_MODELS = ")
        json.dump([meta[s] for s in species.ORDER if s in meta], f, separators=(",", ":"))
        f.write(";\n")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
