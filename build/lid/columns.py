"""Exact z-intervals of a closed mesh along vertical columns (ray parity)."""
import numpy as np

def intervals(tri, xs, ys, kmax=6):
    """Return lo, hi arrays (nx, ny, kmax) of solid z-intervals (nan where none)."""
    lo = np.full((len(xs), len(ys), kmax), np.nan); hi = lo.copy()
    for i, x in enumerate(xs):
        m = (tri[:, :, 0].min(1) <= x) & (tri[:, :, 0].max(1) >= x)
        if not m.any(): continue
        T = tri[m]; A, B, C = T[:, 0], T[:, 1], T[:, 2]
        P = np.stack([np.full(len(ys), x), ys], 1)[:, None, :]
        d = (B[:, 1] - C[:, 1]) * (A[:, 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (A[:, 1] - C[:, 1])
        ok = np.abs(d) > 1e-12; d = np.where(ok, d, 1)
        l1 = ((B[:, 1] - C[:, 1]) * (P[..., 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (P[..., 1] - C[:, 1])) / d
        l2 = ((C[:, 1] - A[:, 1]) * (P[..., 0] - C[:, 0]) + (A[:, 0] - C[:, 0]) * (P[..., 1] - C[:, 1])) / d
        l3 = 1 - l1 - l2
        inside = ok & (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        z = np.where(inside, l1 * A[:, 2] + l2 * B[:, 2] + l3 * C[:, 2], np.nan)
        z = np.sort(z, 1)
        for j in range(len(ys)):
            h = z[j][~np.isnan(z[j])]
            if len(h) == 0: continue
            h = np.unique(np.round(h, 6))           # shared-edge double hits
            if len(h) % 2: continue                  # grazing column: skip
            k = min(len(h) // 2, kmax)
            lo[i, j, :k] = h[0:2 * k:2]; hi[i, j, :k] = h[1:2 * k:2]
    return lo, hi

def zfield(lo, hi, zs):
    """signed distance along z (negative inside) for a stack of intervals."""
    f = np.full(lo.shape[:2] + (len(zs),), 1e3, np.float32)
    for k in range(lo.shape[2]):
        a = lo[:, :, k:k + 1]; b = hi[:, :, k:k + 1]
        g = np.maximum(a - zs[None, None, :], zs[None, None, :] - b)
        g = np.where(np.isnan(g), 1e3, g)
        f = np.minimum(f, g.astype(np.float32))
    return f
