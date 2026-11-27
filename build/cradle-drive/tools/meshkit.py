"""Small dependency-free (numpy/matplotlib) solid modelling kit.

Signed distance fields (negative inside) combined with min/max booleans,
meshed with naive surface nets into watertight triangle meshes, plus exact
tube meshes and binary STL I/O.  Units: mm.
"""
import numpy as np
from matplotlib.path import Path as MPath


# ---------------------------------------------------------------- grids
class Grid:
    def __init__(self, lo, hi, h):
        h = np.broadcast_to(np.asarray(h, float), (3,)).copy()
        lo = np.asarray(lo, float); hi = np.asarray(hi, float)
        n = np.ceil((hi - lo) / h).astype(int) + 1
        self.lo, self.h, self.n = lo, h, n
        self.x = lo[0] + h[0] * np.arange(n[0])
        self.y = lo[1] + h[1] * np.arange(n[1])
        self.z = lo[2] + h[2] * np.arange(n[2])

    def X(self): return self.x[:, None, None]
    def Y(self): return self.y[None, :, None]
    def Z(self): return self.z[None, None, :]


# ---------------------------------------------------------------- SDF ops
def union(*a):
    out = a[0]
    for b in a[1:]: out = np.minimum(out, b)
    return out

def subtract(a, *b):
    out = a
    for c in b: out = np.maximum(out, -c)
    return out

def intersect(*a):
    out = a[0]
    for b in a[1:]: out = np.maximum(out, b)
    return out

def _combine(d_in_plane, d_axis):
    o = np.sqrt(np.maximum(d_in_plane, 0) ** 2 + np.maximum(d_axis, 0) ** 2)
    return (o + np.minimum(np.maximum(d_in_plane, d_axis), 0)).astype(np.float32)

def box(g, lo, hi):
    lo = np.asarray(lo, float); hi = np.asarray(hi, float); c = (lo + hi) / 2; e = (hi - lo) / 2
    qx = np.abs(g.X() - c[0]) - e[0]; qy = np.abs(g.Y() - c[1]) - e[1]; qz = np.abs(g.Z() - c[2]) - e[2]
    o = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
    return (o + np.minimum(np.maximum(np.maximum(qx, qy), qz), 0)).astype(np.float32)

def cyl_y(g, x0, z0, r, y0, y1):
    d = np.sqrt((g.X() - x0) ** 2 + (g.Z() - z0) ** 2) - r
    dy = np.maximum(y0 - g.Y(), g.Y() - y1)
    return _combine(d, dy)

def cyl_x(g, y0, z0, r, x0, x1):
    d = np.sqrt((g.Y() - y0) ** 2 + (g.Z() - z0) ** 2) - r
    dx = np.maximum(x0 - g.X(), g.X() - x1)
    return _combine(d, dx)

def cyl_z(g, x0, y0, r, z0, z1):
    d = np.sqrt((g.X() - x0) ** 2 + (g.Y() - y0) ** 2) - r
    dz = np.maximum(z0 - g.Z(), g.Z() - z1)
    return _combine(d, dz)

def poly_sdf2(px, pz, poly):
    """signed distance on the (px, pz) mesh to a closed polygon (N,2)."""
    P = np.stack(np.meshgrid(px, pz, indexing='ij'), -1).reshape(-1, 2)
    a = poly; b = np.roll(poly, -1, 0)
    best = np.full(len(P), np.inf)
    for s in range(0, len(a), 64):
        A = a[s:s + 64][None]; B = b[s:s + 64][None]; Q = P[:, None]
        ab = B - A; t = np.clip(((Q - A) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-12), 0, 1)
        d = np.linalg.norm(Q - (A + t[..., None] * ab), axis=-1).min(1)
        best = np.minimum(best, d)
    inside = MPath(poly).contains_points(P)
    return np.where(inside, -best, best).reshape(len(px), len(pz))

def extrude_y(g, poly, y0, y1):
    d = poly_sdf2(g.x, g.z, poly)[:, None, :]
    return _combine(d, np.maximum(y0 - g.Y(), g.Y() - y1))


