"""Four-legged stance and gait for the Miocene apes.

The trunk angle is not chosen by hand: it is solved so that hands and feet
both reach the ground, so posture follows from the limb proportions (long
arms -> sloping back, as in living great apes).
"""
import numpy as np

from .anim import Rig, smooth, lerp, TAU
from .body import rot, rx, ry, rz, FRONT, UP

SIDES = (("_l", 1.0), ("_r", -1.0))
CURL = {"index": (9, 14, 9), "middle": (13, 18, 11), "ring": (17, 22, 13), "pinky": (21, 24, 15), "thumb": (4, 8, 8)}


def _palm_frame(s, side, sg):
    """(direction, palm normal) of the hand in the current rest pose."""
    I = s.idx
    w = s.head[I["hand" + side]]
    kn = 0.5 * (s.head[I["index_01" + side]] + s.head[I["pinky_01" + side]])
    d = kn - w
    d /= np.linalg.norm(d)
    n = np.cross(s.head[I["index_01" + side]] - w, s.head[I["pinky_01" + side]] - w)
    n /= np.linalg.norm(n)
    if n[0] * sg > 0:            # standing with arms down, palms face the thighs
        n = -n
    n = n - np.dot(n, d) * d
    n /= np.linalg.norm(n)
    return d, n


def _frame(d, n):
    return np.stack([d, n, np.cross(d, n)], axis=1)


def _pose(body, pitch, st, legs=None, arms=None, extra=None):
    """Build the quadrupedal pose for a given trunk pitch (deg from vertical).
    legs / arms: optional per-side overrides {side: dict(target=, pitch=)}."""
    s = body.skel
    I = s.idx
    r = Rig(s)
    leg = np.linalg.norm(s.head[I["calf_l"]] - s.head[I["thigh_l"]]) + np.linalg.norm(s.head[I["foot_l"]] - s.head[I["calf_l"]])
    hip_h = st.get("hip_height", 0.84) * leg + s.head[I["foot_l"]][2]
    curve = st.get("spine_curve", 0.22)
    r.rots["pelvis"] = rx(pitch * (1 - curve))
    for b in ("spine_01", "spine_02", "spine_03"):
        r.rots[b] = rx(pitch * curve / 3.0)
    hip0 = s.head[I["thigh_l"]][2]
    # put the hips at the chosen height
    _, Pth = r.world("thigh_l")
    r.shifts["pelvis"] = np.array([0.0, 0.0, hip_h - Pth[2]])
    if extra:
        extra(r)
    out = {}
    for side, sg in SIDES:
        hip = r.world("thigh" + side)[1]
        a0 = s.head[I["foot" + side]]
        tgt = np.array([hip[0] * st.get("foot_spread", 1.15), hip[1] - st.get("foot_fwd", 0.10) * leg, a0[2]])
        fp = 0.0
        if legs and side in legs:
            tgt = legs[side].get("target", tgt)
            fp = legs[side].get("pitch", 0.0)
        r.ik("thigh" + side, "calf" + side, "foot" + side, tgt, pole=FRONT + np.array([0.35 * sg, 0, 0.1]))
        r.set_world_rot("foot" + side, rz(-st.get("toe_out", 14.0) * sg) @ rx(fp))
        r.set_world_rot("ball" + side, rz(-st.get("toe_out", 14.0) * sg) @ rx(min(fp, 0.0)))
        out["foot" + side] = tgt

        sh = r.world("upperarm" + side)[1]
        d0, n0 = _palm_frame(s, side, sg)
        knuckle = np.linalg.norm(0.5 * (s.head[I["index_01" + side]] + s.head[I["pinky_01" + side]]) - s.head[I["hand" + side]])
        wrist_h = st.get("wrist_height", 0.32) * knuckle
        wt = np.array([sh[0] * st.get("hand_spread", 1.02), sh[1] - st.get("hand_fwd", 0.03), wrist_h])
        hp = 0.0
        if arms and side in arms:
            wt = arms[side].get("target", wt)
            hp = arms[side].get("pitch", 0.0)
        r.ik("upperarm" + side, "lowerarm" + side, "hand" + side, wt, pole=-FRONT + np.array([0.45 * sg, 0, 0.0]))
        d1 = rz(-st.get("hand_out", 12.0) * sg) @ rx(hp + 4.0) @ FRONT
        n1 = rx(hp + 4.0) @ np.array([0.0, 0.0, -1.0])
        n1 = n1 - np.dot(n1, d1) * d1
        n1 /= np.linalg.norm(n1)
        r.set_world_rot("hand" + side, _frame(d1, n1) @ _frame(d0, n0).T)
        # open the fingers so they lie on the ground (undo most of the relaxed curl)
        open_amt = st.get("finger_open", 0.85) if hp <= 1 else st.get("finger_open", 0.85) * 0.3
        for fname, degs in CURL.items():
            for j, deg in enumerate(degs, start=1):
                b = f"{fname}_0{j}{side}"
                d = s.tail[I[b]] - s.head[I[b]]
                r.rots[b] = rot(np.cross(d, n0), -deg * open_amt)
        out["hand" + side] = wt
        out["shoulder" + side] = sh
    # head looks ahead; the neck takes up the difference
    look = st.get("head_pitch", 14.0)
    hx = extra.__dict__.get("head", (0.0, 0.0)) if extra and hasattr(extra, "__dict__") else (0.0, 0.0)
    r.set_world_rot("neck_01", rx(pitch * st.get("neck_share", 0.5)))
    r.set_world_rot("head", rz(hx[0]) @ rx(look + hx[1]))
    return r, out


