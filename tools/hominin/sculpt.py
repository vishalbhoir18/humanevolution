"""Cranio-facial reshaping as smooth displacement fields.

All operators work in a canonical head frame measured in centimetres on the
un-scaled reference head:

    x  lateral (character's left positive)
    f  forward (toward the face)
    u  up

with the origin at the midpoint between the eyeball centres.  On the reference
head: glabella is at f~2.4,u~2.5 ; nose tip f~4.1,u~-4 ; mouth u~-7 ;
chin f~2.4,u~-10.5 ; ear canal f~-9,u~-1.5 ; vertex u~10.8 ;
opisthocranion f~-17.7,u~3.

Every operator is evaluated on the ORIGINAL positions and the displacements
are summed, so operators do not interfere with each other's regions and the
order in which they are listed does not matter.
"""
import numpy as np


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def g(v, c, s):
    return np.exp(-((v - c) / s) ** 2)


# Base line of the braincase: glabella -> inion, in (f, u).
_G = np.array([2.3, 2.6])
_I = np.array([-16.5, -2.5])
_BL = (_I - _G) / np.linalg.norm(_I - _G)
_BN = np.array([-_BL[1], _BL[0]])  # normal
if _BN[1] < 0:
    _BN = -_BN


def above_base(f, u):
    """Signed height (cm) above the glabella-inion line."""
    return (f - _G[0]) * _BN[0] + (u - _G[1]) * _BN[1]


def front_mask(f):
    return sstep(-7.0, -1.5, f)


