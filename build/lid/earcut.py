"""Planar cap for a mesh clipped at z = const: boundary loops -> triangles.

Small ear-clipping triangulator for polygons with holes (holes joined to the
outer ring by bridge edges).  Vertices are mesh indices, so the cap shares
the clip edges exactly and the result stays watertight."""
import numpy as np


def _cx(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def _area(P):
    return 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])


def _seg_hits(P, a, b, ring):
    """does segment a-b cross any edge of ring (excluding edges touching a or b)?"""
    A, B = P[a], P[b]
    for i in range(len(ring)):
        c, d = ring[i], ring[(i + 1) % len(ring)]
        if len({a, b, c, d}) < 4 or (P[c] == A).all() or (P[d] == A).all(): continue
        C, D = P[c], P[d]
        d1 = _cx(B - A, C - A); d2 = _cx(B - A, D - A)
        d3 = _cx(D - C, A - C); d4 = _cx(D - C, B - C)
        if d1 * d2 < 0 and d3 * d4 < 0: return True
    return False


def bridge(P, outer, holes):
    ring = list(outer)
    for h in sorted(holes, key=lambda h: -P[h][:, 0].max()):
        h = list(h); k = int(np.argmax(P[h][:, 0])); h = h[k:] + h[:k]; hv = h[0]
        # nearest visible outer vertex
        cand = sorted(range(len(ring)), key=lambda i: np.sum((P[ring[i]] - P[hv]) ** 2))
        for i in cand:
            if not _seg_hits(P, ring[i], hv, ring) and not _seg_hits(P, ring[i], hv, h): break
        ov = ring[i]
        ring = ring[:i + 1] + h + [hv, ov] + ring[i + 1:]
    return ring


def earclip(P, ring):
    idx = list(ring); tris = []; guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1; n = len(idx); found = False
        Q = P[idx]
        for i in range(n):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % n]
            pa, pb, pc = P[a], P[b], P[c]
            cr = _cx(pb - pa, pc - pb)
            if cr <= 1e-12: continue
            # any other vertex inside or on the triangle (strict-ish)?
            m = np.ones(n, bool); m[[i - 1 if i else n - 1, i, (i + 1) % n]] = False
            R = Q[m]
            same = (np.all(R == pa, 1) | np.all(R == pb, 1) | np.all(R == pc, 1))
            R = R[~same]
            if len(R):
                w1 = _cx(pb - pa, R - pa); w2 = _cx(pc - pb, R - pb); w3 = _cx(pa - pc, R - pc)
                if np.any((w1 >= -1e-12) & (w2 >= -1e-12) & (w3 >= -1e-12)): continue
            tris.append((a, b, c)); idx.pop(i); found = True; break
        if not found:
            # remove a collinear vertex as a zero-area ear (keeps edges shared)
            for i in range(n):
                a, b, c = idx[i - 1], idx[i], idx[(i + 1) % n]
                if abs(_cx(P[b] - P[a], P[c] - P[b])) <= 1e-9:
                    tris.append((a, b, c)); idx.pop(i); found = True; break
        if not found: raise RuntimeError('ear clipping stuck')
    tris.append(tuple(idx))
    return tris


def cap(V, T, z, normal_up=True):
    """Triangulate the open boundary of (V, T) lying on the plane z."""
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    key = np.sort(e, 1); _, inv, c = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    oe = e[c[inv] == 1]
    assert np.allclose(V[np.unique(oe), 2], z), 'open edges off the plane'
    nxt = {b: a for a, b in oe}                     # reversed: cap runs against the kept faces
    loops, seen = [], set()
    for s in list(nxt):
        if s in seen: continue
        L = [s]; seen.add(s); k = nxt[s]
        while k != s: L.append(k); seen.add(k); k = nxt[k]
        loops.append(L)
    P = V[:, :2]
    outers = [L for L in loops if _area(P[L]) > 0]; holes = [L for L in loops if _area(P[L]) < 0]
    from matplotlib.path import Path
    tris = []
    for o in outers:
        pth = Path(P[o]); mine = [h for h in holes if pth.contains_point(P[h[0]])]
        ring = bridge(P, o, [np.array(h) for h in mine]) if mine else o
        tris += earclip(P, ring)
    Tc = np.array(tris)
    if not normal_up: Tc = Tc[:, ::-1]
    return Tc
