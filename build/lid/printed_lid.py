"""08 - Printed lid (rev 1): jojo's two-port PolyDryer lid + feeder hood.

Parts (all in the archived model frame, the same frame as cad/01 and cad/05):
  08a lid body   - Printables 1441905 (jojo) lid with the cad/05 pocket clipped
                   flush at the plate top: rim, gasket channel, latches, ports
                   and the 4.3 mm outlet hole are the original triangles.
  08b hood       - roof-down print; butt-welded onto the 08a opening ring.
                   Carries the PREP switch, a cable-gland hole and two roof
                   screws for the feeder carrier.
  08c carrier    - replaces the BoxTurtle trayframe interface under the Smol:
                   the Smol's two downward M3 bolts thread into V1 heat-set
                   inserts; two towers hang the carrier from the hood roof.
08-Printed-lid-one-piece.stl is 08a + 08b as two touching shells (slicers union them).
Run: clouds.py, printed_lid.py, checks.py (packs cad/08-Printed-lid.zip), render.py.
"""
import sys, json, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
from cliplid import clip_below, cap_ring, RING_IN, RING_OUT

PLATE_TOP = 111.588           # flat top of the jojo plate (print-bed face)
ROOF_IN, ROOF_OUT = 144.5, 147.0
# Smol frame (from cad/01): axis a (filament travel), base normal v, w = v x a
TF = np.array([50.82170486028815, -1.52379502811359, 104.38142041181])
A = np.array([0.90750213, 0.0, -0.42004747])
V_ = np.array([0.41978434, -0.03539018, 0.90693365])
W = np.cross(V_, A)
BOLTS = {'A': (-17.53, 25.47), 'B': (30.50, 25.47)}   # (u, w) of the two downward Smol bolts
BASE_V = 4.90                                          # Smol contact face at the bolts
PREP_HOLES = [(-44.65, -2.83), (-44.65, 3.67)]         # (u, w), D2F-type, axis along v
PREP_TOP_V = 9.90
INSERT_D, INSERT_L, CLEAR_D = 4.2, 5.5, 3.4            # V1 BOM M3 heat-set insert
GLAND = dict(y=20.0, z=133.0, d=12.4)                  # M12 / PG7 gland in the -x end wall
TOWERS = dict(A=(16.6, 23.4), B=(94.7, 99.1))          # x ranges; y 17.4..31.0
TOWER_Y = (17.4, 31.0)
SCREW_XY = {k: ((x0 + x1) / 2, 24.2) for k, (x0, x1) in TOWERS.items()}
H = 0.4
OFF = 0.0137                  # keep grid planes off the design planes


def loc(g):
    X, Y, Z = g.X() - TF[0], g.Y() - TF[1], g.Z() - TF[2]
    return [(X * e[0] + Y * e[1] + Z * e[2]).astype(np.float32) for e in (A, W, V_)]

def lbox(L, lo, hi):
    q = [np.abs(L[i] - (lo[i] + hi[i]) / 2) - (hi[i] - lo[i]) / 2 for i in range(3)]
    o = np.sqrt(sum(np.maximum(t, 0) ** 2 for t in q))
    return (o + np.minimum(np.maximum(np.maximum(q[0], q[1]), q[2]), 0)).astype(np.float32)

def lcyl_v(L, u, w, r, v0, v1):
    d = np.sqrt((L[0] - u) ** 2 + (L[1] - w) ** 2) - r
    return mk._combine(d, np.maximum(v0 - L[2], L[2] - v1))

def half(f):  # half-space helper: f <= 0 inside
    return f.astype(np.float32)


# ------------------------------------------------------------------ 08c carrier
RAIL = dict(u=(-23.5, 36.5), w=(17.4, 31.0), v=(-9.5, BASE_V))
EAR_A = dict(u=(-33.6, -23.0), v=(-9.5, 1.2))
EAR_B = dict(u=(36.0, 47.5), v=(-9.5, 1.0))

def carrier(g):
    L = loc(g)
    rail = lbox(L, (RAIL['u'][0], RAIL['w'][0], RAIL['v'][0]), (RAIL['u'][1], RAIL['w'][1], RAIL['v'][1]))
    ea = lbox(L, (EAR_A['u'][0], RAIL['w'][0], EAR_A['v'][0]), (EAR_A['u'][1], RAIL['w'][1], EAR_A['v'][1]))
    eb = lbox(L, (EAR_B['u'][0], RAIL['w'][0], EAR_B['v'][0]), (EAR_B['u'][1], RAIL['w'][1], EAR_B['v'][1]))
    body = mk.union(rail, ea, eb)
    for k, (x0, x1) in TOWERS.items():
        tw = mk.box(g, (x0, TOWER_Y[0], 60), (x1, TOWER_Y[1], ROOF_IN - 0.3))
        # tower stands on its ear: keep only the part above the ear's bottom plane
        tw = mk.intersect(tw, half(EAR_A['v'][0] - L[2]))
        body = mk.union(body, tw)
    body = mk.intersect(body, half(g.Y() - TOWER_Y[1]), half(TOWER_Y[0] - g.Y()))   # flat print face
    cuts = []
    for k, (u, w) in BOLTS.items():
        cuts.append(lcyl_v(L, u, w, INSERT_D / 2, BASE_V - INSERT_L, BASE_V + 1))
        cuts.append(lcyl_v(L, u, w, CLEAR_D / 2, -20, BASE_V))           # bolt tail relief, open below
    for k, (x, y) in SCREW_XY.items():
        cuts.append(mk.cyl_z(g, x, y, INSERT_D / 2, ROOF_IN - 0.3 - INSERT_L, ROOF_IN + 1))
        cuts.append(mk.cyl_z(g, x, y, CLEAR_D / 2, ROOF_IN - 16, ROOF_IN + 1))
    return mk.subtract(body, *cuts)


