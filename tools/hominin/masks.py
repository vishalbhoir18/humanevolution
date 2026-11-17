"""Hair-region masks in the canonical head frame (cm).  Shared by the
texture stage (per texel) and the shaping stage (per vertex, for hair volume)."""
import numpy as np

from .sculpt import sstep


def scalp(X, F, U, hairline=None, jit=0.0, soft=1.2):
    """1 inside the scalp-hair region.  `soft` = width (cm) of the edge."""
    hl = hairline or {}
    a_f, a_u = hl.get("front", (1.2, 7.3))
    b_f, b_u = hl.get("nape", (-13.0, -6.5))
    dn = np.array([-(b_u - a_u), (b_f - a_f)], dtype=float)
    dn /= np.linalg.norm(dn)
    if dn[1] < 0:
        dn = -dn
    d = (F - a_f) * dn[0] + (U - a_u) * dn[1]
    temple = sstep(4.0, 7.5, np.abs(X)) * hl.get("temple", 1.2)
    m = sstep(-0.4 * soft, 0.6 * soft, d + temple + jit * 0.6)
    return m * sstep(-19.0, -15.0, U) * (U > -17.0)


def beard(X, F, U, jit=0.0, soft=1.0):
    """Jaw-line beard plus moustache; the cheeks stay bare."""
    AX = np.abs(X)
    top = -6.3 + 3.9 * sstep(-2.5, -8.6, F)             # cheek line: mouth corner -> sideburn
    under = sstep(-14.6, -12.6, U + jit * 0.25)          # stops a little below the jaw line
    jaw = sstep(0.0, 1.2 * soft, top - U + jit * 0.5) * under * sstep(-10.5, -8.6, F)
    # moustache, running down past the mouth corners to join the beard
    tache = sstep(-6.75, -6.35, U) * sstep(-5.0, -5.5, U + jit * 0.1) * sstep(3.9, 2.9, AX) * sstep(1.0, 2.0, F)
    corner = sstep(-9.5, -8.0, U) * sstep(-5.4, -6.2, U) * sstep(2.2, 3.0, AX) * sstep(4.6, 3.8, AX) * sstep(0.0, 1.5, F)
    tache = np.clip(tache + corner, 0, 1)
    return np.clip(jaw + tache, 0, 1) * (U > -17.0)


def brows(X, F, U, jit=0.0):
    AX = np.abs(X)
    ub = 1.55 + 0.55 * np.exp(-((AX - 4.0) / 2.0) ** 2)
    tb = 0.55 - 0.035 * np.clip(AX - 2.0, 0, 4)
    return np.exp(-((U - ub + jit * 0.12) / tb) ** 2) * sstep(1.0, 1.7, AX) * sstep(6.3, 5.3, AX) * sstep(-1.0, 0.5, F)


def ear_zone(X, F, U):
    """Rough ear location, to keep hair volume off the ears."""
    AX = np.abs(X)
    return sstep(6.3, 7.2, AX) * sstep(-12.5, -11.0, F) * sstep(-6.0, -7.5, F) * sstep(-5.5, -4.0, U) * sstep(3.6, 2.4, U)


def vertex_normals(V, tris):
    n = np.zeros_like(V)
    fn = np.cross(V[tris[:, 1]] - V[tris[:, 0]], V[tris[:, 2]] - V[tris[:, 0]])
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1
    return n / ln