# ---------------------------------------------------------------- meshing
def surface_nets(sdf, g):
    """Naive surface nets.  sdf must be positive on the grid boundary."""
    s = sdf.astype(np.float64)
    nx, ny, nz = s.shape
    inside = s < 0
    acc = np.zeros((nx - 1, ny - 1, nz - 1, 3)); cnt = np.zeros((nx - 1, ny - 1, nz - 1))

    def edge(axis):
        sl0 = [slice(None)] * 3; sl1 = [slice(None)] * 3
        sl0[axis] = slice(0, -1); sl1[axis] = slice(1, None)
        a = s[tuple(sl0)]; b = s[tuple(sl1)]
        cross = (a < 0) != (b < 0)
        t = np.where(cross, a / np.where(cross, a - b, 1), 0)
        return cross, t, a

    edges = []
    for axis in range(3):
        cross, t, a = edge(axis)
        idx = np.argwhere(cross)
        tt = t[cross]
        p = idx.astype(float); p[:, axis] += tt
        others = [k for k in range(3) if k != axis]
        for d0 in (0, 1):
            for d1 in (0, 1):
                c = idx.copy(); c[:, others[0]] -= d0; c[:, others[1]] -= d1
                ok = np.all((c >= 0) & (c < np.array([nx - 1, ny - 1, nz - 1])), 1)
                np.add.at(acc, tuple(c[ok].T), p[ok])
                np.add.at(cnt, tuple(c[ok].T), 1)
        edges.append((axis, idx, a[cross]))
    active = cnt > 0
    vid = -np.ones(cnt.shape, np.int64); vid[active] = np.arange(active.sum())
    verts = acc[active] / cnt[active][:, None]
    verts = g.lo + verts * g.h
    quads = []
    for axis, idx, aval in edges:
        others = [k for k in range(3) if k != axis]
        u, v = others
        if axis == 1: u, v = 2, 0     # keep right-handed (u, v, axis)
        n = np.array([nx - 1, ny - 1, nz - 1])
        def cell(du, dv):
            c = idx.copy(); c[:, u] -= du; c[:, v] -= dv; return c
        cs = [cell(1, 1), cell(0, 1), cell(0, 0), cell(1, 0)]
        ok = np.ones(len(idx), bool)
        for c in cs: ok &= np.all((c >= 0) & (c < n), 1)
        q = np.stack([vid[tuple(c[ok].T)] for c in cs], 1)
        flip = aval[ok] >= 0          # outside at the low end -> normal points to -axis
        q[flip] = q[flip][:, ::-1]
        quads.append(q)
    q = np.concatenate(quads)
    tri = np.concatenate([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
    return verts, tri


# ---------------------------------------------------------------- exact meshes
def tube_y(r_out, r_in, y0, y1, x0=0.0, z0=0.0, n=128):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rings = []
    for r, y in [(r_out, y0), (r_out, y1), (r_in, y1), (r_in, y0)]:
        rings.append(np.column_stack([x0 + r * np.cos(t), np.full(n, y), z0 + r * np.sin(t)]))
    V = np.concatenate(rings); tris = []
    i = np.arange(n); j = (i + 1) % n
    def strip(a, b, flip=False):
        A = a * n; B = b * n
        t1 = np.column_stack([A + i, B + i, B + j]); t2 = np.column_stack([A + i, B + j, A + j])
        T = np.concatenate([t1, t2]); return T[:, ::-1] if flip else T
    tris = [strip(0, 1), strip(1, 2), strip(2, 3), strip(3, 0)]
    return V, np.concatenate(tris)


# ---------------------------------------------------------------- mesh utils
def check_mesh(V, T):
    e = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1)
    _, c = np.unique(e, axis=0, return_counts=True)
    d = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    _, cd = np.unique(d, axis=0, return_counts=True)
    vol = volume(V, T)
    return dict(tris=len(T), edges_not_2=int((c != 2).sum()), directed_dupes=int((cd > 1).sum()), volume=vol)

def volume(V, T):
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6)

def _float32_clean(V, T):
    """Weld exactly as a slicer reads a binary STL (float32) and drop triangles that
    collapse there; keep the result only if it stays 2-manifold."""
    V32 = np.asarray(V, np.float32); u, inv = np.unique(V32, axis=0, return_inverse=True)
    T2 = inv.reshape(-1)[np.asarray(T)]
    keep = (T2[:, 0] != T2[:, 1]) & (T2[:, 1] != T2[:, 2]) & (T2[:, 0] != T2[:, 2])
    if keep.all(): return V, T
    e = np.sort(np.concatenate([T2[keep][:, [0, 1]], T2[keep][:, [1, 2]], T2[keep][:, [2, 0]]]), 1)
    _, c = np.unique(e, axis=0, return_counts=True)
    if (c != 2).any(): return V, T
    return u.astype(float), T2[keep]

def write_stl(path, V, T, name=b'poly-turtle'):
    V, T = _float32_clean(V, T)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    n = np.cross(b - a, c - a); n /= np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    out = np.zeros(len(T), dt); out['n'] = n; out['v'] = np.stack([a, b, c], 1)
    with open(path, 'wb') as f:
        f.write(name.ljust(80, b' ')[:80]); f.write(np.uint32(len(T)).tobytes()); f.write(out.tobytes())

