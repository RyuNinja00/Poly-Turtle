"""Pose search (rev 3 uses ALPHA 45: minimise x + z of the inlet, i.e. the 45-degree roof line, subject to spool clearance, no lid intersection and a vertical drop through the opening)."""
import numpy as np, pickle
from pose import Pose
import occ as O
occ = np.load('occ.npz')['occ']
print('sanity', O.lookup(occ, np.array([[50,40,109],[50,0,90],[-50,0,109],[105,0,80]])))
C = pickle.load(open('clouds.pkl', 'rb'))
def boxpts(lo, hi, n=7):
    g = [np.linspace(l, h, n) for l, h in zip(lo, hi)]
    return np.stack(np.meshgrid(*g, indexing='ij'), -1).reshape(-1, 3)
# carrier + PREP arm envelope in archived-local (u, w, v)
LOC = np.concatenate([boxpts((-33.6, 17.4, -9.5), (43.0, 31, 4.9), 12), boxpts((-49.4, 6.9, -9.5), (-31.5, 31, 16), 8),
                      boxpts((-49.4, -6.6, 10.1), (-36.8, 6.9, 16), 6)])
from pose import TF0, A0, V0
W0 = np.cross(V0, A0)
CAR0 = TF0 + LOC[:, :1] * A0 + LOC[:, 1:2] * W0 + LOC[:, 2:] * V0
ALL0 = np.concatenate([C['smol'], C['prep'], CAR0])
SC = np.array([-6.072, 3.354])
def evaluate(al, x, y, z, rs=(102.5, 75, 45)):
    p = Pose(al, (x, y, z)); P = p(ALL0)
    m = np.abs(P[:, 1]) <= 39
    sp = (np.hypot(P[m, 0] - SC[0], P[m, 2] - SC[1]) - 102.5).min()
    below = P[P[:, 2] < 111.6]
    lid = O.lookup(occ, below).sum()
    xr = (P[:, 0].min(), P[:, 0].max()); yr = (P[:, 1].min(), P[:, 1].max())
    top = P[:, 2].max()
    # inlet turn: incoming from right-side tangent of spool radius r to inlet point
    pin = np.array([x, z]); a = np.array([p.A[0], p.A[2]]); turns = []
    for r in rs:
        d = pin - SC; L = np.linalg.norm(d); th = np.arcsin(r / L)
        base = np.arctan2(-d[1], -d[0])            # direction inlet -> centre
        ang = base + th                            # tangent on the +X side (rotate ccw toward +x?)
        # pick the tangent whose contact point has larger x
        cands = []
        for s in (1, -1):
            ang = base + s * th; tdir = np.array([np.cos(ang), np.sin(ang)])
            tp = pin + tdir * np.sqrt(L * L - r * r); cands.append((tp[0], -tdir))
        _, inc = max(cands, key=lambda c: c[0])
        turns.append(np.degrees(np.arccos(np.clip(inc @ a, -1, 1))))
    return dict(spool=sp, lid=int(lid), x=xr, y=yr, top=top, turns=turns)

if __name__ == '__main__':
    best = []
    for al in (15, 20, 25, 30, 35):
        for x in np.arange(70, 99, 2.0):
            for z in np.arange(80, 112, 1.0):
                y = 0.0
                r = evaluate(al, x, y, z)
                ymid = (r['y'][0] + r['y'][1]) / 2; y = -4.0 - ymid   # centre in opening (-39.5..31.5)
                r = evaluate(al, x, y, z)
                ok = r['spool'] >= 3 and r['lid'] == 0 and r['x'][0] >= 6 and r['x'][1] <= 98.5 and r['y'][0] >= -38.5 and r['y'][1] <= 30.5
                if ok: best.append((r['top'], al, x, y, z, r))
    best.sort(key=lambda t: t[0])
    for b in best[:12]: print(round(b[0], 1), b[1], b[2], round(b[3], 2), b[4], {k: (np.round(v, 1) if not isinstance(v, int) else v) for k, v in b[5].items()})
