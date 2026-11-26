"""Overview renders for the 08 printed lid, rev 2 -> docs/printed-lid.png"""
import sys, pickle, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk, scene3d as s3
import printed_lid as P

def coarse(fn, box, h):
    from skimage import measure
    g = mk.Grid(np.asarray(box[0]) - 0.137, box[1], h); s = fn(g)
    V, T, _, _ = measure.marching_cubes(s, 0.0, spacing=tuple(g.h)); V = V + g.lo
    if mk.volume(V, T) < 0: T = T[:, ::-1]
    return V, T
def stl(p):
    t = mk.read_stl(p); V = t.reshape(-1, 3); return mk.weld(V, np.arange(len(V)).reshape(-1, 3), 1e-4)

lid = stl(ROOT / 'cad/08-printed-lid/08a-lid-body.stl')
hood = coarse(P.hood, P.HOOD_BOX, 0.9); car = coarse(P.carrier, P.CAR_BOX, 0.6)
cl = pickle.load(open(HERE / 'clouds.pkl', 'rb')); smol, prep = P.POSE(cl['smol']), P.POSE(cl['prep'])
chk = json.load(open(ROOT / 'cad/08-printed-lid/checks.json'))
LID, HOOD, CAR, SM, PR, FIL = '#c9cdd3', '#e3a33b', '#3c8dbc', '#2a9d8f', '#d1495b', '#7b2cbf'
sh = lambda VT, d: (VT[0] + np.asarray(d, float), VT[1])

fig = plt.figure(figsize=(18, 13)); fig.patch.set_facecolor('white')
fig.suptitle('08 Printed lid, rev 2: uphill feeder in jojo\'s two-port lid (Printables 1441905)', fontsize=15, weight='bold', y=0.995)

# 1 assembled
ax = fig.add_axes([0.0, 0.52, 0.5, 0.42]); v = s3.View(az=-60, el=26)
s3.draw(ax, v, [(lid, LID), (hood, HOOD)], max_edge=40, lw=0.9); s3.frame(ax, v, (-117, -59, 60), (117, 59, 158), 0.03)
s3.callout(ax, v, (52, -42, 140), '08b hood, 45.9 mm\nabove the lid top', HOOD, (-95, 30))
s3.callout(ax, v, (-60, 0, 111.6), '08a = jojo lid: rim, gasket,\nlatches, ports unchanged;\nold outlet hole closed', '#555', (-20, -80))
s3.callout(ax, v, (-1.5, -5.5, 147.5), 'outlet: PC4-M10\n(Ø9, self-threading)', '#333', (-120, 10))
s3.callout(ax, v, (102, 14, 132), 'M12 / PG7 gland', '#333', (60, 40))
for k, (x, y) in P.SCREWS.items(): s3.callout(ax, v, (x, y, P.ROOF_OUT), f'roof screw {k}', CAR, (25 if k == 'A' else -25, 50))
ax.set_title('Assembled', fontsize=12, weight='bold')

# 2 side section y = -5.5 (filament plane)
ax = fig.add_axes([0.52, 0.52, 0.47, 0.42]); ax.set_aspect('equal')
th = np.linspace(0, 2 * np.pi, 400)
for R, ls in ((102.5, '-'), (45, ':')):
    ax.plot(-6.072 + R * np.cos(th), 3.354 + R * np.sin(th), ls, c='#999', lw=1)
def sect(VT, c, y0=-5.5, alpha=1.0):
    V, T = VT; tri = V[T]; s = tri[:, :, 1] - y0
    m = (s.min(1) < 0) & (s.max(1) > 0)
    segs = []
    for t, d in zip(tri[m], s[m]):
        pts = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            if (d[i] < 0) != (d[j] < 0):
                f = d[i] / (d[i] - d[j]); pts.append(t[i] + f * (t[j] - t[i]))
        if len(pts) == 2: segs.append([pts[0][[0, 2]], pts[1][[0, 2]]])
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(segs, colors=c, lw=1.2, alpha=alpha))
sect(lid, '#777'); sect(hood, HOOD); sect(car, CAR)
m = np.abs(smol[:, 1] + 5.5) < 12; ax.scatter(smol[m, 0], smol[m, 2], s=0.3, c=SM, alpha=0.5)
ax.scatter(prep[:, 0], prep[:, 2], s=0.5, c=PR)
# filament: spool tangent -> guide -> axis -> outlet
for row, ls in ((chk['inlet_routing'][0], '-'), (chk['inlet_routing'][-1], ':')):
    tp = row['leaves_spool_at']; M = chk['guide']['mouth_xyz']; ax.plot([tp[0], M[0]], [tp[1], M[2]], ls, c=FIL, lw=1.6)
