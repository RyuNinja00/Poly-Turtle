"""2D kinematic check of the 15T/17T m1 pair: interference depth and backlash over a tooth cycle."""
import sys, numpy as np
sys.path.insert(0, 'tools'); from meshkit import involute_gear
from matplotlib.path import Path as MP

def rot(P, a): c, s = np.cos(a), np.sin(a); return P @ np.array([[c, s], [-s, c]])
def dense(P, step=0.02):
    out = []
    for a, b in zip(P, np.roll(P, -1, 0)):
        n = max(1, int(np.linalg.norm(b - a) / step)); out.append(a + np.outer(np.arange(n) / n, b - a))
    return np.concatenate(out)
def seg_dist(Q, P):
    a = P; b = np.roll(P, -1, 0); best = np.full(len(Q), np.inf)
    for s in range(0, len(a), 256):
        A = a[s:s+256][None]; B = b[s:s+256][None]; q = Q[:, None]; ab = B - A
        t = np.clip(((q - A) * ab).sum(-1) / (ab * ab).sum(-1), 0, 1); best = np.minimum(best, np.linalg.norm(q - A - t[..., None] * ab, axis=-1).min(1))
    return best

def cycle(G, P, z1, z2, cd, phase, n, m=1.0):
    worst, gaps = 0.0, []
    for th in np.linspace(0, 2 * np.pi / z1, n):
        g = rot(G, th); p = rot(P, -th * z1 / z2 + phase) + [cd, 0]
        gd, pd = dense(g, 0.03), dense(p, 0.03)
        pin = MP(g).contains_points(pd); gin = MP(p).contains_points(gd)
        worst = max(worst, seg_dist(pd[pin], g).max() if pin.any() else 0, seg_dist(gd[gin], p).max() if gin.any() else 0)
        near = pd[(np.abs(pd[:, 1]) < 4 * m) & (pd[:, 0] < m * (z1 / 2 + 1.5))]
        gaps.append(seg_dist(near, g).min() if len(near) else np.inf)
    return worst, gaps

def run(z1, z2, backlash=0.12, m=1.0, cd=None):
    G = involute_gear(m, z1, backlash=backlash); P = involute_gear(m, z2, backlash=backlash); cd = cd or m * (z1 + z2) / 2
    ph = np.linspace(0, 2 * np.pi / z2, 35)
    best = ph[int(np.argmin([cycle(G, P, z1, z2, cd, f, 11, m)[0] for f in ph]))]
    worst, gaps = cycle(G, P, z1, z2, cd, best, 61, m)
    tip = cd - m * (z2 / 2 + 1) - m * (z1 / 2 - 1.25)
    return worst, min(gaps), tip

if __name__ == '__main__':
    w, gmin, tip = run(15, 17)
    print(f'15T/17T m1 (fast): worst penetration over a tooth cycle {w:.3f} mm, min flank distance {gmin:.3f} mm (driving-flank contact), tip-to-root clearance {tip:.2f} mm')
    w, gmin, tip = run(30, 15, m=0.75, cd=17.101)
    print(f'30T/15T m0.75 at 17.101 (v1pinion): interference {w:.3f} mm, min flank distance {gmin:.3f} mm, tip-to-root {tip:.2f} mm')