class HeadField:
    """Sum of displacement operators, built from a dict of parameters.

    Parameters (all optional, cm unless noted; 0 / 1 = modern human):
      vault_h      factor  height of the vault above the glabella-inion line
      vault_w      factor  braincase breadth (low on the vault)
      vault_w_top  factor  braincase breadth high on the vault (keeled / tent
                           shaped vaults are narrow on top)
      occiput      cm      backward (+) or forward (-) shift of the occiput
      bun          cm      localised occipital bun / torus projection
      forehead     cm      retreat of the upper frontal (receding forehead)
      brow         cm      supraorbital torus projection
      brow_arch    0..1    1 = double-arched (dips at the midline)
      brow_sulcus  cm      groove above the torus
      midface      cm      mid-facial projection (nose root to upper jaw)
      muzzle       cm      alveolar / lower-face projection
      muzzle_w     cm      half-width of the projecting muzzle
      chin         cm      chin retreat (+) or extra projection (-)
      jaw_drop     cm      lengthening of the lower face
      nose_flat    cm      flattening of the nose tip (+) / extra projection (-)
      nose_bridge  cm      lowering of the nasal bridge
      nose_w       cm      widening of the alae (each side)
      zygo         cm      extra cheek-bone breadth (each side)
      gonial       cm      extra breadth at the jaw angles (each side)
      interorb     cm      eyes moved toward the midline (each side)
      orbit_h      cm      heightening of the orbits
      nuchal       cm      thickening at the back of the neck / nuchal plane
      crest        cm      sagittal crest height
    """

    DEFAULTS = dict(vault_h=1.0, vault_w=1.0, vault_w_top=None, occiput=0.0, bun=0.0,
                    forehead=0.0, brow=0.0, brow_arch=0.0, brow_sulcus=0.0,
                    midface=0.0, muzzle=0.0, muzzle_w=4.2, chin=0.0, jaw_drop=0.0,
                    nose_flat=0.0, nose_bridge=0.0, nose_w=0.0, zygo=0.0, gonial=0.0,
                    interorb=0.0, orbit_h=0.0, nuchal=0.0, crest=0.0, face_w=1.0,
                    upper_face=0.0, lip_seal=0.0)

    def __init__(self, **params):
        self.p = dict(self.DEFAULTS)
        unknown = set(params) - set(self.p)
        if unknown:
            raise KeyError(f"unknown head parameters: {sorted(unknown)}")
        self.p.update(params)

    def displacement(self, P):
        """P: (n, 3) canonical (x, f, u) cm.  Returns (n, 3) displacement."""
        p = self.p
        x, f, u = P[:, 0], P[:, 1], P[:, 2]
        ax = np.abs(x)
        sx = np.sign(x)
        D = np.zeros_like(P)
        s = above_base(f, u)
        m_bc = sstep(-0.8, 2.2, s)
        fm = front_mask(f)

        # --- braincase ----------------------------------------------------
        if p["vault_h"] != 1.0:
            k = p["vault_h"] - 1.0
            D[:, 1] += k * np.maximum(s, 0) * _BN[0] * m_bc
            D[:, 2] += k * np.maximum(s, 0) * _BN[1] * m_bc
        kw_low = p["vault_w"]
        kw_top = p["vault_w_top"] if p["vault_w_top"] is not None else kw_low
        if kw_low != 1.0 or kw_top != 1.0:
            kw = kw_low + (kw_top - kw_low) * sstep(1.0, 8.0, s)
            # fade the narrowing out toward the face so the cheeks keep their width
            D[:, 0] += (kw - 1.0) * x * sstep(-2.5, 1.5, s) * sstep(3.5, -3.0, f)
        if p["occiput"]:
            D[:, 1] += -p["occiput"] * sstep(-7.0, -15.5, f) * sstep(-6.0, -2.0, u) * sstep(11.5, 7.5, u)
        if p["bun"]:
            D[:, 1] += -p["bun"] * g(u, 1.5, 2.6) * sstep(-11.0, -16.5, f) * g(x, 0, 6.0)
        if p["forehead"]:
            D[:, 1] += -p["forehead"] * sstep(2.6, 9.0, u) * sstep(-10.5, -2.0, f)
        if p["crest"]:
            D[:, 2] += p["crest"] * g(x, 0, 0.9) * sstep(-1.0, -5.0, f) * sstep(-17.0, -12.0, f) * sstep(6.0, 8.5, u)

        # --- brow ridge ---------------------------------------------------
        if p["brow"]:
            lat = sstep(8.2, 5.4, ax)
            mid = 1.0 - 0.55 * p["brow_arch"] * g(x, 0, 1.3)
            band = g(u, 2.25, 1.05)
            D[:, 1] += p["brow"] * band * lat * mid * fm
            D[:, 2] += -0.22 * p["brow"] * g(u, 1.7, 0.9) * lat * fm     # slight overhang
        if p["brow_sulcus"]:
            D[:, 1] += -p["brow_sulcus"] * g(u, 4.3, 1.3) * sstep(8.5, 5.0, ax) * fm

        # --- face ---------------------------------------------------------
        if p["upper_face"]:
            # tall upper face: everything below the orbits moves down
            D[:, 2] += -p["upper_face"] * sstep(-1.2, -4.5, u) * fm
        if p["midface"]:
            D[:, 1] += p["midface"] * g(x, 0, 3.4) * sstep(1.2, -1.6, u) * sstep(-9.5, -6.0, u) * fm
        if p["muzzle"]:
            w = p["muzzle_w"]
            lat = np.exp(-(ax / w) ** 2.4)
            vert = sstep(-0.6, -5.2, u) * sstep(-14.0, -10.2, u)
            D[:, 1] += p["muzzle"] * lat * vert * fm
        if p["chin"]:
            # the whole symphysis slopes back, including the soft tissue under it
            D[:, 1] += -p["chin"] * g(x, 0, 3.6) * (g(u, -10.9, 1.9) + 0.55 * g(u, -13.0, 1.6)) * fm
            D[:, 2] += 0.35 * p["chin"] * g(x, 0, 3.6) * g(u, -12.6, 1.5) * sstep(-6.0, 0.0, f)
        if p["jaw_drop"]:
            D[:, 2] += -p["jaw_drop"] * sstep(-4.5, -9.5, u) * sstep(-9.0, -3.0, f)
        if p["nose_flat"]:
            D[:, 1] += -p["nose_flat"] * g(x, 0, 1.7) * g(u, -3.7, 1.7) * sstep(1.2, 3.6, f)
        if p["nose_bridge"]:
            D[:, 1] += -p["nose_bridge"] * g(x, 0, 1.3) * g(u, -1.2, 1.6) * sstep(0.8, 2.6, f)
        if p["nose_w"]:
            D[:, 0] += sx * p["nose_w"] * g(ax, 1.5, 1.3) * g(u, -4.5, 1.2) * sstep(0.5, 2.5, f)
        if p["zygo"]:
            D[:, 0] += sx * p["zygo"] * g(ax, 6.2, 2.4) * g(u, -2.4, 2.6) * sstep(-9.5, -2.0, f)
        if p["gonial"]:
            D[:, 0] += sx * p["gonial"] * g(ax, 5.6, 2.6) * g(u, -8.6, 2.8) * g(f, -4.5, 4.0)
        if p["face_w"] != 1.0:
            D[:, 0] += (p["face_w"] - 1.0) * x * sstep(1.5, -1.5, s) * sstep(-8.0, -2.0, f) * sstep(-13.5, -10.0, u)
        if p["interorb"]:
            D[:, 0] += -sx * p["interorb"] * g(ax, 2.9, 2.2) * g(u, 0.0, 2.4) * fm
        if p["orbit_h"]:
            D[:, 2] += p["orbit_h"] * g(ax, 2.9, 2.0) * g(u, 1.2, 1.1) * fm
        if p["nuchal"]:
            D[:, 1] += -p["nuchal"] * g(x, 0, 6.5) * g(u, -6.0, 4.5) * sstep(-8.0, -13.0, f)
        return D

    def apply(self, P):
        return P + self.displacement(P)
