"""08 - Printed lid, rev 2 (uphill feeder): jojo's two-port PolyDryer lid + feeder hood.

Rev 2 re-poses the Smol + PREP (pose.py): the feeder is turned end for end and
tilted so filament travels UP it at ALPHA = 40 deg toward -X.  The inlet (PREP)
is the low +X end, just above the lid rim, where filament arrives from the +X
side of the spool through a curved guide.  The outlet is the high -X end and
leaves through a PC4-M10 boss in the hood's -X wall.

Parts (cad/01 / cad/05 model frame, Z up, mm):
  08a lid body  - Printables 1441905 (jojo) lid, cad/05 pocket clipped flush with
                  the plate top, old 4.3 mm outlet hole closed.  Jojo's triangles.
  08b hood      - roof-down print, bonded onto the 08a opening ring.  Outlet boss,
                  cable-gland hole, two roof screws.
  08c carrier   - under the Smol (replaces the BoxTurtle trayframe interface):
                  V1 heat-set inserts for the Smol's two downward bolts, PREP
                  block + M2 pilots, curved inlet guide, two towers to the roof.
08-Printed-lid-one-piece.stl = 08a + 08b as touching shells (slicers union them).
Run: clouds.py, occ.py, printed_lid.py, checks.py (packs the zip), render.py.
"""
import sys, json, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
from cliplid import RING_IN, RING_OUT
from pose import Pose

ALPHA = 40.0
INLET = (87.0, -5.48, 76.0)          # PREP entry point on the filament axis (u = -50)
POSE = Pose(ALPHA, INLET)
TF, A, V_, W = POSE.TF, POSE.A, POSE.V, POSE.W

PLATE_TOP = 111.588                  # flat top of the jojo plate (print-bed face)
ROOF_IN, ROOF_OUT = 155.0, 157.5     # Smol top 153.5 + 1.5
BOLTS = {'A': (-17.53, 25.47), 'B': (30.50, 25.47)}   # (u, w): the Smol's two downward bolts
BASE_V = 4.90
PREP_HOLES = [(-44.65, -2.83), (-44.65, 3.67)]         # D2F-type switch, screws along v
PREP_TOP_V = 9.90
INSERT_D, INSERT_L, CLEAR_D = 4.2, 5.5, 3.4            # V1 M3 heat-set insert
RELIEF_D = 3.2                                          # bolt-tail relief below the rail inserts
H, OFF = 0.4, 0.0137

# carrier, archived-local (u along travel, w, v = Smol base normal)
RAIL = dict(u=(-23.5, 36.5), w=(17.4, 32.5), v=(-9.5, BASE_V))
W_FLAT = 31.0                         # carrier's flat print face (global y plane through w = 31)
EAR_B = dict(u=(36.0, 48.3), v=(-9.5, 1.0))            # high (-X) end, under the Smol's end features
ARM = dict(u=(-49.4, -23.0), w=(6.9, 32.5), v=(-9.5, 1.2))   # low (+X) end, beside the inlet
PREP_BLOCK = dict(u=(-49.4, -36.8), w=(-6.6, 32.5), v=(PREP_TOP_V + 0.2, 16.0))
PREP_POST = dict(u=(-49.4, -36.8), w=(7.6, 32.5), v=(-9.5, 16.0))
GUIDE = dict(R=20.0, sweep=40.0, r_out=3.2, r_bore=1.2, mouth=2.6)
WEB = dict(u=(-58.0, -44.0), w=(-3.0, 7.4), v=(-9.5, -2.2))
TOWER_A_X = (90.0, 96.5)             # +X end, rises from the PREP post
TOWER_B_X = (5.6, 11.5)              # -X end, rises from ear B
OUTLET = dict(u_in=52.0, u_out=61.5, r=7.5, hole=9.0)    # PC4-M10 self-threads into Ø9
GLAND = dict(y=14.0, z=132.0, d=12.4)                   # M12 / PG7 in the +X end wall


def loc(g):
    X, Y, Z = g.X() - TF[0], g.Y() - TF[1], g.Z() - TF[2]
    return [(X * e[0] + Y * e[1] + Z * e[2]).astype(np.float32) for e in (A, W, V_)]

def lbox(L, d):
    lo = (d['u'][0], d['w'][0], d['v'][0]); hi = (d['u'][1], d['w'][1], d['v'][1])
    q = [np.abs(L[i] - (lo[i] + hi[i]) / 2) - (hi[i] - lo[i]) / 2 for i in range(3)]
    o = np.sqrt(sum(np.maximum(t, 0) ** 2 for t in q))
    return (o + np.minimum(np.maximum(np.maximum(q[0], q[1]), q[2]), 0)).astype(np.float32)

