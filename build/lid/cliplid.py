"""Clip the jojo-derived lid (cad/05) at a horizontal plane and cap the cut.

Keeps every triangle of the Printables 1441905 lid (rim, gasket channel,
latches, ports, outlet hole) untouched below ZCUT; only the old clearance
pocket above ZCUT is removed.  The cut through the pocket walls is a
rectangular ring, capped with exact triangle strips, so the result is a
closed, watertight mesh with no approximation of the seal geometry.
"""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk

ZCUT = 113.0
RING_OUT = (2.0, 102.0, -42.0, 34.0)
RING_IN = (4.5, 99.5, -39.5, 31.5)


def clip_below(V, T, z0):
    cache = {}; NV = [V]; n = [len(V)]
    def cut(a, b):
        k = (min(a, b), max(a, b))
        if k not in cache:
            pa, pb = V[a], V[b]; t = (z0 - pa[2]) / (pb[2] - pa[2])
            p = pa + t * (pb - pa); p[2] = z0
            cache[k] = n[0]; NV.append(p[None]); n[0] += 1
        return cache[k]
    out = []
    below = V[:, 2] <= z0
    for tri in T:
        b = below[tri]
        if b.all(): out.append(tri); continue
        if not b.any(): continue
        # rotate so pattern is canonical
        for r in range(3):
            t = np.roll(tri, -r); bb = below[t]
            if b.sum() == 1 and bb[0]:
                a, c, d = t; out.append([a, cut(a, c), cut(a, d)]); break
            if b.sum() == 2 and bb[0] and bb[1]:
                a, c, d = t; p, q = cut(c, d), cut(a, d)
                out += [[a, c, p], [a, p, q]]; break
    return np.concatenate(NV), np.array(out)


def side_of(p, rect):
    x0, x1, y0, y1 = rect; tol = 1e-3; s = set()
    if abs(p[1] - y0) < tol: s.add(0)
    if abs(p[0] - x1) < tol: s.add(1)
    if abs(p[1] - y1) < tol: s.add(2)
    if abs(p[0] - x0) < tol: s.add(3)
    return s


def cap_ring(V, ids):
    """Triangulate the ring between RING_OUT and RING_IN at the cut plane."""
    P = V[ids]
    corners_o = [(RING_OUT[0], RING_OUT[2]), (RING_OUT[1], RING_OUT[2]), (RING_OUT[1], RING_OUT[3]), (RING_OUT[0], RING_OUT[3])]
    corners_i = [(RING_IN[0], RING_IN[2]), (RING_IN[1], RING_IN[2]), (RING_IN[1], RING_IN[3]), (RING_IN[0], RING_IN[3])]
    tris = []
    for s in range(4):
        def chain(rect, corners):
            a = np.array(corners[s]); b = np.array(corners[(s + 1) % 4]); d = b - a; L = np.linalg.norm(d)
            sel = [(float((P[k, :2] - a) @ d / L / L), ids[k]) for k in range(len(ids)) if s in side_of(P[k], rect)]
            sel.sort(); return sel
        O = chain(RING_OUT, corners_o); I = chain(RING_IN, corners_i)
        assert abs(O[0][0]) < 1e-6 and abs(O[-1][0] - 1) < 1e-6, ('outer chain', s, O[:2], O[-2:])
        assert abs(I[0][0]) < 1e-6 and abs(I[-1][0] - 1) < 1e-6, ('inner chain', s)
        i = j = 0
        while i < len(O) - 1 or j < len(I) - 1:
            if j == len(I) - 1 or (i < len(O) - 1 and O[i + 1][0] <= I[j + 1][0]):
                tris.append([O[i][1], O[i + 1][1], I[j][1]]); i += 1
            else:
                tris.append([O[i][1], I[j + 1][1], I[j][1]]); j += 1
    T = np.array(tris)
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])[:, 2]
    T[n < 0] = T[n < 0][:, ::-1]            # cap faces +Z (top of the kept solid)
    return T


def clipped_lid(src):
    tri = mk.read_stl(src)
    V = tri.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3)
    V, T = mk.weld(V, T, 1e-4)
    V, T = clip_below(V, T, ZCUT)
    V, T = mk.weld(V, T, 1e-5)
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    e = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1)
    u, c = np.unique(e, axis=0, return_counts=True)
    bnd = np.unique(u[c == 1])
    assert np.allclose(V[bnd, 2], ZCUT), 'open edges off the cut plane'
    T = np.concatenate([T, cap_ring(V, bnd)])
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    return V[used], remap[T]


if __name__ == '__main__':
    V, T = clipped_lid(HERE.parents[1] / 'cad' / '05-Raised-lid-clearance-shell.stl')
    print(mk.check_mesh(V, T), V.min(0), V.max(0))
