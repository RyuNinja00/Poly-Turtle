"""Exact small parts for the rev 3.1 lid (no voxels):

* outlet_bushing(): M10x1 internal thread (PC4-M10) + O-ring / TPU-washer groove,
  placed on the filament axis; merged as its own shell into the lid file.
* tpu_washer():     printable alternative to the 10 x 1 O-ring.
* gaskets():        TPU lid-to-box gaskets that snap into jojo's rim channel.
* mf_plate(), mf_gasket(): Micro-Fit 3.0 2x6 bulkhead plate and its TPU gasket.
All return (V, T) closed manifolds; prisms are capped with earcut.py.
"""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import earcut


# ------------------------------------------------------------------ prisms from 2D loops
def _ccw(P): return P if earcut._area(P) > 0 else P[::-1]
def _cw(P): return P if earcut._area(P) < 0 else P[::-1]

def prism(outer, holes, z0, z1, flip=False):
    """Extrude a polygon (outer loop + hole loops, Nx2 arrays) from z0 to z1."""
    outer = _ccw(np.asarray(outer, float)); holes = [_cw(np.asarray(h, float)) for h in holes]
    loops = [outer] + holes
    P2 = np.concatenate(loops); n = len(P2)
    V = np.concatenate([np.column_stack([P2, np.full(n, z0)]), np.column_stack([P2, np.full(n, z1)])])
    T = []; off = 0; idx = []
    for L in loops:
        m = len(L); ids = np.arange(off, off + m); idx.append(ids); off += m
        for i in range(m):
            a, b = ids[i], ids[(i + 1) % m]
            T += [[a, b, b + n], [a, b + n, a + n]]
    ring = earcut.bridge(P2, list(idx[0]), [np.array(h) for h in idx[1:]]) if holes else list(idx[0])
    top = np.array(earcut.earclip(P2, ring))
    T = np.concatenate([np.array(T), top + n, top[:, ::-1]])
    if flip: T = T[:, ::-1]
    return V, T

def merge(*parts):
    Vs, Ts, off = [], [], 0
    for V, T in parts:
        Vs.append(V); Ts.append(T + off); off += len(V)
    return np.concatenate(Vs), np.concatenate(Ts)

def simplify(P, tol=0.01):
    """Douglas-Peucker on a closed loop."""
    P = np.asarray(P)
    def dp(Q):
        if len(Q) < 3: return Q
        a, b = Q[0], Q[-1]; ab = b - a; L = np.hypot(*ab) + 1e-12
        d = np.abs(ab[0] * (Q[:, 1] - a[1]) - ab[1] * (Q[:, 0] - a[0])) / L
        i = int(np.argmax(d))
        if d[i] > tol: return np.concatenate([dp(Q[:i + 1])[:-1], dp(Q[i:])])
        return np.array([a, b])
    k = int(np.argmax(np.hypot(P[:, 0] - P[0, 0], P[:, 1] - P[0, 1])))
    A = dp(np.concatenate([P[:k + 1]])); B = dp(np.concatenate([P[k:], P[:1]]))
    return np.concatenate([A[:-1], B[:-1]])

def rounded_rect(cx, cy, w, h, r, n=10):
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        c = (cx + sx * (w / 2 - r), cy + sy * (h / 2 - r))
        for t in np.radians(np.linspace(a0, a0 + 90, n)):
            pts.append((c[0] + r * np.cos(t), c[1] + r * np.sin(t)))
    return np.array(pts)

def circle(cx, cy, r, n=40):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False); return np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])


# ------------------------------------------------------------------ outlet bushing (M10 x 1)
THREAD = dict(pitch=1.0, major=10.30, minor=9.10)     # PC4-M10 male: M10x1; +0.3/+0.2 print clearance
BUSH_R = 7.2
GROOVE = dict(r_out=6.30, depth=0.80)                  # counterbore at the mouth: 10 x 1 O-ring round the fitting thread, or the TPU washer

def _thread_r(theta, s):
    """internal-thread surface radius: 60-deg profile, P/8 flat at the major, P/4 at the minor"""
    P = THREAD['pitch']; p = np.mod(s / P - theta / (2 * np.pi), 1.0)
    rM, rm = THREAD['major'] / 2, THREAD['minor'] / 2
    # trapezoid: minor flat 0..0.125 and 0.875..1, rise 0.125..0.4375, major flat 0.4375..0.5625, fall
    up = np.clip((p - 0.125) / 0.3125, 0, 1); dn = np.clip((0.875 - p) / 0.3125, 0, 1)
    return rm + (rM - rm) * np.minimum(up, dn)