def solve_pitch(body, st):
    """Trunk pitch at which the arms reach the ground at ~`arm_reach` of full length."""
    s = body.skel
    I = s.idx
    arm = np.linalg.norm(s.head[I["lowerarm_l"]] - s.head[I["upperarm_l"]]) + np.linalg.norm(s.head[I["hand_l"]] - s.head[I["lowerarm_l"]])
    want = st.get("arm_reach", 0.955) * arm
    lo, hi = 25.0, 100.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        r, out = _pose(body, mid, st)
        dist = np.linalg.norm(out["shoulder_l"] - out["hand_l"])
        if dist > want:      # shoulder too high -> lean further
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def stand_quadruped(body):
    st = body.spec.get("stance", {})
    pitch = st.get("trunk_pitch") or solve_pitch(body, st)
    body.trunk_pitch = pitch
    r, _ = _pose(body, pitch, st)
    rots, shifts = r.pose()
    # bake_pose only takes a root shift: fold the pelvis shift into the vertices via Root
    s = body.skel
    extra = {k: (b, v) for k, (b, v) in body.points.items()}
    body.V, ex = _bake_with_shifts(body, rots, shifts, extra)
    body.points = {k: (extra[k][0], v[0]) for k, v in ex.items()}
    body.head_rot = ex["eyeL"][1] @ body.head_rot
    # centre the animal between its hands and feet
    I = s.idx
    cy = np.mean([s.head[I[b]][1] for b in ("foot_l", "foot_r", "hand_l", "hand_r")])
    body.V[:, 1] -= cy
    s.head[:, 1] -= cy
    s.tail[:, 1] -= cy
    body.points = {k: (b, v - np.array([0, cy, 0])) for k, (b, v) in body.points.items()}


def _bake_with_shifts(body, rots, shifts, extra):
    """Like Skeleton.bake_pose but honouring per-bone head shifts."""
    s = body.skel
    n = len(s.names)
    G = np.zeros((n, 3, 3))
    P = np.zeros((n, 3))
    for i, b in enumerate(s.names):
        D = rots.get(b, np.eye(3))
        p = s.parent[i]
        if p < 0:
            G[i] = D
            P[i] = s.head[i] + shifts.get(b, 0)
        else:
            G[i] = G[p] @ D
            P[i] = P[p] + G[p] @ (s.head[i] - s.head[p]) + shifts.get(b, 0)
    c = np.array([P[i] - G[i] @ s.head[i] for i in range(n)])
    Vn = s._apply(body.V, body.W, body.bones, G, c)
    ex = {k: (G[s.idx[b]] @ p + c[s.idx[b]], G[s.idx[b]]) for k, (b, p) in extra.items()}
    s.tail = np.array([P[i] + G[i] @ (s.tail[i] - s.head[i]) for i in range(n)])
    s.zref = np.array([G[i] @ s.zref[i] for i in range(n)])
    s.head = P
    return Vn, ex


# ---------------------------------------------------------------- animation
def _limb_rest(s):
    I = s.idx
    return {b: s.head[I[b]].copy() for b in ("foot_l", "foot_r", "hand_l", "hand_r")}


