"""Tiny orthographic 3D illustration kit (numpy + matplotlib): primitives, a caliper model,
painter's-algorithm shading and 3D-to-2D projection for annotations.  Units: mm."""
import numpy as np, matplotlib
from matplotlib.collections import PolyCollection
from meshkit import Grid, box as sbox, cyl_y as scyl_y, subtract, union, surface_nets

# ------------------------------------------------------------------ primitives
def cuboid(lo, hi):
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    V = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    T = np.array([t for a, b, c, d in F for t in ((a, b, c), (a, c, d))])
    return V, T

def cylinder(p0, p1, r, n=48, r_in=0.0):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); ax = p1 - p0; L = np.linalg.norm(ax); ax /= L
    u = np.cross(ax, [0, 0, 1.0] if abs(ax[2]) < 0.9 else [1.0, 0, 0]); u /= np.linalg.norm(u); w = np.cross(ax, u)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False); ring = np.outer(np.cos(t), u) + np.outer(np.sin(t), w)
    i = np.arange(n); j = (i + 1) % n; T = []
    if r_in <= 0:
        V = np.concatenate([p0 + r * ring, p1 + r * ring, [p0, p1]]); c0, c1 = 2 * n, 2 * n + 1
        T += list(np.column_stack([i, j, n + j])) + list(np.column_stack([i, n + j, n + i]))
        T += list(np.column_stack([np.full(n, c0), j, i])) + list(np.column_stack([np.full(n, c1), n + i, n + j]))
    else:
        V = np.concatenate([p0 + r * ring, p1 + r * ring, p1 + r_in * ring, p0 + r_in * ring])
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            A, B = a * n, b * n
            T += list(np.column_stack([A + i, A + j, B + j])) + list(np.column_stack([A + i, B + j, B + i]))
    return V, np.array(T)

def plate_with_slot(xc, y0, y1, slot_w=14.0, top=28.0, axle_z=22.0, x_back=9.0, x_front=8.0, h=0.35):
    """Cradle plate (normal along Y) with a U slot open at the top, as photographed (sizes are estimates)."""
    g = Grid((xc - x_back - 1, y0 - 1, -1), (xc + x_front + 1, y1 + 1, top + 1), h)
    s = sbox(g, (xc - x_back, y0, 0), (xc + x_front, y1, top))
    slot = union(scyl_y(g, xc, axle_z, slot_w / 2, y0 - 1, y1 + 1), sbox(g, (xc - slot_w / 2, y0 - 1, axle_z), (xc + slot_w / 2, y1 + 1, top + 2)))
    return surface_nets(subtract(s, slot), g)

def xform(VT, R=np.eye(3), t=(0, 0, 0)):
    V, T = VT; return V @ np.asarray(R).T + np.asarray(t, float), T

def rot(axis, deg):
    a = np.deg2rad(deg); c, s = np.cos(a), np.sin(a)
    return {'x': np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), 'y': np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
            'z': np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]

# ------------------------------------------------------------------ caliper
def caliper(opening, depth_rod=None):
    """Digital caliper in its local frame: beam along +X, fixed jaw measuring faces at X = 0.
    Outside jaws hang to -Z (faces at X = 0 and X = opening, facing each other);
    inside jaws rise to +Z (outer faces at X = 0 and X = opening, facing away);
    depth rod leaves the beam end (X = 170) along +X by `depth_rod` (hidden when None).
    Returns list of (name, (V, T), colour)."""
    o = float(opening); d = 0.0 if depth_rod is None else float(depth_rod)
    steel, dark, disp = '#B8C0C6', '#3C4650', '#1E2A30'
    parts = [('beam', cuboid((-12, -1.6, 0), (170, 1.6, 16)), steel),
             ('fixed outside jaw', cuboid((-7, -1.6, -42), (0, 1.6, 0)), steel),
             ('fixed inside jaw', cuboid((0, -1.6, 16), (3.5, 1.6, 31)), steel),
             ('slider', cuboid((o - 3, -4.5, -3), (o + 42, 4.5, 19)), dark),
             ('display', cuboid((o + 8, 4.5, 2), (o + 34, 5.2, 14)), disp),
             ('slider outside jaw', cuboid((o, -1.6, -42), (o + 7, 1.6, -3)), steel),
             ('slider inside jaw', cuboid((o - 3.5, -1.6, 19), (o, 1.6, 31)), steel)]
    if d > 0: parts.append(('depth rod', cuboid((170, -0.8, 6), (170 + d, 0.8, 8.5)), steel))
    return parts