# ------------------------------------------------------------------ 08b hood
PREP_BLOCK = dict(u=(-49.4, -36.8), w=(-6.6, 6.9), v=(PREP_TOP_V + 0.2, 60))
TABS = [((5.7, 10, PLATE_TOP - 3), (6.9, 22, PLATE_TOP + 1)),          # -x edge, clear of the gland
        ((5.7, -34, PLATE_TOP - 3), (6.9, -22, PLATE_TOP + 1)),
        ((10, -38.3, PLATE_TOP - 3), (22, -37.1, PLATE_TOP + 1)),        # -y edge
        ((88, -38.3, PLATE_TOP - 3), (97, -37.1, PLATE_TOP + 1))]

def hood(g):
    L = loc(g)
    outer = mk.box(g, (RING_OUT[0], RING_OUT[2], PLATE_TOP), (RING_OUT[1], RING_OUT[3], ROOF_OUT))
    inner = mk.box(g, (RING_IN[0], RING_IN[2], PLATE_TOP - 5), (RING_IN[1], RING_IN[3], ROOF_IN))
    body = mk.subtract(outer, inner)
    prep = lbox(L, (PREP_BLOCK['u'][0], PREP_BLOCK['w'][0], PREP_BLOCK['v'][0]), (PREP_BLOCK['u'][1], PREP_BLOCK['w'][1], PREP_BLOCK['v'][1]))
    prep = mk.intersect(prep, half(g.Z() - ROOF_IN - 0.5))
    body = mk.union(body, prep, *[mk.box(g, lo, hi) for lo, hi in TABS])
    # roof pads around the carrier screws (inside), keep roof 2.5 elsewhere
    cuts = [mk.cyl_x(g, GLAND['y'], GLAND['z'], GLAND['d'] / 2, RING_OUT[0] - 1, RING_IN[0] + 1)]
    for u, w in PREP_HOLES:
        cuts.append(lcyl_v(L, u, w, 0.85, PREP_TOP_V, PREP_TOP_V + 9))     # M2 self-tap pilots
    for k, (x, y) in SCREW_XY.items():
        cuts.append(mk.cyl_z(g, x, y, CLEAR_D / 2, ROOF_IN - 1, ROOF_OUT + 1))
        cuts.append(mk.cyl_z(g, x, y, 3.25, ROOF_OUT - 0.6, ROOF_OUT + 1))  # shallow seat for washer
    return mk.subtract(body, *cuts)


def mesh(fn, lo, hi):
    """Surface nets can pinch two sheets into one edge on a 2-cell feature (the
    M2 pilots).  Shift the grid by a sub-cell offset until the mesh is manifold."""
    for off in (OFF, 0.1919, 0.0711, 0.1234, 0.2531, 0.3127):
        g = mk.Grid(np.asarray(lo) - off, hi, H); s = fn(g)
        V, T = mk.surface_nets(s, g)
        if mk.check_mesh(V, T)['edges_not_2'] == 0: return V, T, s, g
    raise RuntimeError('no manifold mesh for ' + fn.__name__)


def stl(path, V, T):
    mk.write_stl(path, V, T)


if __name__ == '__main__':
    out = ROOT / 'cad' / '08-printed-lid'; out.mkdir(exist_ok=True)
    from cliplid import clipped_lid
    import cliplid
    cliplid.ZCUT = PLATE_TOP + 0.012   # 12 um above the plate face (coplanar cut avoided)
    Vl, Tl = clipped_lid(ROOT / 'cad' / '05-Raised-lid-clearance-shell.stl')
    Vh, Th, sh, gh = mesh(hood, (0, -44, PLATE_TOP - 4.5), (104, 36, ROOF_OUT + 1))
    Vc, Tc, sc, gc = mesh(carrier, (13, 15, 70), (102, 33, ROOF_IN + 1))
    rep = {}
    for n, (V, T) in dict(lid=(Vl, Tl), hood=(Vh, Th), carrier=(Vc, Tc)).items():
        rep[n] = mk.check_mesh(V, T); rep[n]['bbox'] = [V.min(0).round(2).tolist(), V.max(0).round(2).tolist()]
        print(n, rep[n])
    stl(out / '08a-lid-body.stl', Vl, Tl); stl(out / '08b-hood.stl', Vh, Th); stl(out / '08c-feeder-carrier.stl', Vc, Tc)
    Vj = np.concatenate([Vl, Vh]); Tj = np.concatenate([Tl, Th + len(Vl)])
    stl(out / '08-Printed-lid-one-piece.stl', Vj, Tj)
    np.savez_compressed(HERE / 'sdf.npz', sh=sh, hlo=gh.lo, hh=gh.h, sc=sc, clo=gc.lo, ch=gc.h)
    json.dump(rep, open(out / 'mesh-report.json', 'w'), indent=1)
