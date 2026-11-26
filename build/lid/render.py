"""Overview renders for the 08 printed lid -> docs/printed-lid.png"""
import sys, pickle, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk, scene3d as s3
import printed_lid as P

def coarse(fn, lo, hi, h=0.9):
    g = mk.Grid(np.asarray(lo) - 0.137, hi, h); return mk.surface_nets(fn(g), g)
def stl(p):
    t = mk.read_stl(p); V = t.reshape(-1, 3); return mk.weld(V, np.arange(len(V)).reshape(-1, 3), 1e-4)

lid = stl(ROOT / 'cad/08-printed-lid/08a-lid-body.stl')
hood = coarse(P.hood, (0, -44, P.PLATE_TOP - 4.5), (104, 36, P.ROOF_OUT + 1))
car = coarse(P.carrier, (13, 15, 70), (102, 33, P.ROOF_IN + 1), 0.7)
cl = pickle.load(open(HERE / 'clouds.pkl', 'rb'))
smol, prep = cl['smol'], cl['prep']
LID, HOOD, CAR, SM, PR = '#c9cdd3', '#e3a33b', '#3c8dbc', '#2a9d8f', '#d1495b'
sh = lambda VT, d: (VT[0] + np.asarray(d, float), VT[1])

fig = plt.figure(figsize=(18, 12.5)); fig.patch.set_facecolor('white')
fig.suptitle('08 Printed lid, rev 1 — jojo two-port lid (Printables 1441905) + feeder hood + feeder carrier', fontsize=15, weight='bold', y=0.995)

ax = fig.add_axes([0.0, 0.50, 0.5, 0.43]); v = s3.View(az=-60, el=28)
s3.draw(ax, v, [(lid, LID), (hood, HOOD)], max_edge=40, lw=0.9); s3.frame(ax, v, (-117, -59, 60), (117, 59, 147), 0.03)
s3.callout(ax, v, (52, -42, 135), '08b hood\n(roof-down print)', HOOD, (-90, 25))
s3.callout(ax, v, (-60, 0, 111.6), '08a lid body = jojo lid\nrim, gasket channel, latches\nand ports untouched', '#555', (-40, -70))
s3.callout(ax, v, (2, 20, 133), 'M12 / PG7 gland\n(all lane wiring)', '#333', (-70, 40))
for k, (x, y) in P.SCREW_XY.items(): s3.callout(ax, v, (x, y, P.ROOF_OUT), f'roof screw {k}\nM3×10', CAR, (30 if k == 'B' else -10, 45))
ax.set_title('Assembled, lid closed', fontsize=12, weight='bold')

ax = fig.add_axes([0.5, 0.50, 0.5, 0.43]); v = s3.View(az=-70, el=-38)
s3.draw(ax, v, [(lid, LID), (hood, HOOD), (car, CAR)], max_edge=40, lw=0.9)
for pts, c in ((smol, SM), (prep, PR)):
    q = v.p(pts); ax.scatter(q[:, 0], q[:, 1], s=0.15, c=c, alpha=0.5, zorder=6)
s3.frame(ax, v, (-117, -59, 60), (117, 59, 147), 0.03)
s3.callout(ax, v, (58, 24, 98), '08c carrier\n(replaces trayframe)', CAR, (70, -40))
s3.callout(ax, v, (60, -10, 100), 'Smol + LOAD (points)', SM, (60, -75))
s3.callout(ax, v, (15, 0, 125), 'PREP switch on\nhood block', PR, (-60, -60))
s3.callout(ax, v, (110, 0, 75), 'outlet: 4.3 mm PTFE hole\n(jojo end wall, unchanged)', '#555', (10, 60))
ax.set_title('From below (lid upside down): opening, carrier and feeder', fontsize=12, weight='bold')

ax = fig.add_axes([0.0, 0.0, 0.62, 0.50]); v = s3.View(az=-35, el=22)
DZ = 22
items = [(sh(lid, (0, 0, -30)), LID), (sh(hood, (0, 0, 75)), HOOD), (sh(car, (0, 0, DZ)), CAR)]
s3.draw(ax, v, items, max_edge=40, lw=0.9)
s3.frame(ax, v, (-117, -59, 30), (117, 59, 222), 0.03)
for k, (u, w) in P.BOLTS.items():
    p = P.TF + u * P.A + w * P.W + P.BASE_V * P.V_ + [0, 0, DZ]
    s3.callout(ax, v, p, f'insert {k}\nSmol bolt', CAR, (-60 if k == 'A' else 50, -55))
s3.callout(ax, v, (19, 17.4, 118 + DZ), 'tower A', CAR, (-60, -10)); s3.callout(ax, v, (97, 17.4, 140 + DZ), 'tower B', CAR, (50, 10))
s3.callout(ax, v, (52, -42, P.PLATE_TOP + 75), 'bond face: 2.5 mm wall\nonto 08a ring', HOOD, (90, 40))
ax.set_title('Exploded: 08a, 08c (+ Smol, not shown), 08b', fontsize=12, weight='bold')

ax = fig.add_axes([0.63, 0.02, 0.36, 0.46]); ax.axis('off')
txt = [('Print', '08a top-face down (as jojo); 08b roof-down; 08c on its flat +Y face. ASA, no supports.'),
       ('Join', '08b on 08a\'s 2.5 mm ring: ASA acetone weld or epoxy; 4 tabs locate it.'),
       ('Feeder', 'Smol\'s two downward M3 bolts → V1 heat-set inserts in 08c. 08c → roof by 2× M3×10 (+ washer, sealant).'),
       ('PREP', 'D2F-type switch → hood block, 2× M2 self-tapping from below (pilots Ø1.7).'),
       ('Wiring', 'LOAD, PREP, N20 out one M12 / PG7 gland (Ø12.4 hole, -X end wall).'),
       ('Service', '2 roof screws drop the carrier + Smol through the opening.'),
       ('Open item', 'Spool → PREP entry needs a ~110° turn in < 10 mm in the archived feeder pose. Not solved by this lid. See docs/printed-lid.md.')]
y = 0.97
for k, t in txt:
    ax.text(0.0, y, k, fontsize=11, weight='bold', color='#b23a48' if k == 'Open item' else '#222', va='top', transform=ax.transAxes)
    ax.text(0.2, y, t, fontsize=10.5, va='top', wrap=True, transform=ax.transAxes)
    y -= 0.135
fig.savefig(ROOT / 'docs/printed-lid.png', dpi=110)
print('ok')
