"""Thin-feature scan: voxelise a closed mesh (exact z-intervals on an h-grid),
open it with a ball of radius r; solid that disappears is thinner than ~2r."""
import sys, json, numpy as np
from pathlib import Path
from scipy import ndimage as ndi
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'build/cradle-drive/tools')); sys.path.insert(0, str(ROOT / 'build/lid'))
import meshkit as mk, columns

def shells(path):
    t = mk.read_stl(path); V = t.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3); V, T = mk.weld(V, T, 1e-5)
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]]])
    n, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(len(V), len(V))), directed=False)
    return [V[T[lab[T[:, 0]] == k]] for k in np.unique(lab[T[:, 0]])]

def scan(path, h=0.2, r=0.45, box=None):
    sh = shells(path); allv = np.concatenate([s.reshape(-1, 3) for s in sh])
    lo = allv.min(0) - 1; hi = allv.max(0) + 1
    if box is not None: lo = np.maximum(lo, box[0]); hi = np.minimum(hi, box[1])
    xs = np.arange(lo[0], hi[0], h); ys = np.arange(lo[1], hi[1], h); zs = np.arange(lo[2], hi[2], h)
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    for tri in sh:
        a, b = columns.intervals(tri, xs, ys, kmax=10); occ |= columns.zfield(a, b, zs) < 0
    k = int(np.ceil(r / h)); g = np.arange(-k, k + 1) * h
    ball = (g[:, None, None] ** 2 + g[None, :, None] ** 2 + g[None, None, :] ** 2) <= r * r
    thin = occ & ~ndi.binary_opening(occ, structure=ball)
    edt = ndi.distance_transform_edt(occ) * h
    lab, n = ndi.label(thin)
    out = []
    if n:
        sizes = ndi.sum(thin, lab, range(1, n + 1))
        for i in np.argsort(-sizes)[:40]:
            idx = np.argwhere(lab == i + 1)
            if len(idx) < 4: continue
            p = np.column_stack([xs[idx[:, 0]], ys[idx[:, 1]], zs[idx[:, 2]]])
            it = int(np.ceil((r + 0.6) / h))
            sl = tuple(slice(max(a - it - 1, 0), b + it + 2) for a, b in zip(idx.min(0), idx.max(0)))
            near = ndi.binary_dilation(lab[sl] == i + 1, iterations=it) & occ[sl]
            # a skin on a thick wall has deep solid right behind it; a real thin feature does not
            if min(p.max(0) - p.min(0)) <= 2.0 * h: continue      # 1-2 voxel sheet = surface speckle of the voxelisation
            out.append(dict(max_half_thickness_mm=round(float(edt[sl][near].max()), 2), voxels=int(len(idx)), volume_mm3=round(float(len(idx) * h ** 3), 2), center=p.mean(0).round(1).tolist(),
                            extent=(p.max(0) - p.min(0)).round(1).tolist()))
    return dict(file=str(Path(path).relative_to(ROOT)), solid_mm3=round(float(occ.sum() * h ** 3)), thin_mm3=round(float(thin.sum() * h ** 3), 2),
                min_feature_mm=2 * r, clusters=out)

if __name__ == '__main__':
    res = []
    jobs = [('cad/08-printed-lid/08c-feeder-carrier.stl', 0.2, None),
            ('cad/08-printed-lid/08m-microfit-2x6-plate.stl', 0.1, None),
            ('cad/07-cradle-drive/07d-Motor-bracket-cradle-key.stl', 0.15, None),
            ('cad/07-cradle-drive/07a-Roller-with-gear.stl', 0.15, None),
            ('cad/07-cradle-drive/07c-Pinion-17T-N20.stl', 0.1, None),
            ('cad/08-printed-lid/08-Printed-lid.stl', 0.3, (np.array([-118, -60, 100.0]), np.array([118, 60, 164.0]))),
            ('cad/08-printed-lid/08-Printed-lid.stl', 0.1, (np.array([80.0, 2, 59.5]), np.array([102.0, 44, 69.0]))),   # pogo pocket
            ('cad/08-printed-lid/08p-pogo-box-bar-print-in-place.stl', 0.1, (np.array([82.0, 0, 52.0]), np.array([104.0, 44, 61.0]))),
            ('cad/08-printed-lid/08q-TPU-pogo-bar-bumper-x2.stl', 0.1, None)]
    for p, h, box in jobs:
        r = scan(ROOT / p, h=h, r=0.45, box=box); res.append(r)
        print(r['file'], 'solid', r['solid_mm3'], 'thin', r['thin_mm3'])
        for c in r['clusters'][:8]: print('   ', c)
    json.dump(res, open(HERE / 'thin.json', 'w'), indent=1)
