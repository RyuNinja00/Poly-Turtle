"""Coarse occupancy of the 08a lid body (z-ray parity), cached to occ.npz."""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
LO = np.array([-2.0, -46.0, 58.0]); H = 0.5; N = (214, 180, 110)

def build(stl=ROOT / 'cad/08-printed-lid/08a-lid-body.stl'):
    tri = mk.read_stl(stl)
    xs = LO[0] + H * np.arange(N[0]); ys = LO[1] + H * np.arange(N[1]); zs = LO[2] + H * np.arange(N[2])
    occ = np.zeros(N, bool)
    a, b, c = tri[:, 0, :2], tri[:, 1, :2], tri[:, 2, :2]
    for i, x in enumerate(xs):
        m = (tri[:, :, 0].min(1) <= x) & (tri[:, :, 0].max(1) >= x)
        T = tri[m]; A, B, C = T[:, 0], T[:, 1], T[:, 2]
        P = np.stack([np.full(len(ys), x), ys], 1)[:, None, :]
        d = (B[:, 1] - C[:, 1]) * (A[:, 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (A[:, 1] - C[:, 1])
        ok = np.abs(d) > 1e-12; d = np.where(ok, d, 1)
        l1 = ((B[:, 1] - C[:, 1]) * (P[..., 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (P[..., 1] - C[:, 1])) / d
        l2 = ((C[:, 1] - A[:, 1]) * (P[..., 0] - C[:, 0]) + (A[:, 0] - C[:, 0]) * (P[..., 1] - C[:, 1])) / d
        l3 = 1 - l1 - l2
        inside = ok & (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        zhit = l1 * A[:, 2] + l2 * B[:, 2] + l3 * C[:, 2]
        cnt = ((zhit[:, :, None] < zs[None, None, :]) & inside[:, :, None]).sum(1)
        occ[i] = cnt % 2 == 1
    np.savez_compressed(HERE / 'occ.npz', occ=occ)
    return occ

def lookup(occ, P):
    idx = np.round((np.asarray(P) - LO) / H).astype(int)
    ok = np.all((idx >= 0) & (idx < np.array(N)), 1)
    out = np.zeros(len(P), bool); out[ok] = occ[tuple(idx[ok].T)]; return out

if __name__ == '__main__':
    o = build(); print(o.mean())
