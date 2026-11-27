"""Planar-region decimation: half-edge collapses that only remove vertices whose
whole 1-ring is flat (within TOL mm of a plane).  Geometry error <= TOL; the mesh
stays closed and 2-manifold (link condition + no normal flips are enforced)."""
import numpy as np


def decimate(V, T, tol=0.01, passes=12, min_cos=0.999, verbose=False):
    V = np.asarray(V, float); T = [list(t) for t in np.asarray(T)]
    alive = [True] * len(T)
    vf = [set() for _ in range(len(V))]
    for fi, t in enumerate(T):
        for v in t: vf[v].add(fi)

    def fnormal(t):
        n = np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]); L = np.linalg.norm(n)
        return n / L if L > 1e-14 else None

    for ps in range(passes):
        removed = 0; locked = np.zeros(len(V), bool)
        order = np.random.default_rng(ps).permutation(len(V))
        for v in order:
            if locked[v] or not vf[v]: continue
            faces = list(vf[v])
            ring = set()
            for fi in faces: ring.update(T[fi])
            ring.discard(v); ring = list(ring)
            if len(ring) < 3: continue
            P = V[ring + [v]]; c = P.mean(0)
            # plane through the ring (least squares)
            _, _, vt = np.linalg.svd(P - c, full_matrices=False); n = vt[2]
            if np.max(np.abs((P - c) @ n)) > tol: continue
            # try collapsing v onto each ring neighbour
            done = False
            for w in sorted(ring, key=lambda q: np.sum((V[q] - V[v]) ** 2)):
                # link condition: common neighbours of v and w must be exactly the 2 opposite vertices
                shared = [fi for fi in faces if w in T[fi]]
                if len(shared) != 2: continue
                opp = set()
                for fi in shared: opp.update(T[fi])
                opp -= {v, w}
                nw = set()
                for fi in vf[w]: nw.update(T[fi])
                nv = set(ring)
                if (nv & nw) - {v, w} != opp: continue
                ok = True; newt = {}
                for fi in faces:
                    if fi in shared: continue
                    t = T[fi]; t2 = [w if q == v else q for q in t]
                    n0 = fnormal(t); n1 = fnormal(t2)
                    if n0 is None or n1 is None or np.dot(n0, n1) < min_cos: ok = False; break
                    newt[fi] = t2
                if not ok: continue
                for fi in shared:
                    alive[fi] = False
                    for q in T[fi]: vf[q].discard(fi)
                for fi, t2 in newt.items():
                    T[fi] = t2; vf[w].add(fi)
                vf[v] = set()
                for q in ring: locked[q] = True
                removed += 1; done = True; break
        if verbose: print('pass', ps, 'removed', removed)
        if removed < 0.002 * len(V): break
    T = np.array([t for t, a in zip(T, alive) if a])
    used = np.unique(T); r = -np.ones(len(V), int); r[used] = np.arange(len(used))
    return V[used], r[T]
