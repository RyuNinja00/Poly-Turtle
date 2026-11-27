"""Whole-assembly interference audit in the model frame (cad/01, cad/05, cad/08).
Cradle-drive STLs are in box coordinates: model = box - (54.5, 0, 113.498)."""
import sys, json, pickle, numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'build/cradle-drive/tools')); sys.path.insert(0, str(ROOT / 'build/lid'))
import meshkit as mk, columns
import printed_lid as P, extras as E
M2B = np.array([54.5, 0.0, 113.498])
H = 0.25

def tri(path, shift=0.0): return mk.read_stl(path) + shift
def shells_of(t):
    V = t.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3); V, T = mk.weld(V, T, 1e-5)
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]]])
    n, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(len(V), len(V))), directed=False)
    return [V[T[lab[T[:, 0]] == k]] for k in np.unique(lab[T[:, 0]])]
class Occ:
    def __init__(self, t):
        sh = shells_of(t); allv = t.reshape(-1, 3); lo = allv.min(0) - 1; hi = allv.max(0) + 1
        self.xs = np.arange(lo[0], hi[0], H); self.ys = np.arange(lo[1], hi[1], H); self.lo = lo
        self.iv = [columns.intervals(s, self.xs, self.ys, kmax=10) for s in sh]
        self.kd = cKDTree(np.unique(allv.round(4), axis=0))
    def inside(self, Pt):
        i = np.round((Pt[:, 0] - self.lo[0]) / H).astype(int); j = np.round((Pt[:, 1] - self.lo[1]) / H).astype(int)
        ok = (i >= 0) & (i < len(self.xs)) & (j >= 0) & (j < len(self.ys)); i = np.clip(i, 0, len(self.xs) - 1); j = np.clip(j, 0, len(self.ys) - 1)
        r = np.zeros(len(Pt), bool)
        for a, b in self.iv: r |= np.any((Pt[:, 2:3] >= a[i, j]) & (Pt[:, 2:3] <= b[i, j]), 1)
        return r & ok
def sample(t, step=0.6):
    """surface samples: vertices + triangle interior points"""
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    k = np.clip((area / step ** 2).astype(int), 0, 50)
    pts = [t.reshape(-1, 3)]
    rng = np.random.default_rng(0)
    for n in range(1, 51):
        m = k == n
        if not m.any(): continue
        u = rng.random((m.sum(), n, 2)); f = u.sum(2) > 1; u[f] = 1 - u[f]
        pts.append((a[m][:, None] + u[..., :1] * (b - a)[m][:, None] + u[..., 1:] * (c - a)[m][:, None]).reshape(-1, 3))
    return np.concatenate(pts)
def pair(name, A_tri, B_occ, res, note=''):
    pts = sample(A_tri); ins = B_occ.inside(pts); d, _ = B_occ.kd.query(pts[~ins]) if (~ins).any() else (np.array([99.0]), None)
    r = dict(points=int(len(pts)), inside=int(ins.sum()), min_gap_mm=round(float(d.min()), 2))
    if ins.any(): r['inside_bbox'] = [pts[ins].min(0).round(1).tolist(), pts[ins].max(0).round(1).tolist()]
    else: r['at'] = pts[~ins][int(np.argmin(d))].round(1).tolist()
    if note: r['note'] = note
    res[name] = r; print(name, r)

res = {}
C = ROOT / 'cad'
lid = tri(C / '08-printed-lid/08-Printed-lid.stl'); car = tri(C / '08-printed-lid/08c-feeder-carrier.stl')
box = tri(C / '04-Printable-box-PROXY.stl')
drive = {p.stem: tri(p, -M2B) for p in sorted((C / '07-cradle-drive').glob('07*.stl'))}
LID, BOX, CAR = Occ(lid), Occ(box), Occ(car)
# installed small parts
g = mk.read_stl(C / '08-printed-lid/08g-TPU-lid-gasket-3.5mm.stl') + [0, 0, 65.2 - 3.5]
plate_g = mk.read_stl(C / '08-printed-lid/08n-TPU-microfit-plate-gasket.stl') + [P.MF_AT['x'], P.MF_AT['y'], 132.54]
plate = mk.read_stl(C / '08-printed-lid/08m-microfit-2x6-plate.stl') + [P.MF_AT['x'], P.MF_AT['y'], 133.54]
# envelopes: 2x6 ear housing (seller 5557-3.0-2*R: 19.0 x 8.5, 17.3 tall) hanging 15.3 below the plate top
def boxtri(lo, hi):
    V, T = mk.box_mesh(lo, hi) if hasattr(mk, 'box_mesh') else (None, None)
    return V[T]
