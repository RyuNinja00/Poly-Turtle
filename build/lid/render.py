"""Overview renders for the 08 printed lid, rev 3 -> docs/printed-lid.png"""
import sys, pickle, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk, scene3d as s3
import printed_lid as P

P.H = 0.8                                     # preview resolution for drawing only
Vb, Tb = P.base(); Vj, Tj = P.endcap_tri()
g = P.Grid(*P.CANOPY_BOX, 0.8); f, hm = P.canopy(g, Vb, Tb, Vj, Tj); Vt, Tt = P.mc(f, g)
Tt = Tt[Vt[Tt][:, :, 2].max(1) > P.ZC + 0.05]          # hide the overlap band (it sits inside the base)
bush = P.E.outlet_bushing(P.TF, P.A, P.outlet_u() - 0.6, P.outlet_face(), n_theta=48, ds=0.1)
gc = P.Grid(*P.CAR_BOX, 0.8); Vc, Tc = P.mc(P.carrier(gc), gc)
cl = pickle.load(open(HERE / 'clouds.pkl', 'rb')); smol, prep = P.POSE(cl['smol']), P.POSE(cl['prep'])
chk = json.load(open(ROOT / 'cad/08-printed-lid/checks.json'))
vf = json.load(open(ROOT / 'cad/08-printed-lid/verify.json'))
LID, CAN, CAR, SM, PR, FIL = '#c9cdd3', '#e3a33b', '#3c8dbc', '#2a9d8f', '#d1495b', '#7b2cbf'
base, can, car = (Vb, Tb), (Vt, Tt), (Vc, Tc)

fig = plt.figure(figsize=(18, 13.5)); fig.patch.set_facecolor('white')
fig.suptitle('08 Printed lid, rev 3.1: one piece, no supports (jojo\'s lid base, Printables 1441905)', fontsize=15, weight='bold', y=0.995)

ax = fig.add_axes([0.0, 0.52, 0.5, 0.42]); v = s3.View(az=-62, el=24)
s3.draw(ax, v, [(base, LID), (can, CAN), (bush, CAN)], max_edge=30, lw=0.7); s3.frame(ax, v, (-117, -59, 60), (117, 59, 161), 0.03)
s3.callout(ax, v, (48, -20, 160.5), 'feeder canopy\n(45° faces)', CAN, (-40, 45))
s3.callout(ax, v, (-60, 0, 131.5), 'vault: 45° chamfers,\n36 mm flat', CAN, (-30, 55))
s3.callout(ax, v, (-60, -58, 70), 'jojo base kept exactly:\nrim, gasket, latches', '#555', (-30, -60))
s3.callout(ax, v, (P.MF_AT['x'], 0, 133.0), 'Micro-Fit 3.0 2×6\nbulkhead plate', '#333', (-20, 70))
for k, (x, z) in chk['wall_screws_xz'].items(): s3.callout(ax, v, (x, -46.5, z), f'M3 wall screw {k}', CAR, (45 if k == 'A' else 0, -55 if k == 'A' else -75))
ax.set_title('Assembled', fontsize=12, weight='bold')

ax = fig.add_axes([0.5, 0.52, 0.5, 0.42]); v = s3.View(az=125, el=22)
s3.draw(ax, v, [(base, LID), (can, CAN), (bush, CAN)], max_edge=30, lw=0.7); s3.frame(ax, v, (-117, -59, 60), (117, 59, 161), 0.03)
s3.callout(ax, v, chk['outlet']['inner_face_xyz'], 'outlet: printed M10×1 thread\n+ O-ring seat, square to face', '#333', (50, 50))
s3.callout(ax, v, (110, 0, 111.6), 'jojo end caps\n(latch bars, finger slot)', '#555', (60, -40))
ax.set_title('From the −X end', fontsize=12, weight='bold')

# section through the filament plane
ax = fig.add_axes([0.04, 0.05, 0.5, 0.42]); ax.set_aspect('equal')
th = np.linspace(0, 2 * np.pi, 400)
for R, ls in ((102.5, '-'), (45, ':')): ax.plot(-6.072 + R * np.cos(th), 3.354 + R * np.sin(th), ls, c='#999', lw=1)
def sect(VT, c, y0=-5.5):
    V, T = VT; tri = V[T]; s = tri[:, :, 1] - y0; m = (s.min(1) < 0) & (s.max(1) > 0); segs = []
    for t, d in zip(tri[m], s[m]):
        pts = [t[i] + d[i] / (d[i] - d[j]) * (t[j] - t[i]) for i, j in ((0, 1), (1, 2), (2, 0)) if (d[i] < 0) != (d[j] < 0)]
        if len(pts) == 2: segs.append([pts[0][[0, 2]], pts[1][[0, 2]]])
    ax.add_collection(LineCollection(segs, colors=c, lw=1.2))
