"""Checks for the 08 printed lid, rev 3 (one piece): clearances, drop-in, routing, printability.

Writes cad/08-printed-lid/checks.json and packs cad/08-Printed-lid.zip."""
import sys, json, pickle, zipfile, numpy as np
from pathlib import Path
from scipy.ndimage import map_coordinates, label
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import printed_lid as P
import occ as O
from pose import TF0, A0, V0
W0 = np.cross(V0, A0)
OUT = ROOT / 'cad/08-printed-lid'

D = np.load(HERE / 'sdf.npz'); OCC = np.load(HERE / 'occ.npz')['occ']
def sample(k, pts):
    s, lo, h = D['s' + k], D[k + 'lo'], D[k + 'h']
    return map_coordinates(s, ((pts - lo) / h).T, order=1, mode='nearest')
def lid_clear(pts):
    """approx. distance outside the lid (negative = inside); base below Z 102 by occupancy."""
    d = sample('l', pts)
    base_in = (pts[:, 2] < P.ZC) & O.lookup(OCC, pts)
    return np.where(base_in, -1.0, np.where(pts[:, 2] < P.ZC - 1.4, 9.0, d))

cl = pickle.load(open(HERE / 'clouds.pkl', 'rb'))
smol, prep = P.POSE(cl['smol']), P.POSE(cl['prep'])
d0 = cl['smol'] - TF0; Ls = np.stack([d0 @ A0, d0 @ W0, d0 @ V0], -1)
iface = (Ls[:, 1] > 16.0) & (Ls[:, 2] < P.BASE_V + 0.05) & (Ls[:, 0] > -34) & (Ls[:, 0] < 48)
def verts(name):
    t = mk.read_stl(OUT / name).reshape(-1, 3); return np.unique(t.round(3), axis=0)
Vc = verts('08c-feeder-carrier.stl')
module = np.concatenate([smol, prep, Vc[::3]])

res = dict(pose=dict(alpha_deg=P.ALPHA, inlet_xyz=list(P.INLET)))
def worst(tag, d, pts):
    i = int(np.argmin(d)); res[tag] = dict(min_mm=round(float(d[i]), 2), at=pts[i].round(1).tolist())
worst('lid_vs_smol', lid_clear(smol), smol)
worst('lid_vs_prep', lid_clear(prep), prep)
worst('lid_vs_carrier', lid_clear(Vc[::3]), Vc[::3])
ds = sample('c', smol[~iface]); worst('carrier_vs_smol (excl. replaced trayframe interface)', ds, smol[~iface])
worst('carrier_vs_prep (switch sits on the block)', sample('c', prep), prep)

# drop-in: lower the whole module in 2 mm steps down past the rim; nothing may enter the lid
hits = 0; worst_d = 99.0
for dz in np.arange(0, 110, 2.0):
    q = module - [0, 0, dz]; q = q[q[:, 2] > 58]
    if len(q) == 0: break
    d = lid_clear(q); hits += int((d < 0).sum()); worst_d = min(worst_d, float(d.min()))
res['drop_in'] = dict(points_inside_lid=hits, min_clearance_mm=round(worst_d, 2), note='module translated straight down to below the rim')

# spool envelope (205 x 78) against the lid ceiling
SC = np.array([-6.072, 3.354])
th = np.linspace(0, np.pi, 1400); ys = np.linspace(-39, 39, 53)
S = np.array([[SC[0] + 102.5 * np.cos(t), y, SC[1] + 102.5 * np.sin(t)] for t in th for y in ys])
S = S[S[:, 2] > 60]
worst('lid_vs_spool', lid_clear(S), S)
m = np.abs(module[:, 1]) <= 39
r = np.hypot(module[m, 0] - SC[0], module[m, 2] - SC[1]) - 102.5; i = int(np.argmin(r))
res['module_vs_spool'] = dict(min_mm=round(float(r[i]), 2), at=module[m][i].round(1).tolist())

