"""08 - Printed lid, rev 3: one-piece, support-free, faceted canopy.

Same functional layout as rev 2 (uphill feeder, inlet + PREP low at +X, outlet
high at -X), retuned so the whole lid prints in ONE piece, rim down, without
supports:

* Jojo's lid (Printables 1441905) is kept triangle-for-triangle below Z 102:
  rim, gasket channel, side latches.  Above Z 102 the end caps (latch bars,
  finger slots) are rebuilt from jojo's own geometry (exact in Z).
* The flat plate is replaced by a vault: 45-degree chamfers from the walls to a
  40 mm wide flat (a short bridge).  The feeder sits under a 45-degree
  frustum.  ALPHA = 45 deg makes the feeder's top and outlet faces parallel to
  the frustum faces, so the outlet fitting screws in square to its face.
* Every downward-facing surface is >= 45 deg or a bridge <= 40 mm.

Parts (cad/01 / cad/05 model frame, Z up, mm):
  08-Printed-lid.stl          one print: jojo base (exact) + canopy (touching shells)
  08c-feeder-carrier.stl      under the Smol; PREP block, inlet guide, two side pads
Run: clouds.py, printed_lid.py, occ.py, checks.py (packs the zip), render.py.
"""
import sys, json, numpy as np
from pathlib import Path
from scipy import ndimage as ndi
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import cliplid, earcut, columns
import extras as E
from decimate import decimate
from pose import Pose

# ------------------------------------------------------------------ pose and layout
ALPHA = 45.0
INLET = (86.5, -5.48, 74.0)          # PREP entry on the filament axis (u = -50)
POSE = Pose(ALPHA, INLET)
TF, A, V_, W = POSE.TF, POSE.A, POSE.V, POSE.W

ZC = 102.0                           # jojo kept exactly below this plane
Z_WALL = 106.5                       # inner chamfers start here at the side walls
VAULT_IN = 129.0                     # inner flat of the vault (~36 mm bridge)
T_V = 3.54                           # vertical skin thickness (2.5 mm normal on 45-deg faces)
FRUSTUM = dict(z=158.5, x=(36.1, 61.1), y=(-28.7, 6.3))   # inner top of the feeder canopy (>= 2 mm normal to the Smol)
X_END = 100.5                        # jojo inner end walls
X_CLIFF = 102.5                      # canopy may rise over the +X end-cap bar up to here
I_XMAX = 97.4                        # canopy cavity stops here at +X: >= 2.9 mm end wall (module is below Z 101 there)
Z_CAP = 111.588                      # jojo end-cap top
H = 0.4

BOLTS = {'A': (-17.53, 25.47), 'B': (30.50, 25.47)}   # Smol's two downward bolts (u, w)
BASE_V = 4.90
PREP_HOLES = [(-44.65, -2.83), (-44.65, 3.67)]
PREP_TOP_V = 9.90
INSERT_D, INSERT_L, CLEAR_D, RELIEF_D = 4.2, 5.5, 3.4, 3.2