def cuboid(lo, hi):
    x0, y0, z0 = lo; x1, y1, z1 = hi
    V = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    F = [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]]
    return V[np.array(F)]
housing = cuboid((P.MF_AT['x'] - 9.5, -4.25, 135.54 - 15.3), (P.MF_AT['x'] + 9.5, 4.25, 135.54))
wires = cuboid((P.MF_AT['x'] - 9.5, -4.25, 135.54 - 25.0), (P.MF_AT['x'] + 9.5, 4.25, 135.54 - 15.3))
# PC4-M10 fitting envelope (hex 14 AF -> r 8.1, 5 mm; body r 6, 12 mm) outside the face, on the axis
def axcyl(u0, u1, r, n=32):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False); tris = []
    p0 = P.glob(u0, 0, 0); p1 = P.glob(u1, 0, 0)
    ring = lambda c: [c + r * (np.cos(t) * P.W + np.sin(t) * P.V_) for t in th]
    R0, R1 = ring(p0), ring(p1)
    for i in range(n):
        j = (i + 1) % n; tris += [[R0[i], R0[j], R1[j]], [R0[i], R1[j], R1[i]], [p0, R0[j], R0[i]], [p1, R1[i], R1[j]]]
    return np.array(tris)
uf = P.outlet_face()
fitting = np.concatenate([axcyl(uf + 0.05, uf + 5.0, 8.1), axcyl(uf + 5.0, uf + 17.0, 6.0)])
# spool envelope surface
SC = np.array([-6.072, 3.354]); th = np.linspace(0, 2 * np.pi, 720); yy = np.linspace(-39, 39, 40)
spool_pts = np.array([[SC[0] + 102.5 * np.cos(t), y, SC[1] + 102.5 * np.sin(t)] for t in th for y in yy])
def spool_gap(t):
    p = sample(t); m = np.abs(p[:, 1]) <= 39
    if not m.any(): return None
    r = np.hypot(p[m, 0] - SC[0], p[m, 2] - SC[1]) - 102.5; return round(float(r.min()), 2)

for k, t in drive.items():
    pair(f'drive {k} vs box proxy', t, BOX, res, 'proxy is a printable look-alike; the molded box is the authority')
    pair(f'drive {k} vs lid', t, LID, res); pair(f'drive {k} vs carrier', t, CAR, res)
pair('lid vs box proxy', lid, BOX, res, 'expected only at the rim: the proxy rim reaches Z 66.5, 1.3 mm past jojo\'s channel ceiling')
pair('carrier vs box proxy', car, BOX, res)
pair('TPU gasket 3.5 (installed) vs lid', g, LID, res, 'gasket top face touches the channel ceiling by design')
pair('plate gasket vs lid', plate_g, LID, res, 'sits on the vault top by design')
pair('Micro-Fit plate vs lid', plate, LID, res)
pair('2x6 housing envelope vs lid', housing, LID, res, 'passes the 25 x 13.5 opening')
pair('2x6 housing + wire bend vs carrier', np.concatenate([housing, wires]), CAR, res)
pair('PC4-M10 envelope vs lid', fitting, LID, res, 'hex seats on the bushing face')
res['spool gaps'] = {**{k: spool_gap(t) for k, t in drive.items()}, 'housing+wires': spool_gap(np.concatenate([housing, wires]))}
print('spool gaps', res['spool gaps'])
json.dump(res, open(HERE / 'assembly.json', 'w'), indent=1, default=float)
