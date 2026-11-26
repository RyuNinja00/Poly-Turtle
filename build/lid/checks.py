"""Clearance, routing and assembly checks for the 08 printed lid, rev 2 (writes checks.json, packs the zip)."""
import sys, json, pickle, zipfile, numpy as np
from pathlib import Path
from scipy.ndimage import map_coordinates
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import printed_lid as P
import occ as O
from pose import TF0, A0, V0
W0 = np.cross(V0, A0)

D = np.load(HERE / 'sdf.npz'); OCC = np.load(HERE / 'occ.npz')['occ']
def sample(part, pts):
    k = part[0]; s, lo, h = D['s' + k], D[k + 'lo'], D[k + 'h']
    return map_coordinates(s, ((pts - lo) / h).T, order=1, mode='nearest')

cl = pickle.load(open(HERE / 'clouds.pkl', 'rb'))
smol0, prep0 = cl['smol'], cl['prep']
smol, prep = P.POSE(smol0), P.POSE(prep0)
d0 = smol0 - TF0; Ls = np.stack([d0 @ A0, d0 @ W0, d0 @ V0], -1)
iface = (Ls[:, 1] > 16.0) & (Ls[:, 2] < P.BASE_V + 0.05) & (Ls[:, 0] > -34) & (Ls[:, 0] < 48)

res = dict(pose=dict(alpha_deg=P.ALPHA, inlet_xyz=list(P.INLET), note='travel rises toward -X; inlet/PREP low at +X'))
def clr(tag, part, pts):
    d = sample(part, pts); i = int(np.argmin(d))
    res[tag] = dict(min_mm=round(float(d[i]), 2), at=pts[i].round(1).tolist())
clr('hood_vs_smol', 'hood', smol); clr('hood_vs_prep', 'hood', prep)
clr('carrier_vs_smol (excl. replaced trayframe interface)', 'carrier', smol[~iface])
clr('carrier_vs_prep (switch sits on the block)', 'carrier', prep)
res['replaced_interface_points'] = int(iface.sum())

def verts(name):
    t = mk.read_stl(ROOT / 'cad/08-printed-lid' / name).reshape(-1, 3); return np.unique(t.round(3), axis=0)
Vh, Vc = verts('08b-hood.stl'), verts('08c-feeder-carrier.stl')
clr('carrier_vs_hood', 'hood', Vc[::3])

SC = np.array([-6.072, 3.354])
def spool(V, R=102.5):
    m = np.abs(V[:, 1]) <= 39.0; r = np.hypot(V[m, 0] - SC[0], V[m, 2] - SC[1]) - R
    i = int(np.argmin(r)); return dict(min_mm=round(float(r[i]), 2), at=V[m][i].round(1).tolist())
res['smol_prep_vs_spool'] = spool(np.concatenate([smol, prep]))
res['hood_vs_spool'] = spool(Vh); res['carrier_vs_spool'] = spool(Vc)
res['hood_below_plate_in_lid'] = int(O.lookup(OCC, Vh[Vh[:, 2] < P.PLATE_TOP - 0.3]).sum())
res['carrier_in_lid'] = int(O.lookup(OCC, Vc[Vc[:, 2] < P.PLATE_TOP - 0.3]).sum())
res['smol_prep_in_lid'] = int(O.lookup(OCC, np.concatenate([smol, prep])).sum())

# drop-in: carrier + Smol + PREP go straight up through the opening
fp = np.concatenate([Vc, smol, prep])
res['module_xy_range'] = [round(float(v), 2) for v in (fp[:, 0].min(), fp[:, 0].max(), fp[:, 1].min(), fp[:, 1].max())]
res['module_fits_opening'] = bool(fp[:, 0].min() > P.RING_IN[0] and fp[:, 0].max() < P.RING_IN[1] and fp[:, 1].min() > P.RING_IN[2] and fp[:, 1].max() < P.RING_IN[3])
res['module_bottom_z'] = round(float(fp[:, 2].min()), 2)

# inlet routing: free filament from the +X side of the spool to the guide mouth
m, t = P.mouth()
M = P.glob(m[0], 0, m[1]); Tm = t[0] * P.A + t[1] * P.V_            # forward direction at the mouth
inlet_rows = []
for R in (102.5, 80.0, 60.0, 45.0):
    pin = np.array([M[0], M[2]]); dv = pin - SC; L = np.linalg.norm(dv)
    th = np.arcsin(R / L); base = np.arctan2(-dv[1], -dv[0]); best = None
    for s in (1, -1):
        ang = base + s * th; tdir = np.array([np.cos(ang), np.sin(ang)]); tp = pin + tdir * np.sqrt(L * L - R * R)
        if best is None or tp[0] > best[0][0]: best = (tp, -tdir)
    tp, inc = best
    turn_mouth = float(np.degrees(np.arccos(np.clip(inc @ np.array([Tm[0], Tm[2]]), -1, 1))))
    seg = np.linspace(np.array([tp[0], M[1], tp[1]]), M - Tm * 1.0, 60)
    hit_c = float(sample('carrier', seg[:-3]).min()); hit_lid = int(O.lookup(OCC, seg).sum())
    smol_gap = float(np.min(np.linalg.norm(smol[None, ::7] - seg[:, None], axis=2)))
    inlet_rows.append(dict(spool_radius=R, leaves_spool_at=[round(float(tp[0]), 1), round(float(tp[1]), 1)],
                           turn_at_mouth_deg=round(turn_mouth, 1), path_clear_of_carrier_mm=round(hit_c, 2),
                           path_points_in_lid=hit_lid, path_to_smol_mm=round(smol_gap, 2)))
res['inlet_routing'] = inlet_rows
res['guide'] = dict(radius=P.GUIDE['R'], sweep_deg=P.GUIDE['sweep'], bore=2 * P.GUIDE['r_bore'], mouth_xyz=M.round(2).tolist())
res['outlet'] = dict(axis_at_wall_xyz=P.glob(57.7, 0, 0).round(2).tolist(), boss_u=[P.OUTLET['u_in'], P.OUTLET['u_out']], hole=P.OUTLET['hole'])
res['bolt_insert_axes'] = {k: P.glob(u, w, P.BASE_V).round(2).tolist() for k, (u, w) in P.BOLTS.items()}
res['roof_screws_xy'] = {k: [round(float(c), 2) for c in v] for k, v in P.SCREWS.items()}
res['hood_height_above_plate'] = round(P.ROOF_OUT - P.PLATE_TOP, 2)
for k, v in res.items(): print(k, v)
json.dump(res, open(ROOT / 'cad/08-printed-lid/checks.json', 'w'), indent=1, default=float)
with zipfile.ZipFile(ROOT / 'cad/08-Printed-lid.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted((ROOT / 'cad/08-printed-lid').iterdir()): z.write(f, f.name)
