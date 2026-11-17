"""Skeleton maths in numpy: bone frames, proportional reshaping, posing.

Conventions (Blender world): metres, Z up, character faces -Y, left is +X.

Rotations given to `pose()` are *character-space deltas carried by the
parent*: a knee flexion is simply "rotate about the lateral axis", whatever
the thigh is doing.  For a bone with rest orientation B the matching Blender
pose quaternion is  B^T . D . B  (see `local_quat`).
"""
import numpy as np

FRONT = np.array([0.0, -1.0, 0.0])
UP = np.array([0.0, 0.0, 1.0])
LEFT = np.array([1.0, 0.0, 0.0])


def rot(axis, deg):
    """Rotation matrix about `axis` (right-handed), angle in degrees."""
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    x, y, z = a
    return np.array([
        [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
    ])


def rx(deg):
    """About the lateral axis.  +deg tips the top of an upright segment forward;
    for a limb hanging down, +deg swings its far end backward (extension) and
    -deg swings it forward (flexion).  Knee flexion is +, elbow flexion is -."""
    return rot(LEFT, deg)


def ry(deg):
    """About the fore-aft axis.  +deg swings the far end of a hanging LEFT limb
    toward the midline (adduction); use -deg for the right side."""
    return rot([0, 1, 0], deg)


def rz(deg):
    """About the vertical axis (+deg turns the character toward its left)."""
    return rot(UP, deg)


def mat_to_quat(m):
    """3x3 rotation -> (w, x, y, z)."""
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w, x, y, z = (m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w, x, y, z = (m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w, x, y, z = (m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s
    q = np.array([w, x, y, z])
    return q / np.linalg.norm(q)


def frame(head, tail, zref):
    y = tail - head
    y = y / np.linalg.norm(y)
    z = zref - np.dot(zref, y) * y
    n = np.linalg.norm(z)
    if n < 1e-6:
        alt = LEFT if abs(y[0]) < 0.9 else UP
        z = alt - np.dot(alt, y) * y
        n = np.linalg.norm(z)
    z = z / n
    return np.stack([np.cross(y, z), y, z], axis=1)


class Skeleton:
    def __init__(self, joints):
        """joints: {bone: (head, tail, roll, parent)} from MHData.joints()."""
        self.names = []
        pending = dict(joints)
        while pending:  # parents before children
            for b, (h, t, r, p) in list(pending.items()):
                if p is None or p in self.names:
                    self.names.append(b)
                    del pending[b]
        self.idx = {b: i for i, b in enumerate(self.names)}
        self.parent = [self.idx[joints[b][3]] if joints[b][3] else -1 for b in self.names]
        self.head = np.array([joints[b][0] for b in self.names], float)
        self.tail = np.array([joints[b][1] for b in self.names], float)
        self.zref = np.zeros_like(self.head)
        for i in range(len(self.names)):
            y = self.tail[i] - self.head[i]
            y /= np.linalg.norm(y)
            self.zref[i] = UP if abs(np.dot(y, FRONT)) > 0.75 else FRONT

    def copy(self):
        s = Skeleton.__new__(Skeleton)
        s.names, s.idx, s.parent = list(self.names), dict(self.idx), list(self.parent)
        s.head, s.tail, s.zref = self.head.copy(), self.tail.copy(), self.zref.copy()
        return s

    def frames(self):
        return np.stack([frame(self.head[i], self.tail[i], self.zref[i]) for i in range(len(self.names))])

    def length(self, bone):
        i = self.idx[bone]
        return float(np.linalg.norm(self.tail[i] - self.head[i]))

    def children(self, i):
        return [j for j, p in enumerate(self.parent) if p == i]

    # ---------------------------------------------------------- transforms
    def _apply(self, V, W, order, A, c):
        """Linear-blend skinning with per-bone affine maps x -> A x + c."""
        out = np.zeros_like(V)
        for k, b in enumerate(order):
            i = self.idx[b]
            w = W[:, k:k + 1]
            if not w.any():
                continue
            out += w * (V @ A[i].T + c[i])
        return out

    def reshape(self, V, W, order, scales, extra_points=None):
        """Change proportions.  scales: {bone: (sx, sy, sz)} in the bone frame
        (Y along the bone).  A child's joint is carried by its parent's
        scaling but the child itself is not scaled (no scale inheritance).
        Returns new vertices; the skeleton is updated in place.
        """
        n = len(self.names)
        B = self.frames()
        A = np.zeros((n, 3, 3))
        c = np.zeros((n, 3))
        P = np.zeros((n, 3))
        for i, b in enumerate(self.names):
            s = np.asarray(scales.get(b, (1, 1, 1)), float)
            A[i] = B[i] @ np.diag(s) @ B[i].T
            p = self.parent[i]
            P[i] = self.head[i] if p < 0 else A[p] @ self.head[i] + c[p]
            c[i] = P[i] - A[i] @ self.head[i]
        Vn = self._apply(V, W, order, A, c)
        new_tail = np.array([A[i] @ self.tail[i] + c[i] for i in range(n)])
        extras = None
        if extra_points is not None:
            extras = {k: A[self.idx[b]] @ p + c[self.idx[b]] for k, (b, p) in extra_points.items()}
        self.head, self.tail = P, new_tail
        return (Vn, extras) if extra_points is not None else Vn

    def fk(self, rots, root_shift=(0, 0, 0)):
        """Forward kinematics.  rots: {bone: 3x3 delta}.  Returns (G, P):
        world delta rotation and posed head position for every bone."""
        n = len(self.names)
        G = np.zeros((n, 3, 3))
        P = np.zeros((n, 3))
        for i, b in enumerate(self.names):
            D = rots.get(b)
            p = self.parent[i]
            if p < 0:
                G[i] = np.eye(3) if D is None else D
                P[i] = self.head[i] + np.asarray(root_shift, float)
            else:
                G[i] = G[p] if D is None else G[p] @ D
                P[i] = P[p] + G[p] @ (self.head[i] - self.head[p])
        return G, P

    def posed_tail(self, G, P, bone):
        i = self.idx[bone]
        return P[i] + G[i] @ (self.tail[i] - self.head[i])

    def bake_pose(self, V, W, order, rots, root_shift=(0, 0, 0), extra_points=None):
        """Apply a pose and make it the new rest pose."""
        G, P = self.fk(rots, root_shift)
        n = len(self.names)
        c = np.array([P[i] - G[i] @ self.head[i] for i in range(n)])
        Vn = self._apply(V, W, order, G, c)
        extras = None
        if extra_points is not None:
            extras = {k: (G[self.idx[b]] @ p + c[self.idx[b]], G[self.idx[b]]) for k, (b, p) in extra_points.items()}
        self.tail = np.array([P[i] + G[i] @ (self.tail[i] - self.head[i]) for i in range(n)])
        self.zref = np.array([G[i] @ self.zref[i] for i in range(n)])
        self.head = P
        return (Vn, extras) if extra_points is not None else Vn

    def transform_all(self, M, t):
        """Uniform similarity transform of the skeleton (x -> M x + t)."""
        self.head = self.head @ M.T + t
        self.tail = self.tail @ M.T + t
        self.zref = self.zref @ (M / np.cbrt(abs(np.linalg.det(M)))).T

    def local_quat(self, bone, D, B=None):
        """Blender pose-bone quaternion for a character-space delta D."""
        if B is None:
            B = self.frames()
        Bi = B[self.idx[bone]]
        return mat_to_quat(Bi.T @ D @ Bi)

    def as_dict(self):
        out = {}
        for i, b in enumerate(self.names):
            out[b] = dict(head=self.head[i], tail=self.tail[i], zref=self.zref[i],
                          parent=self.names[self.parent[i]] if self.parent[i] >= 0 else None)
        return out


def solve_two_bone(root, target, l1, l2, pole):
    """Planar two-bone IK.  Returns the mid-joint position; the chain bends
    toward `pole` (a direction, need not be perpendicular)."""
    d = target - root
    dist = np.linalg.norm(d)
    dist = min(max(dist, abs(l1 - l2) + 1e-4), l1 + l2 - 1e-4)
    dn = d / np.linalg.norm(d)
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = np.sqrt(max(l1 * l1 - a * a, 0.0))
    pp = pole - np.dot(pole, dn) * dn
    pp = pp / (np.linalg.norm(pp) + 1e-9)
    return root + dn * a + pp * h, root + dn * dist


def rot_between(a, b):
    """Smallest rotation taking direction a to direction b."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    s = np.linalg.norm(v)
    c = np.dot(a, b)
    if s < 1e-9:
        return np.eye(3) if c > 0 else rot(np.cross(a, [1, 0, 0]) if abs(a[0]) < 0.9 else np.cross(a, [0, 1, 0]), 180)
    return rot(v / s, np.degrees(np.arctan2(s, c)))
