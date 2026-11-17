"""Shape one hominin body: morph targets -> head sculpt -> proportions -> stance.

The numeric work is numpy; Blender is used for the mesh container, the
adaptive subdivision of the head and (later stages) baking and export.
"""
import bmesh
import numpy as np

from . import scene as sc
from .body import Skeleton, rot, rot_between, rx, ry, rz, solve_two_bone, FRONT, UP
from .sculpt import HeadField, sstep

RIG = "game_engine"

# Published modern-human means used as the reference for limb indices.
HUMAN_INDEX = dict(humerofemoral=71.5, brachial=77.0, crural=83.5)

CENTRAL = ("pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "Root")
FINGERS = ("index", "middle", "ring", "pinky")

# canonical head landmarks (x, f, u) in cm on the reference head
LANDMARKS = {
    "glabella": (0, 2.4, 2.5), "opisthocranion": (0, -17.7, 3.0), "vertex": (0, -6.0, 10.8),
    "eu_l": (7.4, -8.0, 4.0), "eu_r": (-7.4, -8.0, 4.0), "nose": (0, 4.1, -4.0),
    "prosthion": (0, 3.4, -6.3), "chin": (0, 2.4, -10.6), "porion": (0, -9.0, -1.5),
    "brow": (0, 2.5, 2.2), "nasion": (0, 2.2, 0.6), "mouth_l": (2.6, 2.4, -7.0),
    "zygion_l": (6.6, -2.0, -2.2), "inion": (0, -16.5, -2.5),
}


def _both(scales):
    out = {}
    for k, v in scales.items():
        v = (v, v, v) if np.isscalar(v) else tuple(v)
        if k.endswith(("_l", "_r")) or k in CENTRAL:
            out[k] = v
        else:
            out[k + "_l"] = v
            out[k + "_r"] = v
    return out


def _mul(scales, bone, v):
    cur = np.array(scales.get(bone, (1.0, 1.0, 1.0)), float)
    scales[bone] = tuple(cur * np.array(v, float))


class Body:
    def __init__(self, data, spec, subdiv=True, log=print):
        self.data, self.spec, self.log = data, spec, log
        self._targets()
        self._mesh(subdiv)
        self._sculpt()

    # ------------------------------------------------------------ 1. targets
    def _targets(self):
        d, spec = self.data, self.spec
        V0 = d.macro(**spec.get("macro", {}))
        for name, w in spec.get("targets", {}).items():
            if name.startswith("LR:"):
                folder, stem = name[3:].split("/")
                for side in ("l", "r"):
                    d.apply(V0, f"{folder}/{side}-{stem}", w)
            else:
                d.apply(V0, name, w)
        hallux = spec.get("hallux_abduct", 0.0)
        if hallux:
            self._abduct_hallux(V0, hallux)
        self.V0 = V0
        self.skel0 = Skeleton(d.joints(V0, d.rig(RIG)))
        self.eyes0 = np.stack([V0[d.groups["helper-l-eye"]].mean(0), V0[d.groups["helper-r-eye"]].mean(0)])
        self.eye_r0 = float(np.ptp(V0[d.groups["helper-l-eye"]], axis=0).mean() / 2)
        self.E = self.eyes0.mean(0)

    def _abduct_hallux(self, V0, deg):
        """Swing the big toe away from the others (grasping ape foot)."""
        d = self.data
        import json
        import os
        with open(os.path.join(d.root, "rigs", "standard", "weights.default.json")) as f:
            w = json.load(f)["weights"]
        rig = d.rig("default")
        for side, sg in (("L", 1.0), ("R", -1.0)):
            mask = np.zeros(d.n)
            for b in (f"toe1-1.{side}", f"toe1-2.{side}"):
                arr = np.array(w[b]).reshape(-1, 2)
                mask[arr[:, 0].astype(int)] += arr[:, 1]
            mask = np.clip(mask, 0, 1)
            pivot = d.joint_pos(V0, rig[f"toe1-1.{side}"]["head"])
            R = rz(-deg * sg)  # left toe swings toward the midline side
            V0[:] = V0 + mask[:, None] * ((V0 - pivot) @ R.T + pivot - V0)

    # ------------------------------------------- 2. Blender mesh + subdivide
    def _mesh(self, subdiv):
        d = self.data
        keep = np.zeros(d.n, dtype=bool)
        keep[d.groups["body"]] = True
        ids = np.nonzero(keep)[0]
        remap = -np.ones(d.n, dtype=np.int64)
        remap[ids] = np.arange(len(ids))
        fsel = [i for i, f in enumerate(d.faces) if all(keep[v] for v in f)]
        faces = [[int(remap[v]) for v in d.faces[i]] for i in fsel]
        fuv = [d.face_uvs[i] for i in fsel]
        Wfull, bones = d.weights(RIG)
        self.bones = bones
        obj = sc.make_mesh(self.spec["id"], self.V0[ids], faces, fuv, d.uv)
        Wl = Wfull[ids]
        for j, b in enumerate(bones):
            vg = obj.vertex_groups.new(name=b)
            col = Wl[:, j]
            for i in np.nonzero(col > 1e-4)[0]:
                vg.add([int(i)], float(col[i]), "REPLACE")
        me = obj.data
        if subdiv:
            hi, ni = bones.index("head"), bones.index("neck_01")
            for limit in (0.0105, 0.0085):
                bm = bmesh.new()
                bm.from_mesh(me)
                dl = bm.verts.layers.deform.verify()
                edges = set()
                for face in bm.faces:
                    if not all((v[dl].get(hi, 0) + v[dl].get(ni, 0)) > 0.35 for v in face.verts):
                        continue
                    if max(e.calc_length() for e in face.edges) > limit:
                        edges.update(face.edges)
                if edges:
                    bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, smooth=1.0,
                                              use_grid_fill=True, use_only_quads=False)
                bm.to_mesh(me)
                bm.free()
            me.update()
        n = len(me.vertices)
        V = np.empty(n * 3, dtype=np.float64)
        me.vertices.foreach_get("co", V)
        W = np.zeros((n, len(bones)))
        gi = {vg.index: bones.index(vg.name) for vg in obj.vertex_groups}
        for v in me.vertices:
            for ge in v.groups:
                W[v.index, gi[ge.group]] = ge.weight
        W /= W.sum(1, keepdims=True)
        self.obj, self.Vm, self.W = obj, V.reshape(n, 3), W
        ed = np.empty(len(me.edges) * 2, dtype=np.int32)
        me.edges.foreach_get("vertices", ed)
        self.edges = ed.reshape(-1, 2)
        self.log(f"  mesh: {len(ids)} -> {n} verts after head subdivision")

    # ---------------------------------------------------------- 3. head sculpt
    def _can(self, P):
        E = self.E
        return np.stack([P[:, 0] - E[0], -(P[:, 1] - E[1]), P[:, 2] - E[2]], axis=1) * 100.0

    def _uncan(self, C):
        E = self.E
        return np.stack([E[0] + C[:, 0] / 100, E[1] - C[:, 1] / 100, E[2] + C[:, 2] / 100], axis=1)

    def _sculpt(self):
        field = HeadField(**self.spec.get("head", {}))
        hi, ni = self.bones.index("head"), self.bones.index("neck_01")
        mask = sstep(0.05, 0.7, self.W[:, hi] + 0.55 * self.W[:, ni])
        C = self._can(self.Vm)
        self.Vs = self._uncan(C + field.displacement(C) * mask[:, None])
        hv = self.spec.get("hair_volume")
        if hv:
            from . import masks as M
            me = self.obj.data
            me.calc_loop_triangles()
            tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
            me.loop_triangles.foreach_get("vertices", tris)
            N = M.vertex_normals(self.Vs, tris.reshape(-1, 3))
            X, F, U = C[:, 0], C[:, 1], C[:, 2]
            keep = 1 - M.ear_zone(X, F, U)
            amt = hv.get("scalp", 0.0) * M.scalp(X, F, U, hv.get("hairline"), soft=3.2) * keep \
                + hv.get("beard", 0.0) * M.beard(X, F, U, soft=2.5) * keep
            self.Vs = self.Vs + N * (amt * mask / 100.0)[:, None]
        Ce = self._can(self.eyes0)
        self.eyes_s = self._uncan(Ce + field.displacement(Ce))
        L = np.array(list(LANDMARKS.values()), float)
        self.lm_s = dict(zip(LANDMARKS, self._uncan(L + field.displacement(L))))

    # ----------------------------------------------------------- 4. proportions
    def proportion(self, head_scale=1.0):
        spec = self.spec
        scales = _both(spec.get("scales", {}))
        li = spec.get("limbs", {})
        s_hum = li.get("humerus", 1.0)
        s_fem = s_hum * HUMAN_INDEX["humerofemoral"] / li.get("humerofemoral", HUMAN_INDEX["humerofemoral"])
        s_rad = s_hum * li.get("brachial", HUMAN_INDEX["brachial"]) / HUMAN_INDEX["brachial"]
        s_tib = s_fem * li.get("crural", HUMAN_INDEX["crural"]) / HUMAN_INDEX["crural"]
        for side in ("_l", "_r"):
            _mul(scales, "upperarm" + side, (1, s_hum, 1))
            _mul(scales, "lowerarm" + side, (1, s_rad, 1))
            _mul(scales, "thigh" + side, (1, s_fem, 1))
            _mul(scales, "calf" + side, (1, s_tib, 1))
            fs = spec.get("finger_scale", 1.0)
            ts = spec.get("thumb_scale", 1.0)
            for i in (1, 2, 3):
                for fname in FINGERS:
                    _mul(scales, f"{fname}_0{i}{side}", (1, fs, 1))
                _mul(scales, f"thumb_0{i}{side}", (1, ts, 1))
        _mul(scales, "head", (head_scale,) * 3)
        self.skel = self.skel0.copy()
        extra = {"eyeL": ("head", self.eyes_s[0]), "eyeR": ("head", self.eyes_s[1])}
        extra.update({f"lm_{k}": ("head", v) for k, v in self.lm_s.items()})
        self.V, ex = self.skel.reshape(self.Vs, self.W, self.bones, scales, extra)
        self.points = {k: (extra[k][0], v) for k, v in ex.items()}
        self.head_scale = head_scale
        self.eye_r = self.eye_r0 * head_scale * spec.get("eye_scale", 1.0)
        self.scale = 1.0
        self.head_rot = np.eye(3)

    # ------------------------------------------------------------- 5. stance
    def _bake(self, rots, root_shift=(0, 0, 0)):
        extra = {k: (b, v) for k, (b, v) in self.points.items()}
        self.V, ex = self.skel.bake_pose(self.V, self.W, self.bones, rots, root_shift, extra_points=extra)
        self.points = {k: (extra[k][0], v[0]) for k, v in ex.items()}
        self.head_rot = ex["eyeL"][1] @ self.head_rot

    def _ground_scale(self, k):
        s = self.skel
        zmin = self.V[:, 2].min()
        foot = 0.5 * (s.head[s.idx["foot_l"]] + s.head[s.idx["foot_r"]])
        x0 = 0.5 * (self.V[:, 0].min() + self.V[:, 0].max()) * 0.0
        t = -np.array([x0, foot[1], zmin]) * k
        self.V = self.V * k + t
        s.head = s.head * k + t
        s.tail = s.tail * k + t
        self.points = {key: (b, v * k + t) for key, (b, v) in self.points.items()}
        self.eye_r *= k
        self.scale *= k

    def stand_biped(self):
        st = self.spec.get("stance", {})
        s = self.skel
        rots = {}
        arm_angle = st.get("arm_angle", 11.0)
        for side, sg in (("_l", 1.0), ("_r", -1.0)):
            hip, ank = s.head[s.idx["thigh" + side]], s.head[s.idx["foot" + side]]
            leg = ank - hip
            gap = st.get("foot_gap", abs(hip[0]) * 0.92)
            cur = np.degrees(np.arctan2(abs(ank[0]) - abs(hip[0]), -leg[2]))
            want = np.degrees(np.arctan2(gap - abs(hip[0]), -leg[2]))
            a = (cur - want) * sg
            rots["thigh" + side] = ry(a)
            rots["foot" + side] = ry(-a)
            ua = s.tail[s.idx["upperarm" + side]] - s.head[s.idx["upperarm" + side]]
            la = s.tail[s.idx["lowerarm" + side]] - s.head[s.idx["lowerarm" + side]]
            cur = np.degrees(np.arctan2(abs(ua[0]), -ua[2]))
            rots["clavicle" + side] = ry(4.0 * sg)
            rots["upperarm" + side] = ry((cur - arm_angle - 4.0) * sg) @ rx(st.get("arm_back", 4.0))
            ax = np.cross(ua, la)
            ax /= np.linalg.norm(ax)
            rots["lowerarm" + side] = rot(ax, -st.get("elbow_extend", 30.0))
            # relaxed finger curl (hinge = finger direction x palm normal)
            I = s.idx
            w0 = s.head[I["hand" + side]]
            n = np.cross(s.head[I["index_01" + side]] - w0, s.head[I["pinky_01" + side]] - w0)
            n /= np.linalg.norm(n)
            if n[2] > 0:            # in the A-pose the palms face the ground
                n = -n
            curl = st.get("finger_curl", 1.0)
            for fname, degs in (("index", (9, 14, 9)), ("middle", (13, 18, 11)),
                                ("ring", (17, 22, 13)), ("pinky", (21, 24, 15)), ("thumb", (4, 8, 8))):
                for j, deg in enumerate(degs, start=1):
                    b = f"{fname}_0{j}{side}"
                    d = s.tail[I[b]] - s.head[I[b]]
                    h = np.cross(d, n)
                    rots[b] = rot(h, deg * curl)
        for b, deg in st.get("pitch", {}).items():   # e.g. head carriage, spine curvature
            rots[b] = rx(deg) @ rots[b] if b in rots else rx(deg)
        self._bake(rots)

    def fit(self, iterations=3):
        """Proportion + stance, iterating head scale so the absolute head
        length (glabella-opisthocranion, incl. soft tissue) hits its target."""
        spec = self.spec
        hs = spec.get("head_scale", 1.0)
        for _ in range(iterations):
            self.proportion(hs)
            if spec.get("stance", {}).get("kind", "biped") == "biped":
                self.stand_biped()
                height = self.V[:, 2].max() - self.V[:, 2].min()
                self._ground_scale(spec["stature"] / height)
                self.V_stance = self.V.copy()
            else:
                from .quadruped import stand_quadruped
                # scale is defined on the upright body, then the animal is put on all fours
                self.stand_biped()
                height = self.V[:, 2].max() - self.V[:, 2].min()
                self._ground_scale(spec["stature"] / height)
                self.V_stance = self.V.copy()
                stand_quadruped(self)
                self._ground_scale(1.0)
            target = spec.get("head_length")
            if not target:
                break
            m = self.measure()
            hs *= target / m["head_length"]
        self.relax()
        return self

    def relax(self):
        """Smooth away pinches that linear-blend skinning leaves when a stance
        is baked in (the nape of the four-legged apes above all), and the
        faint terracing that subdivision leaves on the vault."""
        from scipy.sparse import coo_matrix
        from . import masks as M
        from .sculpt import above_base
        n = len(self.V)
        e = self.edges
        A = coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
        deg = np.asarray(A.sum(1)).ravel()
        deg[deg == 0] = 1
        C = self._can(self.Vm)
        X, F, U = C[:, 0], C[:, 1], C[:, 2]
        ear = M.ear_zone(X, F, U)
        quad = self.spec.get("stance", {}).get("kind") == "quadruped"
        nape = sstep(-6.0, -9.5, F) * sstep(4.0, 1.0, U) * sstep(-21.0, -15.0, U) * (1 - ear)
        vault = sstep(0.5, 2.5, above_base(F, U)) * (1 - ear) * np.maximum(sstep(3.4, 4.8, U), sstep(-2.0, -5.0, F)) * (U > -17.0)
        for mask, iters in ((nape, 40 if quad else 8), (vault, 5)):
            m = (mask * 0.6)[:, None]
            if not m.any():
                continue
            for _ in range(iters):
                avg = (A @ self.V) / deg[:, None]
                self.V = self.V + m * (avg - self.V)

    def measure(self):
        s = self.skel
        L = s.length
        hum, rad, fem, tib = L("upperarm_l"), L("lowerarm_l"), L("thigh_l"), L("calf_l")
        p = {k[3:]: v for k, (b, v) in self.points.items() if k.startswith("lm_")}
        return dict(
            stature=float(self.V[:, 2].max() - self.V[:, 2].min()),
            humerus=hum, radius=rad, femur=fem, tibia=tib,
            intermembral=100 * (hum + rad) / (fem + tib),
            humerofemoral=100 * hum / fem, brachial=100 * rad / hum, crural=100 * tib / fem,
            head_length=float(np.linalg.norm(p["glabella"] - p["opisthocranion"])),
            head_breadth=float(np.linalg.norm(p["eu_l"] - p["eu_r"])),
            head_height=float(np.linalg.norm(p["vertex"] - p["porion"])),
            biacromial=float(np.linalg.norm(s.head[s.idx["upperarm_l"]] - s.head[s.idx["upperarm_r"]])),
            hip_breadth=float(np.linalg.norm(s.head[s.idx["thigh_l"]] - s.head[s.idx["thigh_r"]])),
            head_scale=self.head_scale, scale=self.scale,
        )

    def commit(self):
        me = self.obj.data
        me.vertices.foreach_set("co", self.V.reshape(-1))
        me.update()
        return self.obj

    def rig(self, extra_objs=()):
        """Create the armature in the current rest stance and bind the mesh
        (4 influences per vertex, the glTF default) plus rigid head parts."""
        self.commit()
        arm = sc.make_armature("Armature", self.skel.as_dict())
        ob = self.obj
        ob.vertex_groups.clear()
        Wl = self.W.copy()
        order = np.argsort(-Wl, axis=1)
        keepm = np.zeros_like(Wl, dtype=bool)
        np.put_along_axis(keepm, order[:, :4], True, axis=1)
        Wl[~keepm] = 0.0
        Wl /= Wl.sum(1, keepdims=True)
        for j, b in enumerate(self.bones):
            col = Wl[:, j]
            nz = np.nonzero(col > 1e-4)[0]
            if not len(nz):
                continue
            vg = ob.vertex_groups.new(name=b)
            for i in nz:
                vg.add([int(i)], float(col[i]), "REPLACE")
        for o in (ob, *extra_objs):
            if o is not ob and not len(o.vertex_groups):      # rigid head parts (eyes)
                vg = o.vertex_groups.new(name="head")
                vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
            mod = o.modifiers.new("Armature", "ARMATURE")
            mod.object = arm
            o.parent = arm
        self.arm = arm
        # Blender's own rest matrices are the reference for pose quaternions
        self.rest = np.stack([np.array(arm.data.bones[b].matrix_local.to_3x3()) for b in self.skel.names])
        return arm

    def point(self, name):
        return self.points[name][1]
