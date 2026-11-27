"""Planar slice of a closed mesh -> closed polylines (xy)."""
import numpy as np

def slice_loops(tri, z0):
    s = tri[:, :, 2] - z0
    m = (s.min(1) < 0) & (s.max(1) > 0)
    segs = []
    for t, d in zip(tri[m], s[m]):
        pts = [tuple(np.round((t[i] + d[i] / (d[i] - d[j]) * (t[j] - t[i]))[:2], 6)) for i, j in ((0, 1), (1, 2), (2, 0)) if (d[i] < 0) != (d[j] < 0)]
        if len(pts) == 2 and pts[0] != pts[1]: segs.append(pts)
    adj = {}
    for a, b in segs:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    seen = set(); loops = []
    for a, b in segs:
        if (a, b) in seen or (b, a) in seen: continue
        L = [a, b]; seen.add((a, b)); prev, cur = a, b
        while True:
            nx = [q for q in adj[cur] if q != prev and (cur, q) not in seen and (q, cur) not in seen]
            if not nx: break
            q = nx[0]; seen.add((cur, q)); prev, cur = cur, q
            if q == L[0]: break
            L.append(q)
        loops.append(np.array(L))
    return loops

def area(P):
    return 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
