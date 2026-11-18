"""Lateral-view skull diagrams as SVG.

Skulls are described in skulls.py as landmark lists in millimetres, in the
standard craniometric orientation: origin at porion (top of the ear opening),
x forward, y up, Frankfort horizontal along y = 0.  The drawing faces left,
like most comparative figures.  Every skull uses the same scale, so their
sizes can be compared directly.

Line style carries evidence: solid = preserved in the named specimen(s),
dashed = reconstructed.
"""
import math

import numpy as np
from shapely.geometry import Polygon

# palette (matches index.html)
BONE = "#ece3d0"
BONE_FILL = "#d9ccb0"
INK = "#0e0b09"
DIM = "#b8ac95"
OCHRE = "#a8763e"
PATINA = "#4fa392"
PATINA_BRIGHT = "#69c4b1"


# ------------------------------------------------------------------ points
class Pt(tuple):
    """A point; .corner marks a sharp turn in a spline."""

    def __new__(cls, x, y, corner=False):
        t = super().__new__(cls, (float(x), float(y)))
        t.corner = corner
        return t


def resolve(spec, item):
    """(x, y), (x, y, 'c'), 'NAME' or 'NAME!' (! = corner) -> Pt."""
    if isinstance(item, Pt):
        return item
    if isinstance(item, str):
        corner = item.endswith("!")
        x, y = spec["pt"][item.rstrip("!")]
        return Pt(x, y, corner)
    return Pt(item[0], item[1], len(item) > 2)


def pts(spec, items):
    return [resolve(spec, i) for i in items]


# ---------------------------------------------------------------- splines
def bezier(P, closed=False):
    pts_ = [np.array(p, float) for p in P]
    corners = [bool(getattr(p, "corner", False)) for p in P]
    n = len(pts_)
    if n < 2:
        return []

    def tangent(i):
        if corners[i]:
            return None
        if closed:
            a, b = pts_[(i - 1) % n], pts_[(i + 1) % n]
        else:
            if i == 0 or i == n - 1:
                return None
            a, b = pts_[i - 1], pts_[i + 1]
        d = b - a
        L = np.linalg.norm(d)
        return d / L if L > 1e-9 else None

    T = [tangent(i) for i in range(n)]
    segs = []
    m = n if closed else n - 1
    for i in range(m):
        j = (i + 1) % n
        p0, p1 = pts_[i], pts_[j]
        d = np.linalg.norm(p1 - p0)
        t0 = T[i] if T[i] is not None else (p1 - p0) / (d + 1e-9)
        t1 = T[j] if T[j] is not None else (p1 - p0) / (d + 1e-9)
        segs.append((p0, p0 + t0 * d / 3.0, p1 - t1 * d / 3.0, p1))
    return segs


def sample(segs, per=12):
    out = []
    for k, (a, b, c, d) in enumerate(segs):
        for i in range(per + (1 if k == len(segs) - 1 else 0)):
            t = i / per
            u = 1 - t
            out.append(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d)
    return np.array(out)


# ---------------------------------------------------------------- svg out
def fx(v):
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else s.rstrip("0").rstrip(".") if "." in s else s


def X(p):
    """mm (x forward, y up) -> svg user units (face to the left, y down)."""
    return f"{fx(-p[0])},{fx(-p[1])}"


def path_d(segs, closed=False):
    if not segs:
        return ""
    d = [f"M{X(segs[0][0])}"]
    for _, c1, c2, p1 in segs:
        d.append(f"C{X(c1)} {X(c2)} {X(p1)}")
    if closed:
        d.append("Z")
    return "".join(d)


def poly_d(poly, closed=False):
    d = "M" + " L".join(X(p) for p in poly)
    return d + ("Z" if closed else "")