RAIL = dict(u=(-23.5, 36.5), w=(17.4, 40.0), v=(-9.5, BASE_V))
Y_FLAT = -39.1                       # carrier's flat print face (lid inner wall is at y -40.6)
BOSS_Y = -39.7                       # lid standoffs at the two wall screws: 0.6 mm drop-in gap to the carrier
EAR_B = dict(u=(36.0, 43.0), w=(17.4, 40.0), v=(-9.5, 1.0))
ARM = dict(u=(-49.4, -23.0), w=(6.9, 40.0), v=(-9.5, 1.2))
PREP_POST = dict(u=(-49.4, -36.8), w=(7.6, 40.0), v=(-9.5, 16.0))
PREP_BLOCK = dict(u=(-49.4, -36.8), w=(-6.6, 40.0), v=(PREP_TOP_V + 0.2, 16.0))
GUIDE = dict(R=20.0, sweep=40.0, r_out=3.8, r_bore=2.15, mouth=3.0, collar=4.6, fin=4.0)   # Ø4.3 bore takes a 4/2 mm PTFE liner
STRAIGHT = dict(r_out=3.2, r_bore=1.2)                                 # past the liner stop (u -50): bare filament under PREP
WEB = dict(u=(-58.0, -44.0), w=(-3.0, 7.4), v=(-9.5, -2.2))
WEB_FOOT = dict(u=(-58.0, -49.4), w=(7.4, 40.0), v=(-9.5, -2.2))   # carries the web down to the -Y print face
PADS = {'A': 4.0, 'B': 30.0}        # rail screws (u): M3 through the -Y wall into rail inserts
PAD_V = (-9.5 + BASE_V) / 2
MF_AT = dict(x=-20.0, y=0.0)                               # Micro-Fit 3.0 2x6 bulkhead plate on the vault flat (extras.MF)
OUTLET = dict(r=7.5, hole=11.2, out=5.2)                   # boss proud of the -X canopy face; threaded bushing (extras) fills the hole
GROOVE = dict(z=102.8, depth=0.8)                          # V shadow line around the canopy base


def loc(X, Y, Z):
    X, Y, Z = X - TF[0], Y - TF[1], Z - TF[2]
    return [(X * e[0] + Y * e[1] + Z * e[2]).astype(np.float32) for e in (A, W, V_)]

def glob(u, w, v):
    return TF + u * A + w * W + v * V_

def lbox(L, d):
    lo = (d['u'][0], d['w'][0], d['v'][0]); hi = (d['u'][1], d['w'][1], d['v'][1])
    q = [np.abs(L[i] - (lo[i] + hi[i]) / 2) - (hi[i] - lo[i]) / 2 for i in range(3)]
    o = np.sqrt(sum(np.maximum(t, 0) ** 2 for t in q))
    return (o + np.minimum(np.maximum(np.maximum(q[0], q[1]), q[2]), 0)).astype(np.float32)

def lcyl(L, axis, c, r, t0, t1):
    o = [k for k in (0, 1, 2) if k != axis]
    d = np.sqrt((L[o[0]] - c[0]) ** 2 + (L[o[1]] - c[1]) ** 2) - r
    return mk._combine(d, np.maximum(t0 - L[axis], L[axis] - t1))

def arc_dist(L):
    R = GUIDE['R']; cu, cv = -50.0, -R
    du, dv = L[0] - cu, L[2] - cv
    phi = np.clip(np.arctan2(du, dv), -np.radians(GUIDE['sweep']), 0.0)
    qu, qv = cu + R * np.sin(phi), cv + R * np.cos(phi)
    return np.sqrt((L[0] - qu) ** 2 + L[1] ** 2 + (L[2] - qv) ** 2).astype(np.float32)

def mouth():
    s = -np.radians(GUIDE['sweep']); R = GUIDE['R']
    return np.array([-50 + R * np.sin(s), -R + R * np.cos(s)]), np.array([np.cos(s), -np.sin(s)])

def pad_screw(u0):
    p = glob(u0, 30.0, PAD_V)
    return float(p[0]), float(p[2])