def lcyl(L, axis, c, r, t0, t1):
    """cylinder along local axis 0 (u) or 2 (v), centred at the other two coords c."""
    o = [k for k in (0, 1, 2) if k != axis]
    d = np.sqrt((L[o[0]] - c[0]) ** 2 + (L[o[1]] - c[1]) ** 2) - r
    return mk._combine(d, np.maximum(t0 - L[axis], L[axis] - t1))

def glob(u, w, v):
    return TF + u * A + w * W + v * V_

def arc_dist(L):
    """distance to the inlet-guide centreline: arc in the u-v plane (w = 0),
    tangent to the filament axis at u = -50 and curving down toward the spool."""
    R = GUIDE['R']; cu, cv = -50.0, -R
    du, dv = L[0] - cu, L[2] - cv
    phi = np.clip(np.arctan2(du, dv), -np.radians(GUIDE['sweep']), 0.0)
    qu, qv = cu + R * np.sin(phi), cv + R * np.cos(phi)
    return np.sqrt((L[0] - qu) ** 2 + L[1] ** 2 + (L[2] - qv) ** 2).astype(np.float32), phi

def mouth():
    s = -np.radians(GUIDE['sweep']); R = GUIDE['R']
    m = np.array([-50 + R * np.sin(s), -R + R * np.cos(s)])      # (u, v)
    t = np.array([np.cos(s), -np.sin(s)])                          # forward tangent (u, v)
    return m, t


def carrier(g):
    L = loc(g)
    body = mk.union(lbox(L, RAIL), lbox(L, dict(EAR_B, w=RAIL['w'])), lbox(L, ARM),
                    lbox(L, PREP_POST), lbox(L, PREP_BLOCK), lbox(L, WEB))
    d, _ = arc_dist(L)
    arc_side = (L[0] - (-50.0)).astype(np.float32)          # <= 0 on the curved side
    body = mk.union(body, mk.intersect(d - GUIDE['r_out'], arc_side), lcyl(L, 0, (0.0, 0.0), GUIDE['r_out'], -50.0, -46.0))
    y31, y17 = glob(0, W_FLAT + 1.5, 0)[1], glob(0, RAIL['w'][0], 0)[1]
    ta = mk.box(g, (TOWER_A_X[0], y31, 50), (TOWER_A_X[1], y17, ROOF_IN - 0.3))
    ta = mk.intersect(ta, (PREP_POST['v'][0] - L[2]).astype(np.float32), (PREP_POST['u'][0] - L[0]).astype(np.float32))
    tb = mk.box(g, (TOWER_B_X[0], y31, 50), (TOWER_B_X[1], y17, ROOF_IN - 0.3))
    tb = mk.intersect(tb, (EAR_B['v'][0] - L[2]).astype(np.float32), (L[0] - EAR_B['u'][1]).astype(np.float32))
    body = mk.union(body, ta, tb)
    # flat print face / side bounds along w (global y within the rail's w band; guide side open)
    yflat = glob(0, W_FLAT, 0)[1]
    body = mk.intersect(body, (yflat - g.Y()).astype(np.float32))
    cuts = [mk.intersect(d - GUIDE['r_bore'], arc_side - 0.01)]
    m, t = mouth()
    s = (L[0] - m[0]) * t[0] + (L[2] - m[1]) * t[1]              # along the guide at the mouth
    rad = np.sqrt((L[0] - (m[0] + s * t[0])) ** 2 + L[1] ** 2 + (L[2] - (m[1] + s * t[1])) ** 2)
    flare = GUIDE['r_bore'] + (GUIDE['mouth'] - GUIDE['r_bore']) * np.clip(-s / 4.0 + 0, 0, 1)
    cuts.append(mk._combine(rad - flare, np.maximum(-6 - s, s - 4)))
    for k, (u, w) in BOLTS.items():
        cuts.append(lcyl(L, 2, (u, w), INSERT_D / 2, BASE_V - INSERT_L, BASE_V + 1))
        cuts.append(lcyl(L, 2, (u, w), RELIEF_D / 2, -20, BASE_V))
    for u, w in PREP_HOLES:
        cuts.append(lcyl(L, 2, (u, w), 0.85, PREP_TOP_V, PREP_TOP_V + 6.5))
    # keep the filament path under the PREP lever clear (u -50..-30, r 1.6)
    cuts.append(lcyl(L, 0, (0.0, 0.0), GUIDE['r_bore'], -50.0, -30.0))
    for x, y in SCREWS.values():
        cuts.append(mk.cyl_z(g, x, y, INSERT_D / 2, ROOF_IN - 0.3 - INSERT_L, ROOF_IN + 1))
        cuts.append(mk.cyl_z(g, x, y, CLEAR_D / 2, ROOF_IN - 16, ROOF_IN + 1))
    return mk.subtract(body, *cuts)