def squiggle(poly, amp=0.7, wave=2.6):
    """Zig-zag a polyline perpendicular to itself (sutures)."""
    poly = np.asarray(poly, float)
    seg = np.diff(poly, axis=0)
    L = np.r_[0, np.cumsum(np.linalg.norm(seg, axis=1))]
    if L[-1] < 1e-6:
        return poly
    s = np.arange(0, L[-1], wave / 4.0)
    x = np.interp(s, L, poly[:, 0])
    y = np.interp(s, L, poly[:, 1])
    p = np.stack([x, y], 1)
    t = np.gradient(p, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([-t[:, 1], t[:, 0]], 1)
    k = np.arange(len(s))
    off = amp * np.array([0, 1, 0, -1])[k % 4]
    fade = np.minimum(1, np.minimum(s, L[-1] - s) / 3.0)
    return p + nrm * (off * fade)[:, None]


def chaikin(poly, n=2, closed=True):
    P = np.asarray(poly, float)
    for _ in range(n):
        Q = []
        m = len(P)
        rng = range(m) if closed else range(m - 1)
        for i in rng:
            a, b = P[i], P[(i + 1) % m]
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        P = np.array(Q)
    return P


# ------------------------------------------------------------------ teeth
def tooth_row(row, upper, dashed, style):
    """Crown outlines along a tooth row.

    row: x0 (front end), y_alv, y_occ, widths [mesiodistal, projected],
         kinds ('i','c','p','m'), canine_extra, gaps {index: mm}, tilt (deg,
         incisor procumbency)
    """
    out = []
    x = row["x0"]
    ya, yo = row["y_alv"], row["y_occ"]
    sgn = -1 if upper else 1           # crowns grow downward (upper) / upward (lower)
    for i, (w, kind) in enumerate(zip(row["widths"], row["kinds"])):
        x1, x2 = x, x - w                # front, back
        h = abs(yo - ya)
        if kind == "c":
            tip_extra = row.get("canine_extra", 0.0)
            tip = (x1 + x2) / 2 + w * 0.08
            ytip = yo + sgn * tip_extra
            shape = [(x1 - .4, ya), (x1 - w * .02, ya + sgn * h * .45), (tip, ytip, "c"),
                     (x2 + w * .05, ya + sgn * h * .5), (x2 + .3, ya)]
        elif kind == "i":
            # an incisor seen from the side is a wedge: thick at the gum,
            # thin at the cutting edge, tipped forward by `tilt`
            tilt = math.tan(math.radians(row.get("tilt", 0.0)))
            dx = (yo - ya) * tilt * (1 if upper else -1) * -1
            wb = w + 2.2                       # labio-lingual depth at the neck
            shape = [(x1 + .2, ya), (x1 + dx * .55 + .5, ya + sgn * h * .5), (x1 + dx + .3, yo, "c"),
                     (x1 + dx - 1.3, yo, "c"), (x1 - wb * .55 + dx * .3, ya + sgn * h * .45), (x1 - wb + .3, ya)]
        else:
            cusps = 2 if kind == "m" else 1
            pts_ = [(x1 - .3, ya), (x1 - .2, yo - sgn * h * .35)]
            if cusps == 2:
                pts_ += [(x1 - w * .22, yo), (x1 - w * .5, yo - sgn * .9), (x2 + w * .22, yo)]
            else:
                pts_ += [(x1 - w * .45, yo)]
            pts_ += [(x2 + .2, yo - sgn * h * .35), (x2 + .3, ya)]
            shape = pts_
        P = [Pt(*s[:2], len(s) > 2) for s in shape]
        segs = bezier(P, closed=False)
        d = path_d(segs) + "Z"
        out.append(f'<path d="{d}" {style}{dashed}/>')
        x = x2 - row.get("gaps", {}).get(i, 0.0)
    return out


# ---------------------------------------------------------------- builder
class Skull:
    def __init__(self, spec):
        self.s = spec
        pt = lambda items: pts(spec, items)
        self.groups = []                               # (group, [Pt...]) in outline order
        for g, key in (("face", "front_up"), ("vault", "vault"), ("occiput", "occiput"),
                       ("base", "base"), ("face", "under"), ("face", "alveolar"), ("face", "face_up")):
            self.groups.append((g, pt(spec[key])))
        self.outline_pts = [resolve(spec, "N")]
        self.owner = ["face"]
        for g, P in self.groups:
            self.outline_pts += P
            self.owner += [g] * len(P)
        self.outline = bezier(self.outline_pts, closed=True)
        self.mand = bezier(pt(spec["mand"]), closed=True)

    def recess(self):
        s = self.s
        under = [resolve(s, s["base"][-1])] + pts(s, s["under"])
        mand = pts(s, s["mand"])
        k = next(i for i, p in enumerate(mand) if p.corner and i > 10)      # retromolar corner
        front = mand[k:]
        return np.vstack([sample(bezier(under), 8), sample(bezier(front), 8)])

    def dashed(self, group):
        return group in self.s.get("reconstructed", ())

    # ............................................................ endocast
    def endocast(self):
        s = self.s
        P = self.outline_pts
        # outer contour from glabella round to inion
        i0 = P.index(resolve(s, "G"))
        i1 = P.index(resolve(s, "I"))
        outer = sample(bezier(P[i0:i1 + 1]), 10)
        floor = np.array([resolve(s, p) for p in s["floor"]], float)
        floor = sample(bezier([Pt(*p) for p in floor]), 8)
        poly = Polygon(np.vstack([outer, floor])).buffer(0)
        inner = poly.buffer(-s["vault_thickness"], join_style=1)
        if inner.geom_type != "Polygon":
            inner = max(inner.geoms, key=lambda g: g.area)
        ring = np.array(inner.exterior.coords)[:-1]
        ring = Polygon(ring).simplify(0.6).exterior.coords
        ring = chaikin(np.array(ring)[:-1], 2)
        return ring, inner.area

    # ............................................................ drawing
    def svg_parts(self):
        s = self.s
        sw = 1.05
        line = f'fill="none" stroke="{BONE}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
        dash = ' stroke-dasharray="3.2 2.4"'
        out = []
        # fills
        out.append(f'<path class="sk-fill" d="{path_d(self.outline, True)}" fill="{BONE_FILL}" fill-opacity=".13"/>')
        ring, area = self.endocast()
        self.endo_area = area
        out.append(f'<path class="sk-brain" d="{poly_d(ring, True)}" fill="{PATINA_BRIGHT}" fill-opacity=".26" '
                   f'stroke="{PATINA_BRIGHT}" stroke-width=".7" stroke-opacity=".8" stroke-dasharray="1.6 1.6"/>')
        # the hollow below the cheek arch, between the upper jaw and the ramus
        out.append(f'<path d="{poly_d(self.recess(), True)}" fill="{INK}" fill-opacity=".55"/>')
        # mandible
        md = self.dashed("mandible")
        out.append(f'<path class="sk-fill" d="{path_d(self.mand, True)}" fill="{BONE_FILL}" fill-opacity=".16"/>')
        # openings
        for key in ("orbit", "nasal"):
            if key in s:
                P_ = pts(s, s[key])
                if key == "nasal":
                    P_[0], P_[-1] = Pt(*P_[0], True), Pt(*P_[-1], True)
                segs = bezier(P_, closed=True)
                out.append(f'<path d="{path_d(segs, True)}" fill="{INK}" fill-opacity=".92" stroke="{BONE}" stroke-width=".7"/>')
        cx, cy, rx, ry = s["eam"]
        out.append(f'<ellipse cx="{fx(-cx)}" cy="{fx(-cy)}" rx="{rx}" ry="{ry}" fill="{INK}" stroke="{BONE}" stroke-width=".7"/>')
        if "mf" in s:
            mx, my = s["mf"]
            out.append(f'<ellipse cx="{fx(-mx)}" cy="{fx(-my)}" rx="1.6" ry="1.1" fill="{INK}" stroke="{BONE}" stroke-width=".5"/>')
        # fine detail lines
        for key, style in (("temporal", f'stroke-dasharray="0.3 2.2" stroke-width="1.1" stroke-opacity=".55"'),):
            if key in s:
                segs = bezier(pts(s, s[key]))
                out.append(f'<path d="{path_d(segs)}" fill="none" stroke="{BONE}" stroke-linecap="round" {style}/>')
        for key in ("coronal", "squamosal", "lambdoid", "pmastoid", "zygtemp", "fz"):
            if key in s:
                poly = sample(bezier(pts(s, s[key])), 10)
                out.append(f'<path d="{poly_d(squiggle(poly))}" fill="none" stroke="{BONE}" stroke-width=".5" stroke-opacity=".6"/>')
        for P_ in s.get("lines", []):
            segs = bezier(pts(s, P_))
            out.append(f'<path d="{path_d(segs)}" {line} stroke-width=".7" stroke-opacity=".75"/>')
        for P_ in s.get("faint", []):
            segs = bezier(pts(s, P_))
            out.append(f'<path d="{path_d(segs)}" {line} stroke-width=".55" stroke-opacity=".4"/>')
        # zygomatic arch
        fd = dash if self.dashed("face") else ""
        for key in ("zyg_upper", "zyg_lower"):
            segs = bezier(pts(s, s[key]))
            out.append(f'<path d="{path_d(segs)}" {line}{fd}/>')
        # teeth (lower first so the upper canine overlaps)
        tstyle = f'fill="{BONE_FILL}" fill-opacity=".22" stroke="{BONE}" stroke-width=".65" stroke-linejoin="round"'
        out += tooth_row(s["teeth"]["lower"], False, dash if md else "", tstyle)
        out += tooth_row(s["teeth"]["upper"], True, fd, tstyle)
        # outlines, split into solid and dashed runs
        runs, cur, cur_g = [], [], None
        for k, seg in enumerate(self.outline):
            g = self.owner[k]
            dsh = self.dashed(g)
            if cur and dsh != cur_g:
                runs.append((cur_g, cur))
                cur = []
            cur.append(seg)
            cur_g = dsh
        runs.append((cur_g, cur))
        for dsh, segs in runs:
            out.append(f'<path class="sk-line" d="{path_d(segs)}" {line} stroke-width="1.3"{dash if dsh else ""}/>')
        out.append(f'<path class="sk-line" d="{path_d(self.mand, True)}" {line} stroke-width="1.3"{dash if md else ""}/>')
        return out

    # ............................................................ labels
    def labels(self):
        s = self.s
        out = []
        for lab in s.get("labels", []):
            ax, ay = resolve(s, lab["at"])
            tx, ty = lab["to"]
            anchor = lab.get("anchor", "end" if tx > ax else "start")   # mm x grows forward = leftward
            # leader: from anchor dot to a short elbow at the text
            ex = tx + (2.5 if anchor == "end" else -2.5) * -1
            out.append(f'<circle cx="{fx(-ax)}" cy="{fx(-ay)}" r="1.25" fill="{PATINA_BRIGHT}"/>')
            out.append(f'<path d="M{X((ax, ay))} L{X((ex, ty))}" fill="none" stroke="{PATINA_BRIGHT}" '
                       f'stroke-width=".55" stroke-opacity=".9"/>')
            lines = lab["text"].split("\n")
            y0 = -ty + 3.2 - (len(lines) - 1) * 5.3
            tsp = "".join(f'<tspan x="{fx(-tx)}" dy="{0 if i == 0 else 10.6}">{t}</tspan>'
                          for i, t in enumerate(lines))
            out.append(f'<text x="{fx(-tx)}" y="{fx(y0)}" text-anchor="{anchor}" '
                       f'font-family="IBM Plex Mono, ui-monospace, monospace" font-size="9.2" '
                       f'letter-spacing=".2" fill="{BONE}">{tsp}</text>')
        return out

    def bbox(self):
        A = np.vstack([sample(self.outline, 6), sample(self.mand, 6)])
        return A[:, 0].min(), A[:, 0].max(), A[:, 1].min(), A[:, 1].max()


def scale_bar(x_right, y):
    """5 cm bar ending at svg x = x_right."""
    x0 = x_right - 50
    t = [f'<g class="sk-scale" stroke="{DIM}" stroke-width=".7" fill="none">',
         f'<path d="M{fx(x0)},{fx(y)} H{fx(x_right)}"/>']
    for k in range(6):
        h = 2.6 if k in (0, 5) else 1.4
        t.append(f'<path d="M{fx(x0 + 10 * k)},{fx(y - h)} V{fx(y)}"/>')
    t.append("</g>")
    t.append(f'<text x="{fx(x_right)}" y="{fx(y + 8)}" text-anchor="end" font-family="IBM Plex Mono, ui-monospace, monospace" '
             f'font-size="8" fill="{DIM}">5 cm</text>')
    return t


def render(spec, viewbox, title):
    sk = Skull(spec)
    vx, vy, vw, vh = viewbox
    body = sk.svg_parts() + ['<g class="sk-labels">'] + sk.labels() + ['</g>'] + scale_bar(vx + vw - 6, vy + vh - 12)
    svg = (f'<svg class="skull-svg sk-diagram" viewBox="{fx(vx)} {fx(vy)} {fx(vw)} {fx(vh)}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">'
           + "".join(body) + "</svg>")
    return svg, sk


def icon(spec, viewbox):
    """Silhouette for the lineage strip: outline + mandible + openings only."""
    sk = Skull(spec)
    vx, vy, vw, vh = viewbox
    parts = [f'<path class="sil" d="{path_d(sk.outline, True)}"/>',
             f'<path class="sil" d="{path_d(sk.mand, True)}"/>']
    for key in ("orbit", "nasal"):
        if key in spec:
            parts.append(f'<path class="hole" d="{path_d(bezier(pts(spec, spec[key]), closed=True), True)}"/>')
    return (f'<svg class="skull-svg sk-icon" viewBox="{fx(vx)} {fx(vy)} {fx(vw)} {fx(vh)}" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' + "".join(parts) + "</svg>")