# ------------------------------------------------------------------ 08c carrier
def carrier(g):
    L = loc(g.X(), g.Y(), g.Z())
    body = mk.union(lbox(L, RAIL), lbox(L, EAR_B), lbox(L, ARM), lbox(L, PREP_POST), lbox(L, PREP_BLOCK), lbox(L, WEB))
    d = arc_dist(L); arc_side = (L[0] + 50.0).astype(np.float32)
    body = mk.union(body, mk.intersect(d - GUIDE['r_out'], arc_side), lcyl(L, 0, (0.0, 0.0), STRAIGHT['r_out'], -50.0, -46.0))
    m, t = mouth()
    s_ = (L[0] - m[0]) * t[0] + (L[2] - m[1]) * t[1]
    rad_ = np.sqrt((L[0] - (m[0] + s_ * t[0])) ** 2 + L[1] ** 2 + (L[2] - (m[1] + s_ * t[1])) ** 2)
    body = mk.union(body, mk._combine(rad_ - GUIDE['collar'], np.maximum(-4.0 - s_, s_ - 3.0)))   # mouth collar
    # print supports built in (carrier prints on its -Y face, +w is down): a 4 mm fin under the guide from the bed to the tube,
    # ending 1 mm outside the mouth, and the web carried down to the bed
    d_uv = arc_dist(np.stack([L[0], np.zeros_like(L[1]), L[2]]))
    fin = np.maximum.reduce([d_uv - GUIDE['fin'] / 2, -1.0 - s_, GUIDE['r_out'] - 0.5 - L[1], L[1] - 40.0]).astype(np.float32)
    body = mk.union(body, fin, lbox(L, WEB_FOOT))
    body = mk.intersect(body, (Y_FLAT - g.Y()).astype(np.float32))          # flat print face
    cuts = [mk.intersect(d - GUIDE['r_bore'], arc_side - 0.01), lcyl(L, 0, (0.0, 0.0), STRAIGHT['r_bore'], -50.0, -30.0)]
    m, t = mouth()
    s = (L[0] - m[0]) * t[0] + (L[2] - m[1]) * t[1]
    rad = np.sqrt((L[0] - (m[0] + s * t[0])) ** 2 + L[1] ** 2 + (L[2] - (m[1] + s * t[1])) ** 2)
    flare = GUIDE['r_bore'] + (GUIDE['mouth'] - GUIDE['r_bore']) * np.clip(-s / 4.0, 0, 1)
    cuts.append(mk._combine(rad - flare, np.maximum(-6 - s, s - 4)))
    for u, w in BOLTS.values():
        cuts.append(lcyl(L, 2, (u, w), INSERT_D / 2, BASE_V - INSERT_L, BASE_V + 1))
        cuts.append(lcyl(L, 2, (u, w), RELIEF_D / 2, -20, BASE_V))
    for u, w in PREP_HOLES:
        cuts.append(lcyl(L, 2, (u, w), 0.85, PREP_TOP_V, PREP_TOP_V + 6.5))
    for u0 in PADS.values():                                  # inserts along -Y, from the wall side
        x, z = pad_screw(u0)
        cuts.append(mk.cyl_y(g, x, z, INSERT_D / 2, Y_FLAT - 1, Y_FLAT + INSERT_L))
        cuts.append(mk.cyl_y(g, x, z, CLEAR_D / 2, Y_FLAT - 1, Y_FLAT + 12))
    return mk.subtract(body, *cuts)


# ------------------------------------------------------------------ jojo base
def jojo_source():
    tri = mk.read_stl(ROOT / 'cad' / '05-Raised-lid-clearance-shell.stl')
    V = tri.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3)
    return mk.weld(V, T, 1e-4)

def clip_cap(V, T, z):
    V, T = cliplid.clip_below(V, T, z); V, T = mk.weld(V, T, 1e-5)
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    T = np.concatenate([T, earcut.cap(V, T, z)])
    V, T = cliplid.plug_outlet(V, T)
    used = np.unique(T); r = -np.ones(len(V), int); r[used] = np.arange(len(used))
    return V[used], r[T]

def base():
    V, T = jojo_source(); return clip_cap(V, T, ZC)

def endcap_tri():
    """jojo up to its plate top (the cad/05 pocket clipped off), for the end caps."""
    V, T = jojo_source(); return clip_cap(V, T, Z_CAP + 0.012)