def _anim_pose(body, legs, arms, pelvis_shift, pelvis_rot, chest_rot, head, st):
    """Pose relative to the quadrupedal rest stance, limbs placed by IK."""
    s = body.skel
    I = s.idx
    r = Rig(s)
    r.shifts["pelvis"] = np.asarray(pelvis_shift, float)
    r.rots["pelvis"] = pelvis_rot
    r.rots["spine_02"] = chest_rot
    for side, sg in SIDES:
        tgt, fp = legs[side]
        r.ik("thigh" + side, "calf" + side, "foot" + side, tgt, pole=FRONT + np.array([0.35 * sg, 0, 0.1]))
        r.set_world_rot("foot" + side, rx(fp))
        r.set_world_rot("ball" + side, rx(min(fp, 0.0)) if fp < 30 else rx(fp - 30))
        wt, hp = arms[side]
        r.ik("upperarm" + side, "lowerarm" + side, "hand" + side, wt, pole=-FRONT + np.array([0.45 * sg, 0, 0.0]))
        r.set_world_rot("hand" + side, rx(hp))
        if hp > 1:                       # fingers relax and curl a little while the hand is in the air
            n0 = _palm_frame(s, side, sg)[1]
            for fname, degs in CURL.items():
                for j, deg in enumerate(degs, start=1):
                    b = f"{fname}_0{j}{side}"
                    d = s.tail[I[b]] - s.head[I[b]]
                    r.rots[b] = rot(np.cross(d, n0), deg * 0.9 * min(hp / 30.0, 1.0))
    r.set_world_rot("neck_01", rz(head[0] * 0.4) @ rx(head[1] * 0.4))
    r.set_world_rot("head", rz(head[0]) @ rx(head[1]))
    return r.pose()


def quad_walk(body, n=36, stride_rel=0.62, lift_rel=0.16):
    """Diagonal-sequence walk (the footfall order typical of primates):
    left hind, right fore, right hind, left fore."""
    s = body.skel
    I = s.idx
    st = body.spec.get("stance", {})
    rest = _limb_rest(s)
    leg = np.linalg.norm(s.head[I["calf_l"]] - s.head[I["thigh_l"]]) + np.linalg.norm(s.head[I["foot_l"]] - s.head[I["calf_l"]])
    L = stride_rel * leg * 2.0
    duty = 0.64
    reach = duty * L / 2
    phase = {"foot_l": 0.0, "hand_r": 0.2, "foot_r": 0.5, "hand_l": 0.7}
    poses = []
    for k in range(n):
        ph = k / n
        tg = {}
        for limb, off in phase.items():
            p = (ph - off) % 1.0
            base = rest[limb]
            if p < duty:
                u = p / duty
                y = base[1] - reach + 2 * reach * u
                z = base[2]
                pitch = 0.0
                if limb.startswith("foot") and u > 0.7:
                    pitch = lerp(0.0, 32.0, smooth((u - 0.7) / 0.3))
                    z += 0.03 * leg * smooth((u - 0.7) / 0.3)
            else:
                u = (p - duty) / (1 - duty)
                y = base[1] + reach - 2 * reach * smooth(u)
                z = base[2] + lift_rel * leg * np.sin(np.pi * u) ** 1.2 * (1.0 if limb.startswith("foot") else 0.85)
                pitch = (32.0 * (1 - smooth(min(u * 1.6, 1.0)))) if limb.startswith("foot") else 38.0 * np.sin(np.pi * u)
            tg[limb] = (np.array([base[0], y, z]), pitch)
        bob = 0.012 * leg * np.cos(2 * TAU * ph)
        yaw = 4.0 * np.sin(TAU * ph)
        roll = 2.5 * np.sin(TAU * ph + 0.6)
        poses.append(_anim_pose(
            body,
            legs={"_l": tg["foot_l"], "_r": tg["foot_r"]},
            arms={"_l": tg["hand_l"], "_r": tg["hand_r"]},
            pelvis_shift=(0.012 * leg * np.sin(TAU * ph), 0.0, bob - 0.01 * leg),
            pelvis_rot=rz(yaw) @ ry(roll),
            chest_rot=rz(-yaw * 1.6) @ ry(-roll * 1.3),
            head=(3.0 * np.sin(TAU * ph + 1.0), 2.0 * np.sin(2 * TAU * ph)),
            st=st))
    return poses


def quad_idle(body, n=120):
    s = body.skel
    rest = _limb_rest(s)
    st = body.spec.get("stance", {})
    poses = []
    for k in range(n):
        t = k / n
        br = np.sin(TAU * t * 2)
        sh = np.sin(TAU * t)
        look = np.sin(TAU * t + 0.7)
        poses.append(_anim_pose(
            body,
            legs={sd: (rest["foot" + sd], 0.0) for sd, _ in SIDES},
            arms={sd: (rest["hand" + sd], 0.0) for sd, _ in SIDES},
            pelvis_shift=(0.01 * sh, 0.0, -0.006 - 0.003 * br),
            pelvis_rot=ry(-1.2 * sh) @ rx(0.6 * br),
            chest_rot=rx(-1.2 * br) @ ry(1.0 * sh),
            head=(16.0 * look, 5.0 * np.sin(TAU * t * 2 + 0.4) - 2.0),
            st=st))
    return poses