sect(base, '#777'); sect(can, CAN); sect(bush, CAN); sect(car, CAR)
m = np.abs(smol[:, 1] + 5.5) < 12; ax.scatter(smol[m, 0], smol[m, 2], s=0.3, c=SM, alpha=0.5); ax.scatter(prep[:, 0], prep[:, 2], s=0.5, c=PR)
for row, ls in ((chk['inlet_routing'][0], '-'), (chk['inlet_routing'][-1], ':')):
    tp = row['leaves_spool_at']; M = chk['guide']['mouth_xyz']; ax.plot([tp[0], M[0]], [tp[1], M[2]], ls, c=FIL, lw=1.6)
ph = np.linspace(-np.radians(P.GUIDE['sweep']), 0, 30)
G = np.array([P.glob(-50 + 20 * np.sin(p), 0, -20 + 20 * np.cos(p)) for p in ph]); ax.plot(G[:, 0], G[:, 2], c=FIL, lw=1.6)
E = np.array([P.glob(u, 0, 0) for u in (-50, P.outlet_u() + 12)]); ax.plot(E[:, 0], E[:, 2], c=FIL, lw=1.6)
ax.annotate('filament climbs at 45°', P.glob(15, 0, 0)[[0, 2]], (55, 178), color=FIL, weight='bold', fontsize=9.5, arrowprops=dict(arrowstyle='-|>', color=FIL))
ax.annotate('inlet guide R20 + PREP\n(low, +X end)', chk['guide']['mouth_xyz'][::2], (112, 35), color=PR, weight='bold', fontsize=9.5, arrowprops=dict(arrowstyle='-|>', color=PR))
ax.annotate('every ceiling is 45° or a\nshort bridge (36 / 25 mm)', (60, 158), (-35, 172), fontsize=9.5, color=CAN, weight='bold', arrowprops=dict(arrowstyle='-|>', color=CAN))
ax.set_xlim(-40, 140); ax.set_ylim(-5, 188); ax.grid(alpha=0.25); ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)')
ax.set_title('Section at the filament plane (Y = −5.5)', fontsize=12, weight='bold')

ax = fig.add_axes([0.58, 0.25, 0.41, 0.25]); v = s3.View(az=-55, el=-32)
s3.draw(ax, v, [(base, LID), (can, CAN), (bush, CAN), (car, CAR)], max_edge=30, lw=0.7)
s3.frame(ax, v, (-117, -59, 60), (117, 59, 161), 0.03)
s3.callout(ax, v, chk['guide']['mouth_xyz'], 'feeder module\n(drops in from below)', CAR, (60, -25))
ax.set_title('From below: carrier in place (Smol not shown)', fontsize=11, weight='bold')

ax = fig.add_axes([0.6, 0.0, 0.39, 0.24]); ax.axis('off')
ob = chk['overhang_area_rim_down']; fl = chk['canopy_flat_ceilings']
txt = [('Print', 'One piece, rim down, ASA, brim, no supports. TPU: rim gasket, washer.'),
       ('Feeder', 'Bench-build the carrier + Smol + PREP; lift it in through the rim; 2× M3 through the −Y wall.'),
       ('Outlet', 'PC4-M10 into a printed M10×1 thread, O-ring/TPU washer seat; axis = filament axis.'),
       ('Checks', f"final mesh: spool ↔ lid {vf['lid_vs_spool205']['min_gap_mm']} mm, Smol ↔ lid {vf['lid_vs_smol']['min_gap_mm']} mm, drop-in {vf['drop_in']['min_gap_mm']} mm")]
y = 0.97
for k, t in txt:
    ax.text(0.0, y, k, fontsize=10.5, weight='bold', va='top', transform=ax.transAxes)
    ax.text(0.17, y, t, fontsize=10, va='top', wrap=True, transform=ax.transAxes); y -= 0.25
fig.savefig(ROOT / 'docs/printed-lid.png', dpi=110)
print('ok')
