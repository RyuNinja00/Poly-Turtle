from pathlib import Path
import pickle, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle, Polygon
from cradle_drive import *

L = Layout('fast'); A_X, A_Z = L.A_X, L.A_Z
parts = pickle.load(open(Path(__file__).parent / 'parts-fast.pkl', 'rb'))
COL = {'07a-Roller-with-gear': '#E07A2E', '07b-Tread-sleeve-TPU-L': '#2B2D31', '07b-Tread-sleeve-TPU-R': '#2B2D31',
       '07d-Motor-bracket-cradle-key': '#2F6FA8', '07c-Pinion-17T-N20': '#3F8F6B'}

def draw_all(ax, items, view, light=np.array([0.3, -0.5, 0.8])):
    P = {'iso': None}
    if view == 'side':   M = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])     # look from -Y... x right, z up, depth +y toward viewer
    elif view == 'top':  M = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    elif view == 'end':  M = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])      # look from +X (front), y right
    else:
        a, e = np.deg2rad(-35), np.deg2rad(28)
        Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
        M = (Rx @ np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]) @ Rz)
    tris, cols_in = [], []
    for V, T, color in items:
        tris.append((V @ M.T)[T]); cols_in.append(np.repeat(np.array(matplotlib.colors.to_rgb(color))[None], len(T), 0))
    tri = np.concatenate(tris); base = np.concatenate(cols_in)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nn = np.linalg.norm(n, axis=1); ok = nn > 1e-12
    n = n[ok] / nn[ok, None]; tri = tri[ok]
    vis = n[:, 2] > 0
    base = base[ok][vis]; tri, n = tri[vis], n[vis]
    order = np.argsort(tri[:, :, 2].mean(1))
    L = light / np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.clip(n @ L, 0, 1)
    cols = np.clip(shade[:, None] * base + 0.12, 0, 1)
    pc = PolyCollection(tri[order, :, :2], facecolors=cols[order], edgecolors=cols[order], linewidths=0.05, zorder=3)
    ax.add_collection(pc)
    return M

def n20_box(view):
    # envelope rectangles in projection
    if view == 'side': return [Rectangle((A_X - 5.69, A_Z - 6.53), 11.38, 13.06)]
    if view == 'top': return [Rectangle((A_X - 5.69, Y['motor'][0]), 11.38, 25.2)]
    return []

