"""Procedural animation: poses are solved in numpy (FK + two-bone IK) and
written to Blender actions as local quaternions.

A pose is (rots, shifts): `rots` are character-space delta rotations carried
by the parent (see body.py), `shifts` are world-space translations of a bone
head (used for the pelvis).
"""
import bpy
import numpy as np

from .body import rot, rot_between, rx, ry, rz, solve_two_bone, mat_to_quat, FRONT, UP

TAU = 2 * np.pi


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


class Rig:
    """FK helper that lets poses be built joint by joint."""

    def __init__(self, skel):
        self.s = skel
        self.rots, self.shifts = {}, {}
        self.G = {}
        self.P = {}

    def _solve(self, bone):
        s = self.s
        i = s.idx[bone]
        p = s.parent[i]
        if p < 0:
            G = self.rots.get(bone, np.eye(3))
            P = s.head[i] + self.shifts.get(bone, 0)
        else:
            pb = s.names[p]
            Gp, Pp = self.world(pb)
            G = Gp @ self.rots.get(bone, np.eye(3))
            P = Pp + Gp @ (s.head[i] - s.head[p]) + self.shifts.get(bone, 0)
        return G, P

    def world(self, bone):
        """(G, P) for a bone given the rotations set so far (not cached past
        mutation: call after parents are final)."""
        return self._solve(bone)

    def set_world_rot(self, bone, G):
        """Set a bone's world delta rotation directly."""
        s = self.s
        p = s.parent[s.idx[bone]]
        Gp = self.world(s.names[p])[0] if p >= 0 else np.eye(3)
        self.rots[bone] = Gp.T @ G

    def aim(self, bone, direction, twist_ref=None):
        """Rotate `bone` (minimal rotation from its parent-carried rest
        direction) so it points along `direction`."""
        s = self.s
        i = s.idx[bone]
        p = s.parent[i]
        Gp = self.world(s.names[p])[0] if p >= 0 else np.eye(3)
        rest = s.tail[i] - s.head[i]
        cur = Gp @ rest
        G = rot_between(cur, direction) @ Gp
        self.rots[bone] = Gp.T @ G
        return G

    def tail(self, bone):
        s = self.s
        i = s.idx[bone]
        G, P = self.world(bone)
        return P + G @ (s.tail[i] - s.head[i])

    def ik(self, upper, lower, end, target, pole):
        """Two-bone IK: place the head of `end` at `target`."""
        s = self.s
        root = self.world(upper)[1]
        l1 = np.linalg.norm(s.head[s.idx[lower]] - s.head[s.idx[upper]])
        l2 = np.linalg.norm(s.head[s.idx[end]] - s.head[s.idx[lower]])
        mid, tgt = solve_two_bone(root, np.asarray(target, float), l1, l2, np.asarray(pole, float))
        # the bones' own tails may not coincide exactly with the child joint; aim joint-to-joint
        self._aim_joint(upper, lower, mid - root)
        self._aim_joint(lower, end, tgt - mid)

    def _aim_joint(self, bone, child, direction):
        s = self.s
        i = s.idx[bone]
        p = s.parent[i]
        Gp = self.world(s.names[p])[0] if p >= 0 else np.eye(3)
        rest = s.head[s.idx[child]] - s.head[i]
        G = rot_between(Gp @ rest, direction) @ Gp
        self.rots[bone] = Gp.T @ G

    def pose(self):
        return dict(self.rots), dict(self.shifts)