ph = np.linspace(-np.radians(P.GUIDE['sweep']), 0, 30)
G = np.array([P.glob(-50 + 20 * np.sin(p), 0, -20 + 20 * np.cos(p)) for p in ph]); ax.plot(G[:, 0], G[:, 2], c=FIL, lw=1.6)
E = np.array([P.glob(u, 0, 0) for u in (-50, 62)]); ax.plot(E[:, 0], E[:, 2], c=FIL, lw=1.6)
ax.annotate('filament travels uphill (40°)', P.glob(10, 0, 0)[[0, 2]], (20, 175), color=FIL, weight='bold', fontsize=9.5,
            arrowprops=dict(arrowstyle='-|>', color=FIL))
ax.annotate('curved inlet guide R20\n+ PREP (low, +X end)', chk['guide']['mouth_xyz'][::2], (118, 40), color=PR, weight='bold', fontsize=9.5,
            arrowprops=dict(arrowstyle='-|>', color=PR))
ax.annotate('full spool: 8° turn at the guide\nnear-empty (R45, dotted): 46°', (60, 30), (-20, 20), fontsize=9, color=FIL)
ax.annotate('Smol', (45, 120), (-35, 135), color=SM, weight='bold', fontsize=10, arrowprops=dict(arrowstyle='-|>', color=SM))
ax.set_xlim(-40, 135); ax.set_ylim(-5, 182); ax.grid(alpha=0.25); ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)')
ax.set_title('Section at the filament plane (Y = −5.5)', fontsize=12, weight='bold')

# 3 exploded with carrier
ax = fig.add_axes([0.0, 0.0, 0.6, 0.5]); v = s3.View(az=-38, el=20)
DZ = 0
items = [(sh(lid, (0, 0, -45)), LID), (sh(hood, (0, 0, 70)), HOOD), (car, CAR)]
s3.draw(ax, v, items, max_edge=40, lw=0.9)
s3.frame(ax, v, (-117, -59, 15), (117, 59, 228), 0.03)
for k, (u, w) in P.BOLTS.items():
    s3.callout(ax, v, P.glob(u, w, P.BASE_V), f'insert {k}\n(Smol bolt)', CAR, (-60 if k == 'B' else 40, -60))
s3.callout(ax, v, (93.25, -36, 130), 'tower A', CAR, (70, 10)); s3.callout(ax, v, (9, -30, 147), 'tower B', CAR, (-60, 10))
s3.callout(ax, v, chk['guide']['mouth_xyz'], 'inlet guide', PR, (70, -30))
s3.callout(ax, v, P.glob(-43, 0, 13), 'PREP block\n(M2 pilots)', PR, (80, 25))
ax.set_title('Exploded: 08a ↓, 08c carrier (Smol not shown), 08b ↑', fontsize=12, weight='bold')

ax = fig.add_axes([0.62, 0.02, 0.37, 0.46]); ax.axis('off')
txt = [('Print', '08a top-face down (as jojo). 08b roof-down. 08c on its flat −Y face. ASA. Only the outlet boss may want a small support.'),
       ('Join', '08b bonds onto 08a\'s 2.5 mm ring (ASA acetone weld or epoxy); 4 tabs locate it.'),
       ('Feeder', 'Smol\'s two downward M3 bolts → V1 inserts in 08c. PREP → 08c block (2× M2). Whole module: 2× M3×10 through the roof.'),
       ('Filament', 'Load the spool so it pays out up its +X side. It enters the R20 guide, passes under PREP, climbs the Smol at 40° and leaves through the −X wall.'),
       ('Wiring', 'LOAD, PREP, N20 → one M12 / PG7 gland in the +X wall.'),
       ('Checks', f"Smol/PREP ↔ spool {chk['smol_prep_vs_spool']['min_mm']} mm; hood ↔ Smol {chk['hood_vs_smol']['min_mm']} mm; no part inside the lid; module drops through the opening.")]
y = 0.97
for k, t in txt:
    ax.text(0.0, y, k, fontsize=11, weight='bold', va='top', transform=ax.transAxes)
    ax.text(0.19, y, t, fontsize=10.5, va='top', wrap=True, transform=ax.transAxes)
    y -= 0.16
fig.savefig(ROOT / 'docs/printed-lid.png', dpi=110)
print('ok')