fig = plt.figure(figsize=(16, 11))
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 1])
# ---------------- side view (looking from -Y, i.e. the key side)
ax = fig.add_subplot(gs[0, 0])
ax.set_title('Side view (projection along Y)  ·  X forward from rear factory axle, Z up from floor\nspool circles apply only between the flanges (|Y| ≤ 39); the bracket bar over the cradle is outboard at Y −44…−41', fontsize=9)
ax.add_patch(Circle(SPOOL_C, FLANGE_R, fill=False, ec='#8C6B3F', lw=1.4, zorder=1))
ax.add_patch(Circle(SPOOL_C, ENVELOPE_R, fill=False, ec='#8C6B3F', lw=0.8, ls='--', zorder=1))
ax.add_patch(Circle(REAR, 4, fc='#5B6770', zorder=2)); ax.add_patch(Circle(REAR, 7, fill=False, ec='#5B6770', zorder=2))
# approximate molded features
ax.add_patch(Polygon([(-8, 0), (15, 0), (22, 10.5), (85, 10.5), (93, 0), (150, 0), (150, -3), (-8, -3)], fc='#DDE3E6', ec='#9AA7AD', zorder=0))
ax.add_patch(Rectangle((98, 0), 17, 28, fc='#E8EEF0', ec='#9AA7AD', ls=':', zorder=0))
ax.add_patch(Rectangle((124, 4.8), 11, 11.4, fc='#CFE9E6', ec='#7FB5AE', ls=':', zorder=0))
ax.add_patch(Rectangle((135, 0), 15, 55, fc='#EEF1F2', ec='#9AA7AD', ls=':', zorder=0))
draw_all(ax, [(V, T, COL[n]) for n, (V, T) in parts.items()], 'side')
for r in n20_box('side'): r.set(fc='#B9B9B9', ec='#555', zorder=2.5); ax.add_patch(r)
ax.text(A_X, A_Z, 'N20', ha='center', va='center', fontsize=8, zorder=6)
ax.text(106, 0.8, 'front cradle\n(photo est.)', fontsize=7, ha='center', color='#6F7C82')
ax.text(129.5, 6, 'plug rim\ncrest band', fontsize=7, ha='center', color='#4F8C84')
ax.text(142.5, 45, 'end loop\n(est.)', fontsize=7, ha='center', color='#6F7C82')
ax.text(53, 3.5, 'centre platform', fontsize=7, ha='center', color='#6F7C82')
ax.text(SPOOL_C[0], SPOOL_C[1] - 70, 'Ø205 spool on the archived pose\n(raised lid, Smol + LOAD, PREP unchanged)', ha='center', fontsize=8, color='#8C6B3F')
ax.set_xlim(-15, 155); ax.set_ylim(-5, 60); ax.set_aspect('equal'); ax.grid(alpha=0.25)
# ---------------- iso
ax = fig.add_subplot(gs[0, 1]); ax.set_title('Drive in place (iso): 5 printed parts + V1.0 N20, no fasteners on the roller', fontsize=10)
draw_all(ax, [(V, T, COL[n]) for n, (V, T) in parts.items()], 'iso')
ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')
# ---------------- top view
ax = fig.add_subplot(gs[1, 0]); ax.set_title('Top view (spool removed)', fontsize=10)
ax.add_patch(Rectangle((98, -45.5), 17, 6, fc='#E8EEF0', ec='#9AA7AD', ls=':', zorder=0))
ax.add_patch(Rectangle((98, 39.5), 17, 6, fc='#E8EEF0', ec='#9AA7AD', ls=':', zorder=0))
ax.add_patch(Rectangle((135, -20), 15, 40, fc='#EEF1F2', ec='#9AA7AD', ls=':', zorder=0))
ax.add_patch(Rectangle((-4, -47.5), 8, 95, fc='#5B6770', zorder=1))
ax.add_patch(Rectangle((PITCH - 4, -46), 8, 92, fc='#8A949A', zorder=1))
ax.add_patch(Rectangle((PITCH - 7, 40), 14, 4, fc='#C0C6C9', ec='#555', zorder=2)); ax.text(PITCH, 46.5, 'MR148', fontsize=7, ha='center')
draw_all(ax, [(V, T, COL[n]) for n, (V, T) in parts.items()], 'top')
for r in n20_box('top'): r.set(fc='#B9B9B9', ec='#555', zorder=4); ax.add_patch(r)
for yy in (-39, 39): ax.axhline(yy, color='#8C6B3F', ls='--', lw=0.8)
ax.text(10, 40.5, '78 mm spool flanges', fontsize=7, color='#8C6B3F')
ax.annotate('key tab sits in the left bearing slot\n(replaces that bearing; locks bracket rotation)', (PITCH, -42), (40, -40), fontsize=7, arrowprops=dict(arrowstyle='->', lw=0.7))
ax.set_xlim(-15, 155); ax.set_ylim(-52, 52); ax.set_aspect('equal'); ax.grid(alpha=0.25)
# ---------------- end view
ax = fig.add_subplot(gs[1, 1]); ax.set_title('End view (from the front end wall, looking rearward)', fontsize=10)
draw_all(ax, [(V, T, COL[n]) for n, (V, T) in parts.items()], 'end')
ax.add_patch(Rectangle((Y['motor'][0], A_Z - 6.53), 25.2, 13.06, fc='#B9B9B9', ec='#555', zorder=1))
ax.add_patch(Rectangle((-45.5, 0), 6, 28, fc='#E8EEF0', ec='#9AA7AD', ls=':', zorder=0)); ax.add_patch(Rectangle((39.5, 0), 6, 28, fc='#E8EEF0', ec='#9AA7AD', ls=':', zorder=0))
ax.set_xlim(-50, 50); ax.set_ylim(-2, 42); ax.set_aspect('equal'); ax.grid(alpha=0.25)
handles = [Rectangle((0, 0), 1, 1, fc=c) for c in ['#E07A2E', '#2B2D31', '#3F8F6B', '#2F6FA8', '#B9B9B9']]
fig.legend(handles, ['Roller with 15T gear (ASA, one piece)', 'Treads Ø%.2f (TPU 95A)' % (2 * TREAD_R), 'Pinion 17T on the N20 (ASA)',
                     'Motor bracket + cradle key (ASA)', 'V1.0 N20 (zip-tied)'], loc='lower center', ncol=5, fontsize=9)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(cd_out := (ROOT / 'docs' / 'cradle-drive-overview.png'), dpi=130)
print('ok')