def outlet_bushing(origin, axis, s0, s1, n_theta=96, ds=0.05):
    """closed ring mesh, local frame: s along axis from s0 (inside) to s1 (fitting face)."""
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    e1 = np.cross(axis, [0, 1.0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(axis, e1)
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    s_top = s1 - GROOVE['depth']
    s_bore = np.arange(s0, s_top + 1e-9, ds); s_bore[-1] = s_top
    prof = []   # per theta: list of (r, s), closed loop
    for t in th:
        rb = _thread_r(t, s_bore)
        loop = [(r, s) for r, s in zip(rb, s_bore)]                       # bore s0 -> s1
        loop += [(GROOVE['r_out'], s1 - GROOVE['depth']), (GROOVE['r_out'], s1), (BUSH_R, s1), (BUSH_R, s0)]   # counterbore, face, outer wall
        prof.append(loop)
    m = len(prof[0]); V = []
    for t, loop in zip(th, prof):
        c, sn = np.cos(t), np.sin(t)
        for r, s in loop: V.append(origin + axis * s + r * (c * e1 + sn * e2))
    V = np.array(V); T = []
    for i in range(n_theta):
        a0, a1 = i * m, ((i + 1) % n_theta) * m
        for j in range(m):
            p, q = a0 + j, a0 + (j + 1) % m; p2, q2 = a1 + j, a1 + (j + 1) % m
            T += [[p, p2, q2], [p, q2, q]]
    T = np.array(T)
    if mk.check_mesh(V, T)['volume'] < 0: T = T[:, ::-1]
    return V, T

def tpu_washer():
    o = circle(0, 0, GROOVE['r_out'] - 0.15, 64); i = circle(0, 0, 5.15, 64)   # ID 10.3 slips over the M10 thread
    return prism(o, [i], 0.0, 1.2)                                             # 0.4 proud of the 0.8 counterbore


# ------------------------------------------------------------------ lid-to-box gasket
CHANNEL_Z = 64.8            # jojo's channel is widest just under its ceiling (Z 65.2)
GASKET_FIT = 0.15           # per side, against the channel walls at CHANNEL_Z
GASKET_WALL = 0.8
GASKET_HEIGHTS = (2.5, 3.5, 4.5)

def channel_loops(base_tri):
    from slice2d import slice_loops, area
    L = sorted(slice_loops(base_tri, CHANNEL_Z), key=lambda l: -abs(area(l)))
    return L[1], L[2]           # channel outer wall, channel inner wall

def offset_loop(P, d, h=0.05):
    """offset a closed loop by d (mm, + outward) via a fine raster + contour."""
    from matplotlib.path import Path as MP
    from scipy import ndimage as ndi
    from skimage import measure
    lo = P.min(0) - abs(d) - 2; hi = P.max(0) + abs(d) + 2
    xs = np.arange(lo[0], hi[0], h); ys = np.arange(lo[1], hi[1], h)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    inside = MP(P).contains_points(np.column_stack([X.ravel(), Y.ravel()])).reshape(X.shape)
    sd = (ndi.distance_transform_edt(~inside) - ndi.distance_transform_edt(inside)) * h
    C = max(measure.find_contours(sd, d), key=len)
    return simplify(np.column_stack([lo[0] + C[:, 0] * h, lo[1] + C[:, 1] * h]), 0.01)

def gaskets(base_tri):
    co, ci = channel_loops(base_tri)
    out = offset_loop(co, -GASKET_FIT); inn = offset_loop(ci, GASKET_FIT)
    vo = offset_loop(co, -GASKET_FIT - GASKET_WALL); vi = offset_loop(ci, GASKET_FIT + GASKET_WALL)
    width = float(np.median(np.hypot(*(out[:, None, :] - inn[None, ::7, :]).transpose(2, 0, 1)).min(1)))
    res = {}
    for hgt in GASKET_HEIGHTS:
        solid = prism(out, [inn], 0.0, hgt)
        void = prism(vo, [vi], GASKET_WALL, hgt - GASKET_WALL, flip=True)
        res[hgt] = merge(solid, void)
    return res, dict(width=round(width, 2), channel_walls=(co, ci))


# ------------------------------------------------------------------ Micro-Fit 3.0 2x6 bulkhead plate
# Cutout shape after Wireheadarts' "OpenSCAD library for mounting Molex MicroFit 3.0
# panel-mount plugs" (Printables 1300761), which follows the Molex datasheet:
#   body C x H  +  ear slot D x E (full ear span)  +  latch notch 3.18 wide.
# Its C/D tables equal Molex's 43020 table by column count; for 2 x 6: C 19.21, D 22.89.
# The library is single-row (H 4.21, latch to 5.51); dual row adds one 3.00 mm row pitch.
MF = dict(cols=6, rows=2,
          C=19.25, D=22.89,   # C: seller's 2x6 body 19.00 +/-0.25 (max 19.25; Molex cutout 19.21)
          E=3.05, H1=4.21, pitch=3.00, latch_w=3.18, latch_h=1.30,
          fit=0.05,                       # per side, for a printed panel
          plate=(40.0, 22.0, 2.0),        # 2.0 mm: inside the 1.57-2.30 panel range
          r=3.0, screw_dx=16.0, screw_d=3.4,
          aperture=(25.0, 13.5))          # hole in the lid under the plate (housing + ears pass)

def mf_cutout():
    f = MF['fit']; C, D, E = MF['C'] / 2 + 0.10, MF['D'] / 2 + f, MF['E'] / 2 + f
    Hh = (MF['H1'] + (MF['rows'] - 1) * MF['pitch']) / 2 + f
    lw, lt = MF['latch_w'] / 2 + f, Hh + MF['latch_h']
    return np.array([(D, -E), (D, E), (C, E), (C, Hh), (lw, Hh), (lw, lt), (-lw, lt), (-lw, Hh), (-C, Hh), (-C, E),
                     (-D, E), (-D, -E), (-C, -E), (-C, -Hh), (C, -Hh), (C, -E)])

def mf_plate():
    L, Wd, t = MF['plate']
    o = rounded_rect(0, 0, L, Wd, MF['r'])
    holes = [mf_cutout(), circle(-MF['screw_dx'], 0, MF['screw_d'] / 2, 24), circle(MF['screw_dx'], 0, MF['screw_d'] / 2, 24)]
    return prism(o, holes, 0.0, t)

def mf_gasket():
    L, Wd, _ = MF['plate']
    o = rounded_rect(0, 0, L, Wd, MF['r'])
    holes = [rounded_rect(0, 0, MF['aperture'][0] + 1.0, MF['aperture'][1] + 1.0, 1.0, 4), circle(-MF['screw_dx'], 0, 1.9, 24), circle(MF['screw_dx'], 0, 1.9, 24)]
    return prism(o, holes, 0.0, 1.0)
