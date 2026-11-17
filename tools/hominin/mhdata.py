"""Loader for the CC0 MakeHuman / MPFB2 base-mesh data set.

Pure numpy: no Blender needed.  Everything is converted on load to Blender
conventions -- metres, Z up, character facing -Y, character's left at +X.

The data set (base mesh hm08, morph targets, rigs, skin weights) is published
by the MakeHuman community under CC0 1.0.  `tools/fetch_assets.py` fetches it.
"""
import gzip
import json
import os

import numpy as np

SCALE = 0.1  # MakeHuman works in decimetres


def mh_to_bl(a):
    """(x, y, z) MakeHuman  ->  (x, -z, y) Blender, decimetres -> metres."""
    a = np.asarray(a, dtype=np.float64)
    out = np.empty_like(a)
    out[..., 0] = a[..., 0]
    out[..., 1] = -a[..., 2]
    out[..., 2] = a[..., 1]
    return out * SCALE


def _expand(ranges):
    idx = []
    for a, b in ranges:
        idx.extend(range(a, b + 1))
    return np.array(idx, dtype=np.int64)


class MHData:
    def __init__(self, root):
        self.root = root
        self._load_obj()
        with open(os.path.join(root, "mesh_metadata", "basemesh_vertex_groups.json")) as f:
            self.groups = {k: _expand(v) for k, v in json.load(f).items()}
        self._target_cache = {}

    # ------------------------------------------------------------------ mesh
    def _load_obj(self):
        verts, uvs, faces, face_uvs = [], [], [], []
        with open(os.path.join(self.root, "3dobjs", "base.obj")) as f:
            for line in f:
                if line.startswith("v "):
                    p = line.split()
                    verts.append((float(p[1]), float(p[2]), float(p[3])))
                elif line.startswith("vt "):
                    p = line.split()
                    uvs.append((float(p[1]), float(p[2])))
                elif line.startswith("f "):
                    vi, ti = [], []
                    for tok in line.split()[1:]:
                        a = tok.split("/")
                        vi.append(int(a[0]) - 1)
                        ti.append(int(a[1]) - 1)
                    faces.append(vi)
                    face_uvs.append(ti)
        self.base = mh_to_bl(np.array(verts))
        self.uv = np.array(uvs, dtype=np.float64)
        self.faces = faces
        self.face_uvs = face_uvs
        self.n = len(verts)

    # --------------------------------------------------------------- targets
    def target(self, name):
        """Sparse morph target -> (indices, deltas[m, Blender axes])."""
        if name in self._target_cache:
            return self._target_cache[name]
        base = os.path.join(self.root, "targets", name + ".target")
        if os.path.exists(base + ".gz"):
            fh = gzip.open(base + ".gz", "rt")
        elif os.path.exists(base):
            fh = open(base)
        else:
            raise FileNotFoundError(name)
        idx, d = [], []
        with fh:
            for line in fh:
                if not line.strip() or line.startswith("#"):
                    continue
                p = line.split()
                idx.append(int(p[0]))
                d.append((float(p[1]), float(p[2]), float(p[3])))
        out = (np.array(idx, dtype=np.int64), mh_to_bl(np.array(d).reshape(-1, 3)))
        self._target_cache[name] = out
        return out

    def has_target(self, name):
        base = os.path.join(self.root, "targets", name + ".target")
        return os.path.exists(base + ".gz") or os.path.exists(base)

    def apply(self, V, name, w=1.0):
        if abs(w) < 1e-6:
            return
        idx, d = self.target(name)
        V[idx] += d * w

    def apply_pair(self, V, stem, value):
        """value in [-1, 1] -> '<stem>-decr' / '<stem>-incr' style pairs.

        `stem` may contain '{}' where the direction word goes, or a tuple
        (neg_name, pos_name) can be passed instead.
        """
        if isinstance(stem, tuple):
            neg, pos = stem
        elif "{}" in stem:
            neg, pos = stem.format("decr"), stem.format("incr")
        else:
            neg, pos = stem + "-decr", stem + "-incr"
        if value >= 0:
            self.apply(V, pos, value)
        else:
            self.apply(V, neg, -value)

    def apply_lr(self, V, folder, stem, value, dirs=("decr", "incr")):
        """Symmetric left/right targets such as cheek/l-cheek-bones-incr."""
        d = dirs[1] if value >= 0 else dirs[0]
        for side in ("l", "r"):
            self.apply(V, f"{folder}/{side}-{stem}-{d}", abs(value))

    # ---------------------------------------------------------------- macros
    def macro(self, gender=0.5, age=0.5, muscle=0.5, weight=0.5, height=0.5,
              proportions=0.5, african=1 / 3, asian=1 / 3, caucasian=1 / 3):
        """Return base mesh + MakeHuman macro targets (same blending rules)."""
        V = self.base.copy()
        g = {"female": 1.0 - gender, "male": gender}
        if age < 0.5:
            baby = max(0.0, 1 - age * 5.333)
            young = max(0.0, (age - 0.1875) * 3.2)
            child = max(0.0, min(1.0, 5.333 * age) - young)
            old = 0.0
        else:
            baby = child = 0.0
            old = max(0.0, age * 2 - 1)
            young = 1 - old
        a = {"baby": baby, "child": child, "young": young, "old": old}

        def tri(v, lo, mid, hi):
            return {hi: max(0.0, v * 2 - 1), lo: max(0.0, 1 - v * 2),
                    mid: 1 - max(0.0, v * 2 - 1) - max(0.0, 1 - v * 2)}

        m = tri(muscle, "minmuscle", "averagemuscle", "maxmuscle")
        w = tri(weight, "minweight", "averageweight", "maxweight")
        h = tri(height, "minheight", "averageheight", "maxheight")
        p = tri(proportions, "uncommonproportions", "regularproportions", "idealproportions")
        tot = african + asian + caucasian
        r = {"african": african / tot, "asian": asian / tot, "caucasian": caucasian / tot}

        for gk, gv in g.items():
            for ak, av in a.items():
                if gv * av < 1e-6:
                    continue
                for rk, rv in r.items():
                    self.apply(V, f"macrodetails/{rk}-{gk}-{ak}", gv * av * rv)
                for mk, mv in m.items():
                    for wk, wv in w.items():
                        base_w = gv * av * mv * wv
                        if base_w < 1e-6:
                            continue
                        self.apply(V, f"macrodetails/universal-{gk}-{ak}-{mk}-{wk}", base_w)
                        for hk, hv in h.items():
                            n = f"macrodetails/height/{gk}-{ak}-{mk}-{wk}-{hk}"
                            if hk != "averageheight" and self.has_target(n):
                                self.apply(V, n, base_w * hv)
                        for pk, pv in p.items():
                            n = f"macrodetails/proportions/{gk}-{ak}-{mk}-{wk}-{pk}"
                            if pk != "regularproportions" and self.has_target(n):
                                self.apply(V, n, base_w * pv)
        return V

    # ------------------------------------------------------------------- rig
    def rig(self, name="game_engine"):
        with open(os.path.join(self.root, "rigs", "standard", f"rig.{name}.json")) as f:
            return json.load(f)

    def weights(self, name="game_engine"):
        """Dense (n_verts, n_bones) skin-weight matrix and the bone order."""
        with open(os.path.join(self.root, "rigs", "standard", f"weights.{name}.json")) as f:
            w = json.load(f)["weights"]
        bones = list(self.rig(name).keys())
        col = {b: i for i, b in enumerate(bones)}
        W = np.zeros((self.n, len(bones)), dtype=np.float64)
        for b, lst in w.items():
            if b not in col:
                continue
            arr = np.array(lst, dtype=np.float64).reshape(-1, 2)
            W[arr[:, 0].astype(np.int64), col[b]] = arr[:, 1]
        s = W.sum(1, keepdims=True)
        s[s == 0] = 1.0
        return W / s, bones

    def joint_pos(self, V, spec):
        """Evaluate a rig head/tail position spec against morphed vertices."""
        st = spec.get("strategy")
        if st == "CUBE":
            return V[self.groups[spec["cube_name"]]].mean(0)
        if st == "VERTEX":
            return V[spec["vertex_index"]].copy()
        if st == "MEAN":
            return V[np.array(spec["vertex_indices"])].mean(0)
        if st == "XYZ":
            ix, iy, iz = spec["vertex_indices"]
            return np.array([V[ix][0], V[iy][1], V[iz][2]])
        return np.array(spec["default_position"], dtype=np.float64)

    def joints(self, V, rig):
        """{bone: (head, tail, roll, parent)} evaluated on morphed vertices."""
        out = {}
        for b, d in rig.items():
            out[b] = (self.joint_pos(V, d["head"]), self.joint_pos(V, d["tail"]),
                      float(d.get("roll", 0.0)), d.get("parent") or None)
        return out