# ------------------------------------------------------------------ bipeds
def biped_walk(body, n=32, stride_rel=0.74, lift_rel=0.085, arm_swing=22.0, bob_rel=0.022,
               knee_bias=0.006, lean=4.0, sway=0.014, crouch=0.0):
    """In-place walking cycle.  Returns a list of n poses.

    stride_rel  stride length / stature          lift_rel  swing foot lift / leg length
    crouch      extra hip drop / leg length (bent-hip, bent-knee gaits)
    """
    s = body.skel
    I = s.idx
    stature = body.V[:, 2].max()
    hipL, hipR = s.head[I["thigh_l"]], s.head[I["thigh_r"]]
    ank = {sd: s.head[I["foot" + sd]].copy() for sd in ("_l", "_r")}
    ball = {sd: s.head[I["ball" + sd]].copy() for sd in ("_l", "_r")}
    pel0 = s.head[I["pelvis"]].copy()
    leg = np.linalg.norm(s.head[I["calf_l"]] - hipL) + np.linalg.norm(ank["_l"] - s.head[I["calf_l"]])
    L = stride_rel * stature
    duty = 0.62
    reach = duty * L / 2
    shift = 0.042 * stature        # the foot lands nearer the body than it leaves it
    # heel = point under the ankle on the ground, slightly behind
    heel_off = {sd: np.array([0.0, 0.035 * stature / 1.7, -ank[sd][2]]) for sd in ("_l", "_r")}
    hip_h = hipL[2] - ank["_l"][2]
    drop0 = hip_h - np.sqrt(max((0.992 * leg) ** 2 - (reach - shift) ** 2, 1e-6))
    drop0 = max(drop0, 0.0) + crouch * leg
    poses = []
    for k in range(n):
        ph = k / n
        r = Rig(s)
        bob = bob_rel * leg * 0.5 * (1 - np.cos(2 * TAU * ph))       # high at mid-stance
        side = np.sin(TAU * ph + 0.5 * np.pi * 0) * 0.0
        # left foot strikes at ph=0, right at 0.5 -> weight over left around 0.25
        lat = sway * stature * np.sin(TAU * (ph - 0.0)) * 1.0
        r.shifts["pelvis"] = np.array([lat, 0.0, -drop0 - knee_bias * leg + bob])
        yaw = 5.0 * np.cos(TAU * ph)            # left hip forward at left heel strike
        roll = 3.0 * np.sin(TAU * ph)           # pelvis drops on the swing side
        r.rots["pelvis"] = rz(-yaw) @ ry(roll) @ rx(lean * 0.4)
        r.rots["spine_01"] = rz(yaw * 0.5) @ ry(-roll * 0.5) @ rx(lean * 0.3)
        r.rots["spine_02"] = rz(yaw * 0.7) @ ry(-roll * 0.4) @ rx(lean * 0.3)
        r.rots["spine_03"] = rz(yaw * 0.6) @ ry(-roll * 0.1)
        r.rots["neck_01"] = rz(-yaw * 0.4) @ rx(-lean * 0.5)
        r.rots["head"] = rz(-yaw * 0.4) @ rx(-lean * 0.5)
        for sd, off, sg in (("_l", 0.0, 1.0), ("_r", 0.5, -1.0)):
            p = (ph - off) % 1.0
            a0, b0 = ank[sd], ball[sd]
            if p < duty:                                   # stance
                u = p / duty
                gy = b0[1] - reach + shift + 2 * reach * u  # ball on the ground, moving back
                gz = b0[2]
                if u < 0.16:                               # heel strike -> foot flat
                    pitch = lerp(-14.0, 0.0, smooth(u / 0.16))
                    piv = np.array([b0[0], gy + (a0[1] - b0[1]) + heel_off[sd][1], 0.0])   # heel
                    rel = a0 - np.array([a0[0], a0[1] + heel_off[sd][1], 0.0])
                    apos = piv + rx(pitch) @ rel
                elif u < 0.62:
                    pitch = 0.0
                    apos = np.array([a0[0], gy + (a0[1] - b0[1]), a0[2]])
                else:                                      # heel-off: roll over the ball
                    pitch = lerp(0.0, 46.0, smooth((u - 0.62) / 0.38))
                    piv = np.array([b0[0], gy, gz])
                    apos = piv + rx(pitch) @ (a0 - b0)
                toe = pitch if pitch > 0 else 0.0
            else:                                          # swing
                u = (p - duty) / (1 - duty)
                piv = np.array([b0[0], b0[1] + reach + shift, b0[2]])
                start = piv + rx(46.0) @ (a0 - b0)
                pivh = np.array([b0[0], b0[1] - reach + shift + (a0[1] - b0[1]) + heel_off[sd][1], 0.0])
                relh = a0 - np.array([a0[0], a0[1] + heel_off[sd][1], 0.0])
                stop = pivh + rx(-14.0) @ relh
                e = smooth(u)
                apos = lerp(start, stop, e)
                apos[2] += lift_rel * leg * np.sin(np.pi * u) ** 1.3
                pitch = lerp(46.0, -14.0, smooth(min(u * 1.25, 1.0)))
                toe = max(0.0, 46.0 * (1 - u * 4))
            # narrow the track slightly toward the midline like a real walk
            apos = apos.copy()
            apos[0] = a0[0] * 0.86
            r.ik("thigh" + sd, "calf" + sd, "foot" + sd, apos, pole=FRONT + np.array([0.12 * sg, 0, 0]))
            r.set_world_rot("foot" + sd, rx(pitch))
            r.set_world_rot("ball" + sd, rx(pitch - toe))
            # arms swing opposite to the leg on the same side
            sw = arm_swing * np.cos(TAU * p)               # forward when this leg is back
            r.rots["clavicle" + sd] = rz(-yaw * 0.2)
            r.rots["upperarm" + sd] = rx(sw * 0.9 + 2.0)
            r.rots["lowerarm" + sd] = rx(-(3.0 + 13.0 * (0.5 + 0.5 * np.cos(TAU * p + 0.5))))
        poses.append(r.pose())
    return poses