_yA = glob(0, 24.2, 0)[1]
SCREWS = {'A': (sum(TOWER_A_X) / 2, _yA), 'B': (sum(TOWER_B_X) / 2, _yA)}

TABS = [((5.7, 10, PLATE_TOP - 3), (6.9, 22, PLATE_TOP + 1)),
        ((92.6, 10, PLATE_TOP - 3), (93.8, 22, PLATE_TOP + 1)),
        ((30, 29.1, PLATE_TOP - 3), (50, 30.3, PLATE_TOP + 1)),
        ((30, -38.3, PLATE_TOP - 3), (50, -37.1, PLATE_TOP + 1))]

def hood(g):
    L = loc(g)
    outer = mk.box(g, (RING_OUT[0], RING_OUT[2], PLATE_TOP), (RING_OUT[1], RING_OUT[3], ROOF_OUT))
    inner = mk.box(g, (RING_IN[0], RING_IN[2], PLATE_TOP - 5), (RING_IN[1], RING_IN[3], ROOF_IN))
    boss = lcyl(L, 0, (0.0, 0.0), OUTLET['r'], OUTLET['u_in'], OUTLET['u_out'])
    boss = mk.intersect(boss, (g.Z() - ROOF_OUT).astype(np.float32))
    body = mk.union(mk.subtract(outer, inner), boss, *[mk.box(g, lo, hi) for lo, hi in TABS])
    cuts = [mk.cyl_x(g, GLAND['y'], GLAND['z'], GLAND['d'] / 2, RING_IN[1] - 1, RING_OUT[1] + 1),
            lcyl(L, 0, (0.0, 0.0), OUTLET['hole'] / 2, OUTLET['u_in'] - 1, OUTLET['u_out'] + 1)]
    for x, y in SCREWS.values():
        cuts.append(mk.cyl_z(g, x, y, CLEAR_D / 2, ROOF_IN - 1, ROOF_OUT + 1))
        cuts.append(mk.cyl_z(g, x, y, 3.25, ROOF_OUT - 0.6, ROOF_OUT + 1))
    return mk.subtract(body, *cuts)


def mesh(fn, lo, hi):
    """Marching cubes (skimage, Lewiner) on the signed-distance grid: manifold
    where naive surface nets pinched thin features."""
    from skimage import measure
    g = mk.Grid(np.asarray(lo) - OFF, hi, H); s = fn(g)
    V, T, _, _ = measure.marching_cubes(s, 0.0, spacing=tuple(g.h))
    V = V + g.lo; T = T.astype(np.int64)
    r = mk.check_mesh(V, T)
    if r['volume'] < 0: T = T[:, ::-1]
    if r['edges_not_2']: raise RuntimeError('non-manifold mesh for ' + fn.__name__)
    return V, T, s, g

HOOD_BOX = ((-9, -44, PLATE_TOP - 4.5), (104, 36, ROOF_OUT + 1))
CAR_BOX = ((2, -40, 52), (102, 8, ROOF_IN + 1))

if __name__ == '__main__':
    out = ROOT / 'cad' / '08-printed-lid'; out.mkdir(exist_ok=True)
    import cliplid
    cliplid.ZCUT = PLATE_TOP + 0.012          # 12 um above the plate face (avoids a coplanar cut)
    Vl, Tl = cliplid.clipped_lid(ROOT / 'cad' / '05-Raised-lid-clearance-shell.stl')
    Vl, Tl = cliplid.plug_outlet(Vl, Tl)
    Vh, Th, sh, gh = mesh(hood, *HOOD_BOX)
    Vc, Tc, sc, gc = mesh(carrier, *CAR_BOX)
    rep = {}
    for n, (V, T) in dict(lid=(Vl, Tl), hood=(Vh, Th), carrier=(Vc, Tc)).items():
        rep[n] = mk.check_mesh(V, T); rep[n]['bbox'] = [V.min(0).round(2).tolist(), V.max(0).round(2).tolist()]
        print(n, rep[n])
    for f in out.glob('*.stl'): f.unlink()
    mk.write_stl(out / '08a-lid-body.stl', Vl, Tl); mk.write_stl(out / '08b-hood.stl', Vh, Th)
    mk.write_stl(out / '08c-feeder-carrier.stl', Vc, Tc)
    mk.write_stl(out / '08-Printed-lid-one-piece.stl', np.concatenate([Vl, Vh]), np.concatenate([Tl, Th + len(Vl)]))
    np.savez_compressed(HERE / 'sdf.npz', sh=sh, hlo=gh.lo, hh=gh.h, sc=sc, clo=gc.lo, ch=gc.h)
    rep['pose'] = dict(alpha_deg=ALPHA, inlet=list(INLET), TF=TF.round(4).tolist(), A=A.round(5).tolist(), V=V_.round(5).tolist())
    json.dump(rep, open(out / 'mesh-report.json', 'w'), indent=1)