# ------------------------------------------------------------------ canopy (heightmap design)
def plan(xs, ys, Vb, Tb):
    """2D masks at the clip plane from the base cap: solid ring, outline, interior I."""
    from matplotlib.path import Path
    cap_t = Tb[np.all(np.abs(Vb[Tb][:, :, 2] - ZC) < 1e-6, 1)]
    X, Y = np.meshgrid(xs, ys, indexing='ij'); pts = np.column_stack([X.ravel(), Y.ravel()])
    solid = np.zeros(len(pts), bool)
    for t in cap_t:                                         # rasterise the cap triangles
        P = Vb[t][:, :2]; lo, hi = P.min(0), P.max(0)
        m = (pts[:, 0] >= lo[0] - 1e-9) & (pts[:, 0] <= hi[0] + 1e-9) & (pts[:, 1] >= lo[1] - 1e-9) & (pts[:, 1] <= hi[1] + 1e-9)
        if m.any(): solid[m] |= Path(P).contains_points(pts[m], radius=1e-9) | Path(P[::-1]).contains_points(pts[m], radius=1e-9)
    solid = solid.reshape(X.shape)
    outline = ndi.binary_fill_holes(solid)
    air = outline & ~solid
    lab, n = ndi.label(air); sizes = ndi.sum(air, lab, range(1, n + 1))
    I = lab == (1 + int(np.argmax(sizes)))
    I &= (np.abs(X) <= X_END) & (X <= I_XMAX)
    return solid, outline, I, X, Y

def sd2(mask, h):
    return (ndi.distance_transform_edt(~mask) - ndi.distance_transform_edt(mask)) * h + np.where(mask, h / 2, -h / 2)

def canopy_heights(X, Y, I, outline, h):
    dI = ndi.distance_transform_edt(I) * h
    c_v = np.minimum(Z_WALL + dI, VAULT_IN)
    dx = np.maximum(np.maximum(FRUSTUM['x'][0] - X, X - FRUSTUM['x'][1]), 0)
    dy = np.maximum(np.maximum(FRUSTUM['y'][0] - Y, Y - FRUSTUM['y'][1]), 0)
    c_f = FRUSTUM['z'] - np.maximum(dx, dy)
    c = np.where(I, np.maximum(c_v, c_f), -1e3)
    # outer skin: 45-degree offset of the ceiling, carried over the walls
    r = int(np.ceil(10.0 / h)); k = np.arange(-r, r + 1) * h
    K = -np.sqrt(k[:, None] ** 2 + k[None, :] ** 2)
    top = ndi.grey_dilation(np.where(I, c + T_V, -1e3), structure=K, mode='nearest')
    top = np.where(outline, np.maximum(top, ZC + 1.0), ZC)          # every wall pixel gets a top
    # soften the creases (outer surface only; it faces up when printed rim-down)
    ts = ndi.gaussian_filter(top, 2.0)
    top = np.where(outline, np.maximum(ts, np.where(I, c + T_V - 0.6, top - 0.8)), -1e3)
    return c, top