def biped_idle(body, n=120, sway=1.0):
    """Standing: breathing, weight shift, slow look-around."""
    s = body.skel
    poses = []
    for k in range(n):
        t = k / n
        r = Rig(s)
        br = np.sin(TAU * t * 2)                      # two breaths per loop
        sh = np.sin(TAU * t)                          # one weight shift
        look = np.sin(TAU * t + 0.8)
        nod = np.sin(TAU * t * 2 + 0.3)
        hipL = s.head[s.idx["thigh_l"]]
        ank = {sd: s.head[s.idx["foot" + sd]].copy() for sd in ("_l", "_r")}
        r.shifts["pelvis"] = np.array([0.012 * sway * sh, 0.0, -0.004 - 0.002 * br])
        r.rots["pelvis"] = ry(-1.6 * sway * sh) @ rz(1.0 * look)
        r.rots["spine_01"] = ry(1.0 * sway * sh) @ rx(0.5 * br)
        r.rots["spine_02"] = ry(0.8 * sway * sh) @ rx(-0.9 * br)
        r.rots["spine_03"] = rx(-1.1 * br) @ rz(1.5 * look)
        r.rots["neck_01"] = rz(5.0 * look) @ rx(1.2 * nod)
        r.rots["head"] = rz(7.0 * look) @ rx(1.5 * nod + 0.6 * br)
        for sd, sg in (("_l", 1.0), ("_r", -1.0)):
            r.ik("thigh" + sd, "calf" + sd, "foot" + sd, ank[sd], pole=FRONT + np.array([0.1 * sg, 0, 0]))
            r.set_world_rot("foot" + sd, np.eye(3))
            r.rots["clavicle" + sd] = ry(-0.9 * br * sg)
            r.rots["upperarm" + sd] = rx(1.5 * sh * sg + 0.8 * br) @ ry(0.8 * br * sg)
            r.rots["lowerarm" + sd] = rx(-2.0 - 1.5 * np.sin(TAU * t + sg))
        poses.append(r.pose())
    return poses


# ------------------------------------------------------------- to Blender
def write_action(arm_obj, skel, name, poses, fps=30, loop=True, rest=None):
    """Create an action from poses and stash it on an NLA track named `name`.
    `rest` = Blender rest orientations (Body.rest); defaults to skel.frames()."""
    B = rest if rest is not None else skel.frames()
    frames = list(poses) + ([poses[0]] if loop else [])
    nfr = len(frames)
    quats = {b: np.zeros((nfr, 4)) for b in skel.names}
    locs = {}
    for f, (rots, shifts) in enumerate(frames):
        # world delta rotations of parents are needed to localise shifts
        G = {}
        for i, b in enumerate(skel.names):
            p = skel.parent[i]
            D = rots.get(b, np.eye(3))
            G[b] = D if p < 0 else G[skel.names[p]] @ D
            Bi = B[i]
            q = mat_to_quat(Bi.T @ D @ Bi)
            if f > 0 and np.dot(q, quats[b][f - 1]) < 0:
                q = -q
            quats[b][f] = q
            if b in shifts:
                Gp = np.eye(3) if p < 0 else G[skel.names[p]]
                locs.setdefault(b, np.zeros((nfr, 3)))[f] = Bi.T @ Gp.T @ np.asarray(shifts[b], float)
    action = bpy.data.actions.new(name)
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action
    slot = None
    try:
        slot = action.slots.new(id_type="OBJECT", name=arm_obj.name)
        layer = action.layers.new("Layer")
        strip = layer.strips.new(type="KEYFRAME")
        bag = strip.channelbag(slot, ensure=True)
        fcurves = bag.fcurves
        arm_obj.animation_data.action_slot = slot
    except Exception:
        fcurves = action.fcurves
    times = np.arange(nfr, dtype=np.float64)

    def curve(path, idx, values):
        fc = fcurves.new(data_path=path, index=idx)
        fc.keyframe_points.add(nfr)
        co = np.empty(nfr * 2)
        co[0::2] = times
        co[1::2] = values
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.update()

    for b in skel.names:
        q = quats[b]
        if np.allclose(q, q[0]) and np.allclose(q[0], [1, 0, 0, 0], atol=1e-6):
            continue
        for c in range(4):
            curve(f'pose.bones["{b}"].rotation_quaternion', c, q[:, c])
    for b, L in locs.items():
        for c in range(3):
            curve(f'pose.bones["{b}"].location', c, L[:, c])
    # stash on its own NLA track so the exporter writes one glTF animation each
    ad = arm_obj.animation_data
    track = ad.nla_tracks.new()
    track.name = name
    st = track.strips.new(name, 0, action)
    try:
        if slot is not None:
            st.action_slot = slot
    except Exception:
        pass
    ad.action = None
    return action
