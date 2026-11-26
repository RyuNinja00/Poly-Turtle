"""Clearance and assembly checks for the 08 printed lid (writes checks.json)."""
import sys, json, pickle, numpy as np
from pathlib import Path
from scipy.ndimage import map_coordinates
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import printed_lid as P

D = np.load(HERE / 'sdf.npz')
def sample(name, pts):
    s, lo, h = D['s' + name[0]], D[name[0] + 'lo'], D[name[0] + 'h']
    idx = ((pts - lo) / h).T
    return map_coordinates(s, idx, order=1, mode='nearest')

def local(X):
    d = X - P.TF; return np.stack([d @ P.A, d @ P.W, d @ P.V_], -1)

clouds = pickle.load(open(HERE / 'clouds.pkl', 'rb'))
smol, prep = clouds['smol'], clouds['prep']
Ls = local(smol)
iface = (Ls[:, 1] > 16.0) & (Ls[:, 2] < P.BASE_V + 0.05) & (Ls[:, 0] > -34) & (Ls[:, 0] < 48)
res = {}
def clr(tag, name, pts):
    d = sample(name, pts); i = int(np.argmin(d))
    res[tag] = dict(min_mm=round(float(d[i]), 2), at=pts[i].round(1).tolist(), n=int(len(pts)))
clr('hood_vs_smol', 'hood', smol)
clr('hood_vs_prep', 'hood', prep)
clr('carrier_vs_smol(excl. replaced trayframe interface)', 'carrier', smol[~iface])
clr('carrier_vs_prep', 'carrier', prep)
res['replaced_interface_points'] = int(iface.sum())

Vh = mk.read_stl(ROOT / 'cad/08-printed-lid/08b-hood.stl').reshape(-1, 3)
Vc = mk.read_stl(ROOT / 'cad/08-printed-lid/08c-feeder-carrier.stl').reshape(-1, 3)
Vh = np.unique(Vh.round(3), axis=0); Vc = np.unique(Vc.round(3), axis=0)
clr('carrier_vs_hood', 'hood', Vc[::3])

# spool envelope (cad/01 frame): centre (x, z) = (-6.072, 3.354), R 102.5, |y| <= 39
def spool(V):
    m = np.abs(V[:, 1]) <= 39.0
    r = np.hypot(V[m, 0] + 6.072, V[m, 2] - 3.354) - 102.5
    i = int(np.argmin(r)); return dict(min_mm=round(float(r[i]), 2), at=V[m][i].round(1).tolist())
res['hood_vs_spool'] = spool(Vh); res['carrier_vs_spool'] = spool(Vc)

# lid body occupancy by +z ray parity
tri = mk.read_stl(ROOT / 'cad/08-printed-lid/08a-lid-body.stl')
a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]; e1, e2 = b - a, c - a
def inside_lid(pts):
    out = np.zeros(len(pts), bool)
    hz = np.cross(np.array([0, 0, 1.0]), e2); det = (e1 * hz).sum(1); ok = np.abs(det) > 1e-12
    for s in range(0, len(pts), 400):
        p = pts[s:s + 400, None, :]; sv = p - a[None]
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        u = inv * (sv * hz[None]).sum(-1); q = np.cross(sv, e1[None]); v = inv * q[..., 2]; t = inv * (e2[None] * q).sum(-1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0)
        out[s:s + 400] = hit.sum(1) % 2 == 1
    return out
below = Vh[Vh[:, 2] < P.PLATE_TOP - 0.05]
res['hood_below_plate_inside_lid'] = int(inside_lid(below).sum()); res['hood_below_plate_vertices'] = int(len(below))
cs = Vc[::4]; res['carrier_inside_lid'] = int(inside_lid(cs).sum()); res['carrier_vertices_tested'] = int(len(cs))

# carrier / Smol module drops in vertically through the lid opening
opening = (P.RING_IN[0], P.RING_IN[1], P.RING_IN[2], P.RING_IN[3])
fp = np.concatenate([Vc, smol])
res['module_footprint_xy'] = [fp[:, 0].min().round(2), fp[:, 0].max().round(2), fp[:, 1].min().round(2), fp[:, 1].max().round(2)]
res['module_fits_opening'] = bool(fp[:, 0].min() > opening[0] and fp[:, 0].max() < opening[1] and fp[:, 1].min() > opening[2] and fp[:, 1].max() < opening[3])
# nothing hangs from the hood over the module footprint except the towers' own screws
res['prep_block_x_max'] = float(np.round((P.TF + P.PREP_BLOCK['u'][1] * P.A + P.PREP_BLOCK['v'][0] * P.V_)[0], 2))
res['bolt_insert_axes'] = {k: (P.TF + u * P.A + w * P.W + P.BASE_V * P.V_).round(2).tolist() for k, (u, w) in P.BOLTS.items()}
res['roof_screws_xy'] = {k: list(v) for k, v in P.SCREW_XY.items()}
for k, v in res.items(): print(k, v)
json.dump(res, open(ROOT / 'cad/08-printed-lid/checks.json', 'w'), indent=1, default=float)

import zipfile
with zipfile.ZipFile(ROOT / 'cad/08-Printed-lid.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted((ROOT / 'cad/08-printed-lid').iterdir()): z.write(f, f.name)
