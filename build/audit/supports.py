"""Unsupported-overhang scan in print orientation: a voxel needs support when the layer below,
grown by one layer height (45 deg), does not cover it. Usage: supports.py STL up_axis(+x/-x/+y/-y/+z/-z)"""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cradle-drive/tools')); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lid'))
import meshkit as mk, columns
from scipy import ndimage
def split(t):
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    V = t.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3); V, T = mk.weld(V, T, 1e-5)
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]]])
    n, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(len(V), len(V))), directed=False)
    return [V[T[lab[T[:, 0]] == k]] for k in np.unique(lab[T[:, 0]])]
def scan(path, up, h=0.2, shells=None):
    t = mk.read_stl(path); ax = 'xyz'.index(up[1]); sg = 1 if up[0] == '+' else -1
    other = [i for i in range(3) if i != ax]; t = t[:, :, other + [ax]] * np.array([1, 1, sg])
    V = t.reshape(-1, 3); lo, hi = V.min(0), V.max(0)
    xs = np.arange(lo[0], hi[0] + h, h); ys = np.arange(lo[1], hi[1] + h, h); zs = np.arange(lo[2] + h / 2, hi[2], h)
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    for part in split(t):                         # per shell: overlapping shells would break the in/out parity
        a, b = columns.intervals(part, xs, ys, kmax=16)
        for k in range(a.shape[2]):
            A = np.nan_to_num(a[:, :, k:k + 1], nan=1e9); B = np.nan_to_num(b[:, :, k:k + 1], nan=-1e9)
            occ |= (zs[None, None] >= A) & (zs[None, None] <= B)
    need = np.zeros_like(occ); st = np.ones((3, 3), bool)
    for k in range(1, len(zs)):
        sup = ndimage.binary_dilation(occ[:, :, k - 1], st)
        need[:, :, k] = occ[:, :, k] & ~sup
    lab, n = ndimage.label(need, np.ones((3, 3, 3)))
    out = []
    for i, s in enumerate(ndimage.find_objects(lab)):
        m = lab[s] == i + 1; area = m.any(2).sum() * h * h
        if area < 1.0: continue
        ii, jj, kk = np.nonzero(m)
        loc = np.array([xs[s[0]][ii].mean(), ys[s[1]][jj].mean(), zs[s[2]][kk].min()])
        g = np.zeros(3); g[other[0]], g[other[1]], g[ax] = loc[0], loc[1], sg * loc[2]
        out.append(dict(area_mm2=round(float(area), 1), at=g.round(1).tolist(), height_above_bed=round(float(loc[2] - lo[2]), 1)))
    return sorted(out, key=lambda d: -d['area_mm2'])
if __name__ == '__main__':
    r = scan(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.2)
    for d in r[:25]: print(d)
    print('total unsupported area', round(sum(d['area_mm2'] for d in r), 1))