def read_stl(path):
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    d = np.fromfile(path, offset=84, dtype=dt)
    return d['v'].reshape(-1, 3, 3).astype(float)

def weld(V, T, tol=1e-6):
    key = np.round(V / tol).astype(np.int64)
    _, inv, = np.unique(key, axis=0, return_inverse=True)[0:2]
    u, first = np.unique(inv, return_index=True)
    return V[first], inv[T]

def transform(V, R=np.eye(3), t=np.zeros(3)):
    return V @ np.asarray(R).T + t


# ---------------------------------------------------------------- gears
def involute_gear(m, z, pa_deg=20.0, backlash=0.1, clearance=0.25, n_flank=14, bore=None):
    """Closed polygon (N,2) of a spur gear centred at the origin."""
    pa = np.deg2rad(pa_deg)
    rp = m * z / 2; rb = rp * np.cos(pa); ra = rp + m; rf = rp - (1 + clearance) * m
    # half tooth angle at pitch circle (thinned by backlash/2 per flank)
    s = np.pi * m / 2 - backlash
    inv = lambda a: np.tan(a) - a
    half = s / (2 * rp) + inv(pa)          # polar angle of flank at base circle from tooth centre
    r0 = max(rb, rf)
    rr = np.linspace(r0, ra, n_flank)
    alpha = np.arccos(np.clip(rb / rr, -1, 1))
    phi = half - inv(alpha)                # angle of flank point from tooth centre
    flank = np.column_stack([rr, phi])
    pts = []
    pitch = 2 * np.pi / z
    for k in range(z):
        c = k * pitch
        right = [(r, c - p) for r, p in flank]          # rising flank
        left = [(r, c + p) for r, p in flank[::-1]]
        # root: from previous tooth's left base to this tooth's right base along rf
        a_start = c - pitch + flank[0, 1]
        a_end = c - flank[0, 1]
        root = [(rf, a) for a in np.linspace(a_start, a_end, 6)[1:-1]]
        if rf < rb:
            root = [(rf, a_start)] + root + [(rf, a_end)]
        tip = [(ra, a) for a in np.linspace(c - flank[-1, 1], c + flank[-1, 1], 4)[1:-1]]
        seg = root + right + tip + left
        pts.extend(seg)
    P = np.array([(r * np.cos(a), r * np.sin(a)) for r, a in pts])
    # drop duplicates
    keep = np.ones(len(P), bool); keep[1:] = np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-6
    return P[keep]


# ---------------------------------------------------------------- exact axial stacks
def monotone_ring(poly, eps=2e-4):
    """Make a star-shaped CCW polygon strictly increasing in polar angle; returns (angles, ring)."""
    a = np.unwrap(np.arctan2(poly[:, 1], poly[:, 0]))
    if a[-1] < a[0]: poly, a = poly[::-1], a[::-1]
    for i in range(1, len(a)):
        if a[i] <= a[i - 1] + eps / 2:
            a[i] = a[i - 1] + eps
    r = np.linalg.norm(poly, axis=1)
    return a, np.column_stack([r * np.cos(a), r * np.sin(a)])

def circle_ring(angles, r):
    return np.column_stack([r * np.cos(angles), r * np.sin(angles)])

def d_ring(angles, r, flat):
    """round r with a flat at +v = flat (D shaft)"""
    s = np.sin(angles)
    rr = np.where(r * s > flat, flat / np.maximum(s, 1e-9), r)
    return np.column_stack([rr * np.cos(angles), rr * np.sin(angles)])

def axial_stack(path, bore, x0, z0):
    """path: list of (y, ring) along the outer surface, y non-decreasing; bore: ring (same N).
    Rings are (N,2) in (x, z) about (x0, z0).  Returns a closed mesh along +Y."""
    N = len(bore)
    V = []; T = []
    def add_ring(y, ring):
        V.append(np.column_stack([x0 + ring[:, 0], np.full(N, y), z0 + ring[:, 1]])); return (len(V) - 1) * N
    i = np.arange(N); j = (i + 1) % N
    def strip(a, b):          # quads a_i a_j b_j b_i
        T.append(np.column_stack([a + i, a + j, b + j])); T.append(np.column_stack([a + i, b + j, b + i]))
    ids = [add_ring(y, r) for y, r in path]
    for k in range(len(path) - 1):
        strip(ids[k + 1], ids[k])                      # outer wall / interface annulus
    b0 = add_ring(path[0][0], bore); b1 = add_ring(path[-1][0], bore)
    strip(b0, b1)                                      # bore
    strip(ids[0], b0)                                  # start cap
    strip(b1, ids[-1])                                 # end cap
    V = np.concatenate(V); T = np.concatenate(T)
    if volume(V, T) < 0: T = T[:, ::-1]
    return V, T