def ruler(length=150, width=13, thick=0.8):
    return [('ruler', cuboid((0, 0, 0), (length, width, thick)), '#C9CFD3')]

# ------------------------------------------------------------------ rendering
class View:
    def __init__(self, az=-55, el=24, light=(0.35, -0.5, 0.8)):
        a, e = np.deg2rad(az), np.deg2rad(el)
        self.v = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        self.r = np.cross([0, 0, 1.0], self.v); self.r /= np.linalg.norm(self.r); self.u = np.cross(self.v, self.r)
        self.light = np.asarray(light, float) / np.linalg.norm(light)
    def p(self, P):
        P = np.atleast_2d(np.asarray(P, float)); return np.column_stack([P @ self.r, P @ self.u])
    def p1(self, P):
        return tuple(self.p(P)[0])

def subdivide(tri, base, max_edge):
    for _ in range(8):
        e = np.max(np.linalg.norm(tri - np.roll(tri, 1, axis=1), axis=2), axis=1)
        big = e > max_edge
        if not big.any(): break
        t = tri[big]; a, b, c = t[:, 0], t[:, 1], t[:, 2]; ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        new = np.concatenate([np.stack(q, 1) for q in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))])
        tri = np.concatenate([tri[~big], new]); base = np.concatenate([base[~big], np.tile(base[big], (4, 1))])
    return tri, base

def draw(ax, view, items, edge=False, alpha=1.0, max_edge=7.0):
    tris, cols = [], []
    for item in items:
        (V, T), c = item[-2], item[-1]
        tris.append(V[T]); cols.append(np.repeat(np.array(matplotlib.colors.to_rgb(c))[None], len(T), 0))
    tri = np.concatenate(tris); base = np.concatenate(cols)
    tri, base = subdivide(tri, base, max_edge)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nn = np.linalg.norm(n, axis=1); ok = nn > 1e-12
    tri, base, n = tri[ok], base[ok], n[ok] / nn[ok, None]
    vis = n @ view.v > 0; tri, base, n = tri[vis], base[vis], n[vis]
    depth = (tri.mean(1) @ view.v); order = np.argsort(depth)
    shade = 0.5 + 0.5 * np.clip(n @ view.light, 0, 1)
    col = np.clip(shade[:, None] * base + 0.08, 0, 1)
    P2 = np.stack([tri @ view.r, tri @ view.u], -1)
    pc = PolyCollection(P2[order], facecolors=col[order], edgecolors=col[order] if not edge else '#33333355',
                        linewidths=0.15, alpha=alpha, zorder=3)
    ax.add_collection(pc); ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')

def frame(ax, view, lo, hi, pad=0.06):
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    C = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    P = view.p(C); a, b = P.min(0), P.max(0); d = (b - a) * pad
    ax.set_xlim(a[0] - d[0], b[0] + d[0]); ax.set_ylim(a[1] - d[1], b[1] + d[1]); ax.set_aspect('equal')

def dim3d(ax, view, p, q, text, color, off=(0, 0), fs=9, lw=2.0):
    from matplotlib.patches import FancyArrowPatch
    P, Q = view.p1(p), view.p1(q)
    ax.add_patch(FancyArrowPatch(P, Q, arrowstyle='<|-|>', mutation_scale=11, color=color, lw=lw, zorder=10))
    m = ((P[0] + Q[0]) / 2 + off[0], (P[1] + Q[1]) / 2 + off[1])
    ax.text(*m, text, color='white', fontsize=fs, weight='bold', ha='center', va='center', zorder=11,
            bbox=dict(boxstyle='round,pad=0.22', fc=color, ec='none'))

def callout(ax, view, p, text, color, off, fs=8.5):
    P = view.p1(p)
    ax.annotate(text, P, (P[0] + off[0], P[1] + off[1]), fontsize=fs, color=color, weight='bold', zorder=11, ha='center',
                arrowprops=dict(arrowstyle='-|>', color=color, lw=1.2), bbox=dict(boxstyle='round,pad=0.2', fc='white', ec=color, lw=0.8))