# inlet routing from the +X side of the spool into the guide mouth
mo, t = P.mouth(); M = P.glob(mo[0], 0, mo[1]); Tm = t[0] * P.A + t[1] * P.V_
rows = []
for R in (102.5, 80.0, 60.0, 45.0):
    pin = np.array([M[0], M[2]]); dv = pin - SC; L = np.linalg.norm(dv); a = np.arcsin(R / L); base = np.arctan2(-dv[1], -dv[0]); best = None
    for s in (1, -1):
        ang = base + s * a; td = np.array([np.cos(ang), np.sin(ang)]); tp = pin + td * np.sqrt(L * L - R * R)
        if best is None or tp[0] > best[0][0]: best = (tp, -td)
    tp, inc = best
    turn = float(np.degrees(np.arccos(np.clip(inc @ np.array([Tm[0], Tm[2]]), -1, 1))))
    seg = np.linspace(np.array([tp[0], M[1], tp[1]]), M - Tm, 60)
    rows.append(dict(spool_radius=R, leaves_spool_at=[round(float(tp[0]), 1), round(float(tp[1]), 1)], turn_at_mouth_deg=round(turn, 1),
                     path_vs_carrier_mm=round(float(sample('c', seg[:-3]).min()), 2), path_vs_lid_mm=round(float(lid_clear(seg).min()), 2)))
res['inlet_routing'] = rows
res['guide'] = dict(radius=P.GUIDE['R'], sweep_deg=P.GUIDE['sweep'], bore=2 * P.GUIDE['r_bore'], mouth_xyz=M.round(2).tolist())

# outlet: axis normal to the -X canopy face (A = face normal at ALPHA 45)
nface = np.array([-1, 0, 1]) / np.sqrt(2)
res['outlet'] = dict(axis_vs_face_normal_deg=round(float(np.degrees(np.arccos(abs(P.A @ nface)))), 2),
                     inner_face_xyz=P.glob(P.outlet_u(), 0, 0).round(2).tolist(), hole=P.OUTLET['hole'],
                     thread_length_mm=round(P.T_V / np.sqrt(2) + P.OUTLET['out'] + 1.0, 1))
res['wall_screws_xz'] = {k: [round(c, 2) for c in P.pad_screw(u)] for k, u in P.PADS.items()}
res['bolt_insert_axes'] = {k: P.glob(u, w, P.BASE_V).round(2).tolist() for k, (u, w) in P.BOLTS.items()}

# printability, rim down: downward-facing area by overhang angle (from vertical)
tri = mk.read_stl(OUT / '08-Printed-lid.stl')
n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ar = np.linalg.norm(n, axis=1) / 2
nz = n[:, 2] / np.maximum(2 * ar, 1e-12); C = tri.mean(1)
up = C[:, 2] > 60.4
bands = {}
for lo_, hi_, name in ((-1.01, -0.985, 'horizontal (bridges)'), (-0.985, -0.766, '50-80 deg'), (-0.766, -0.707, '45-50 deg')):
    mm = up & (nz >= lo_) & (nz < hi_)
    bands[name] = dict(base_mm2=round(float(ar[mm & (C[:, 2] < P.ZC)].sum())), canopy_mm2=round(float(ar[mm & (C[:, 2] >= P.ZC)].sum())))
res['overhang_area_rim_down'] = bands
# horizontal ceilings in the canopy: span of each connected patch (shorter side = bridge length)
hz = up & (nz < -0.985) & (C[:, 2] >= P.ZC)
spans = []
if hz.any():
    q = C[hz]; zr = np.round(q[:, 2] / 0.5)
    for z in np.unique(zr):
        pts = q[zr == z]
        grid = np.zeros((600, 300), bool); ij = np.clip(((pts[:, :2] + [120, 60]) / 0.4).astype(int), 0, [599, 299])
        grid[ij[:, 0], ij[:, 1]] = True
        from scipy.ndimage import binary_closing
        lab, nl = label(binary_closing(grid, iterations=2))
        for k in range(1, nl + 1):
            w = np.argwhere(lab == k) * 0.4
            if len(w) < 20: continue
            ext = w.max(0) - w.min(0)
            spans.append(dict(z=round(float(z * 0.5), 1), size_xy=[round(float(e), 1) for e in ext], bridge_mm=round(float(min(ext)), 1)))
res['canopy_flat_ceilings'] = sorted(spans, key=lambda s: -s['bridge_mm'])[:8]
for k, v in res.items(): print(k, v)
json.dump(res, open(OUT / 'checks.json', 'w'), indent=1, default=float)
with zipfile.ZipFile(ROOT / 'cad/08-Printed-lid.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted(OUT.iterdir()): z.write(f, f.name)