def canopy(g, Vb, Tb, Vj, Tj):
    xs, ys, zs = g.xs, g.ys, g.zs
    solid, outline, I, X, Y = plan(xs, ys, Vb, Tb)
    c, top = canopy_heights(X, Y, I, outline, H)
    allowed = (outline & (np.abs(X) <= X_CLIFF)) | ((X > X_END - 0.5) & (X <= X_CLIFF) & (np.abs(Y) <= 44.5))   # cliff wall sits on the +X bar
    end = np.abs(X) > X_END
    Z = zs[None, None, :]
    # canopy solid that does not stand on the base (the +X strip between the vault and the bar) starts on a 45-degree underside
    d_base = ndi.distance_transform_edt(~solid) * H
    zmin = np.where(end, Z_CAP - 0.6, np.where(I, ZC - 0.6, ZC - 0.6 + d_base))[:, :, None]
    f_new = np.maximum(np.maximum(sd2(allowed, H)[:, :, None], zmin - Z), Z - top[:, :, None]).astype(np.float32)
    f_cav = np.maximum(sd2(I, H)[:, :, None], Z - c[:, :, None]).astype(np.float32)
    f = np.maximum(f_new, -f_cav)
    # jojo end caps above the clip, exact in Z, |x| > 99.5 only
    trij = Vj[Tj]
    lo, hi = columns.intervals(trij, xs, ys)
    fj = columns.zfield(lo, hi, zs)
    fj[np.abs(xs) <= 99.5] = 1e3
    fj = np.maximum(fj, (ZC - 0.6) - Z)
    port = mk._combine(np.sqrt((g.X() + 100.0) ** 2 + g.Y() ** 2) - 4.6, np.maximum(ZC - 0.6 - g.Z(), g.Z() - Z_CAP))
    f = np.minimum(f, np.minimum(fj, port))                 # jojo's old -X port is closed
    # shadow line: a 45-degree V-groove just above the clip plane hides the base/canopy seam
    so = sd2(outline, H)[:, :, None]
    groove = (np.abs(Z - GROOVE['z']) - GROOVE['depth']) - so
    groove = np.where((np.abs(xs) <= 99.5)[:, None, None], groove, 1e3).astype(np.float32)
    f = np.maximum(f, -groove)
    # features
    L = loc(g.X(), g.Y(), g.Z())
    uf = outlet_u()
    boss = lcyl(L, 0, (0.0, 0.0), OUTLET['r'], uf - 1.0, outlet_face() - 0.3)
    f = np.minimum(f, mk.intersect(boss, (zs.max() - 1 - g.Z()).astype(np.float32) * -1))
    holes = [lcyl(L, 0, (0.0, 0.0), OUTLET['hole'] / 2, uf - 3, uf + 20),
             mk.box(g, (MF_AT['x'] - E.MF['aperture'][0] / 2, MF_AT['y'] - E.MF['aperture'][1] / 2, 100), (MF_AT['x'] + E.MF['aperture'][0] / 2, MF_AT['y'] + E.MF['aperture'][1] / 2, 200))]
    for sx in (-1, 1):
        holes.append(mk.cyl_z(g, MF_AT['x'] + sx * E.MF['screw_dx'], MF_AT['y'], E.MF['screw_d'] / 2, 100, 200))
    for u0 in PADS.values():
        x, z = pad_screw(u0)
        holes.append(mk.cyl_y(g, x, z, CLEAR_D / 2, -60, Y_FLAT + 0.2))
    for u0 in PADS.values():                                 # standoffs from the -Y wall to the carrier face
        x, z = pad_screw(u0)
        f = np.minimum(f, mk.cyl_y(g, x, z, 4.5, -44.0, BOSS_Y))
    f = mk.subtract(f, *holes)
    return f, dict(c=c, top=top, I=I, outline=outline, xs=xs, ys=ys)

def outlet_face():
    """u of the fitting face (outer end of the boss / threaded bushing)"""
    return outlet_u() + T_V / np.sqrt(2) + OUTLET['out']

def outlet_u():
    """u where the filament axis meets the -X canopy face (inner surface)."""
    us = np.linspace(20, 80, 6001); P = np.array([glob(u, 0, 0) for u in us])
    dx = np.maximum(np.maximum(FRUSTUM['x'][0] - P[:, 0], P[:, 0] - FRUSTUM['x'][1]), 0)
    dy = np.maximum(np.maximum(FRUSTUM['y'][0] - P[:, 1], P[:, 1] - FRUSTUM['y'][1]), 0)
    cf = FRUSTUM['z'] - np.maximum(dx, dy)
    return float(us[np.argmax(P[:, 2] > cf)])


class Grid:
    def __init__(self, lo, hi, h):
        self.lo = np.asarray(lo, float); self.h = np.array([h, h, h])
        self.xs = np.arange(lo[0], hi[0] + h / 2, h); self.ys = np.arange(lo[1], hi[1] + h / 2, h); self.zs = np.arange(lo[2], hi[2] + h / 2, h)
    def X(self): return self.xs[:, None, None].astype(np.float32)
    def Y(self): return self.ys[None, :, None].astype(np.float32)
    def Z(self): return self.zs[None, None, :].astype(np.float32)


def mc(f, g):
    """Marching cubes, then weld exactly as a slicer will see the STL (float32)."""
    from skimage import measure
    # keep grid nodes >= 0.01 away from the zero level so no MC vertex sits on a node:
    # otherwise neighbouring vertices collapse in float32 and leave degenerate triangles
    f = np.where(f >= 0, np.maximum(f, 0.01), np.minimum(f, -0.01)).astype(np.float32)
    Vm, Tm, _, _ = measure.marching_cubes(np.ascontiguousarray(f), 0.0, spacing=tuple(g.h))
    Vm = (Vm + g.lo).astype(np.float32)
    Vu, inv = np.unique(Vm, axis=0, return_inverse=True); Tm = inv.reshape(-1)[Tm].astype(np.int64)
    Tm = Tm[(Tm[:, 0] != Tm[:, 1]) & (Tm[:, 1] != Tm[:, 2]) & (Tm[:, 0] != Tm[:, 2])]
    Vm = Vu.astype(np.float64)
    r = mk.check_mesh(Vm, Tm)
    if r['volume'] < 0: Tm = Tm[:, ::-1]
    if r['edges_not_2']: raise RuntimeError(f"non-manifold: {r['edges_not_2']} edges")
    return Vm, Tm


OFF = 0.0137
CANOPY_BOX = ((-118.6 - OFF, -59.0 - OFF, ZC - 1.4 - OFF), (118.6, 59.0, FRUSTUM['z'] + T_V + 12))
CAR_BOX = ((2 - OFF, -46 - OFF, 52 - OFF), (102, 8, 160))

if __name__ == '__main__':
    out = ROOT / 'cad' / '08-printed-lid'; out.mkdir(exist_ok=True)
    for f in out.glob('*'): f.unlink()
    Vb, Tb = base(); Vj, Tj = endcap_tri()
    g = Grid(*CANOPY_BOX, H)
    f, hm = canopy(g, Vb, Tb, Vj, Tj)
    Vt, Tt = mc(f, g)
    gc = Grid(*CAR_BOX, H)
    sc = carrier(gc); Vc, Tc = mc(sc, gc)
    Vt, Tt = decimate(Vt, Tt, passes=30); Vc, Tc = decimate(Vc, Tc, passes=30)
    uf = outlet_u()
    Vs, Ts = E.outlet_bushing(TF, A, uf - 0.6, outlet_face())
    rep = {}
    for n, (V, T) in dict(base=(Vb, Tb), canopy=(Vt, Tt), bushing=(Vs, Ts), carrier=(Vc, Tc)).items():
        rep[n] = mk.check_mesh(V, T); rep[n]['bbox'] = [V.min(0).round(2).tolist(), V.max(0).round(2).tolist()]
        print(n, rep[n])
    mk.write_stl(out / '08-Printed-lid.stl', *E.merge((Vb, Tb), (Vt, Tt), (Vs, Ts)))
    mk.write_stl(out / '08c-feeder-carrier.stl', Vc, Tc)
    mk.write_stl(HERE / 'base.stl', Vb, Tb)              # occ.py input (jojo base only)
    gk, ginfo = E.gaskets(Vb[Tb])
    for hgt, (V, T) in gk.items():
        mk.write_stl(out / f'08g-TPU-lid-gasket-{hgt:.1f}mm.stl', V, T); rep[f'gasket_{hgt}'] = mk.check_mesh(V, T)
    for name, (V, T) in {'08h-TPU-outlet-washer.stl': E.tpu_washer(), '08m-microfit-2x6-plate.stl': E.mf_plate(),
                         '08n-TPU-microfit-plate-gasket.stl': E.mf_gasket()}.items():
        mk.write_stl(out / name, V, T); rep[name] = mk.check_mesh(V, T)
    np.savez_compressed(HERE / 'sdf.npz', sl=f, llo=g.lo, lh=g.h, sc=sc, clo=gc.lo, ch=gc.h,
                        c=hm['c'], top=hm['top'], I=hm['I'], xs=hm['xs'], ys=hm['ys'])
    rep['pose'] = dict(alpha_deg=ALPHA, inlet=list(INLET), TF=TF.round(4).tolist(), A=A.round(5).tolist(), V=V_.round(5).tolist())
    rep['outlet_u'] = outlet_u()
    json.dump(rep, open(out / 'mesh-report.json', 'w'), indent=1)
