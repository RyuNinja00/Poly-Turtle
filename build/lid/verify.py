"""Independent verification of the rev 3 lid on the FINAL meshes (not the design fields).

Occupancy: exact z-intervals along 0.25 mm columns of each closed shell (ray parity).
Distances: nearest-vertex distance to the final meshes (vertex spacing <= 0.4 mm).
Also checks the module against the printable box proxy (cad/04) with the lid closed.
Writes cad/08-printed-lid/verify.json."""
import sys, json, pickle, numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk
import printed_lid as P, columns
from pose import TF0, A0, V0
OUT = ROOT / 'cad/08-printed-lid'
H = 0.25

def shells(path):
    t = mk.read_stl(path); V = t.reshape(-1, 3); T = np.arange(len(V)).reshape(-1, 3); V, T = mk.weld(V, T, 1e-5)
    # connected components over shared vertices
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]]])
    n, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(len(V), len(V))), directed=False)
    out = []
    for k in range(n):
        tk = T[lab[T[:, 0]] == k]
        if len(tk): out.append((V, tk))
    return out

class Occ:
    """union of closed shells; z-intervals on a column grid"""
    def __init__(self, shell_list, lo, hi):
        self.xs = np.arange(lo[0], hi[0] + H / 2, H); self.ys = np.arange(lo[1], hi[1] + H / 2, H); self.lo = np.array(lo[:2])
        self.iv = [columns.intervals(V[T], self.xs, self.ys, kmax=8) for V, T in shell_list]
    def inside(self, P):
        i = np.clip(np.round((P[:, 0] - self.lo[0]) / H).astype(int), 0, len(self.xs) - 1)
        j = np.clip(np.round((P[:, 1] - self.lo[1]) / H).astype(int), 0, len(self.ys) - 1)
        ok = (P[:, 0] >= self.xs[0]) & (P[:, 0] <= self.xs[-1]) & (P[:, 1] >= self.ys[0]) & (P[:, 1] <= self.ys[-1])
        res = np.zeros(len(P), bool)
        for lo_, hi_ in self.iv:
            a, b = lo_[i, j], hi_[i, j]; z = P[:, 2:3]
            res |= np.any((z >= a) & (z <= b), 1)
        return res & ok
    def column(self, x, y):
        i = int(round((x - self.lo[0]) / H)); j = int(round((y - self.lo[1]) / H))
        segs = []
        for lo_, hi_ in self.iv:
            for a, b in zip(lo_[i, j], hi_[i, j]):
                if not np.isnan(a): segs.append((round(float(a), 2), round(float(b), 2)))
        return sorted(segs)

def merged(segs, tol=0.05):
    out = []
    for a, b in sorted(segs):
        if out and a <= out[-1][1] + tol: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out

res = {}
lid_sh = shells(OUT / '08-Printed-lid.stl'); car_sh = shells(OUT / '08c-feeder-carrier.stl')
res['shells'] = dict(lid=[len(T) for _, T in lid_sh], carrier=[len(T) for _, T in car_sh])
res['shells_closed'] = [mk.check_mesh(V, T)['edges_not_2'] == 0 for V, T in lid_sh + car_sh]
box = shells(ROOT / 'cad/04-Printable-box-PROXY.stl')

LID = Occ(lid_sh, (-118, -60), (118, 60)); CAR = Occ(car_sh, (10, -42), (102, 4)); BOX = Occ(box, (-118, -60), (118, 60))
Vl = np.concatenate([V[np.unique(T)] for V, T in lid_sh]); Vc = np.concatenate([V[np.unique(T)] for V, T in car_sh])
kl, kc = cKDTree(Vl), cKDTree(Vc)
Vbox = np.concatenate([V[np.unique(T)] for V, T in box]); kb = cKDTree(Vbox)

cl = pickle.load(open(HERE / 'clouds.pkl', 'rb')); smol, prep = P.POSE(cl['smol']), P.POSE(cl['prep'])
W0 = np.cross(V0, A0); d0 = cl['smol'] - TF0; Ls = np.stack([d0 @ A0, d0 @ W0, d0 @ V0], -1)
iface = (Ls[:, 1] > 16.0) & (Ls[:, 2] < P.BASE_V + 0.05) & (Ls[:, 0] > -34) & (Ls[:, 0] < 48)
module = {'smol': smol, 'prep': prep, 'carrier': Vc[::2]}

def rep(name, pts, occ, kd, skip_inside=False):
    ins = occ.inside(pts); d, i = kd.query(pts)
    r = dict(points=int(len(pts)), inside=int(ins.sum()), min_gap_mm=round(float(d[~ins].min()), 2) if (~ins).any() else None,
             at=pts[~ins][np.argmin(d[~ins])].round(1).tolist() if (~ins).any() else None)
    res[name] = r; return r

for k, pts in module.items():
    rep(f'lid_vs_{k}', pts, LID, kl)
    rep(f'boxproxy_vs_{k}', pts, BOX, kb)
rep('carrier_vs_smol (excl. trayframe interface)', smol[~iface], CAR, kc)
rep('carrier_vs_prep', prep, CAR, kc)

# spool envelope vs lid and vs box proxy
SC = np.array([-6.072, 3.354])
th = np.linspace(0.05, np.pi - 0.05, 1600); ys = np.linspace(-39, 39, 79)
S = np.array([[SC[0] + 102.5 * np.cos(t), y, SC[1] + 102.5 * np.sin(t)] for t in th for y in ys]); S = S[S[:, 2] > 55]
rep('lid_vs_spool205', S, LID, kl)
allm = np.concatenate(list(module.values())); m = np.abs(allm[:, 1]) <= 39
r = np.hypot(allm[m, 0] - SC[0], allm[m, 2] - SC[1]) - 102.5
res['module_vs_spool205'] = dict(min_mm=round(float(r.min()), 2), at=allm[m][np.argmin(r)].round(1).tolist())

# drop-in sweep against the final lid (lid upside-down = module rises; same geometry)
worst, hits = 99.0, 0
for dz in np.arange(0, 110, 1.0):
    q = allm - [0, 0, dz]; q = q[q[:, 2] > 59.5]
    if not len(q): break
    ins = LID.inside(q); hits += int(ins.sum()); worst = min(worst, float(kl.query(q[~ins])[0].min()))
res['drop_in'] = dict(points_inside=hits, min_gap_mm=round(worst, 2))

# seam: wall columns where the base ends at Z 102 must continue (or be the groove's foot)
seam = []
for x in np.arange(-98, 99, 7.0):
    for y in (-46.0, -44.0, -41.5, 41.5, 44.0, 46.0):
        if not LID.inside(np.array([[x, y, 101.5]]))[0]: continue
        mz = merged(LID.column(x, y))
        top_of_101 = [b for a, b in mz if a <= 101.5 <= b]
        seam.append(dict(x=x, y=y, solid_to=top_of_101[0] if top_of_101 else None))
gaps = [s for s in seam if s['solid_to'] is not None and s['solid_to'] < 103.0]
res['seam'] = dict(wall_columns=len(seam), columns_ending_below_Z103=len(gaps), examples=gaps[:6])

# end caps: final lid vs jojo above Z 102 for |x| > 100.5
Vj, Tj = P.endcap_tri(); JO = Occ([(Vj, Tj)], (-118, -60), (118, 60))
diff = 0; tot = 0; worst_col = None
for x in list(np.arange(-116, -100.4, 0.5)) + list(np.arange(100.5, 116.1, 0.5)):
    for y in np.arange(-58, 58.1, 0.5):
        zs = np.arange(102.1, 111.5, 0.1); Q = np.column_stack([np.full_like(zs, x), np.full_like(zs, y), zs])
        a = JO.inside(Q); b = LID.inside(Q)
        dd = int((a != b).sum()); diff += dd; tot += int(a.sum())
        if dd and (worst_col is None or dd > worst_col[2]): worst_col = (float(x), float(y), dd)
res['endcaps_vs_jojo'] = dict(jojo_samples=tot, mismatched_samples=diff, mismatch_pct=round(100 * diff / max(tot, 1), 2), worst_column=worst_col,
                              note='includes the intended changes: the +X canopy wall over the bar (x <= 102.5) and the filled -X port')
# finger slots: open above the end-cap floor?
for sx in (1, -1):
    Q = np.array([[sx * 108.0, y, 110.0] for y in np.arange(-20, 21, 2.0)])
    res[f'finger_slot_{"+" if sx > 0 else "-"}X_open_at_Z110'] = bool(not LID.inside(Q).any()) if not JO.inside(Q).any() else 'jojo solid here'

# wall screws: lid hole open along the axis, insert pocket wall in the carrier, M3x12 tip clear of the Smol
ws = {}
for k, u in P.PADS.items():
    x, z = P.pad_screw(u); ys_ = np.arange(-48, -38, 0.1); Q = np.column_stack([np.full_like(ys_, x), ys_, np.full_like(ys_, z)])
    ring_c = np.array([[x + 2.9 * np.cos(a), y_, z + 2.9 * np.sin(a)] for a in np.linspace(0, 2 * np.pi, 16, endpoint=False) for y_ in (-38.5, -36.0, -34.0)])
    ring_l = np.array([[x + 2.4 * np.cos(a), -40.0, z + 2.4 * np.sin(a)] for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)])
    tip = -46.6 + 12.0
    r = np.hypot(smol[:, 0] - x, smol[:, 2] - z); yy = np.clip(smol[:, 1], -47, tip)
    ws[k] = dict(x=round(x, 2), z=round(z, 2), lid_hole_blocked=int(LID.inside(Q).sum()), lid_standoff_ring_solid=f"{int(LID.inside(ring_l).sum())}/16",
                 carrier_insert_wall_solid=f"{int(CAR.inside(ring_c).sum())}/48", outer_wall_y=round(float(ys_[LID.inside(np.column_stack([np.full_like(ys_, x + 3), ys_, np.full_like(ys_, z)]))].min()), 2),
                 m3x12_tip_y=tip, m3x12_gap_to_smol_mm=round(float((np.sqrt(r ** 2 + (smol[:, 1] - yy) ** 2) - 1.5).min()), 2))
res['wall_screws'] = ws

# outlet: bore clear through, fitting tip vs Smol
uf = P.outlet_u(); us = np.arange(uf - 2, uf + 12, 0.1); Q = np.array([P.glob(u, 0, 0) for u in us])
ring = np.array([P.glob(u, 4.4 * np.cos(a), 4.4 * np.sin(a)) for u in us for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)])
d0s = smol - P.TF; su = d0s @ P.A; sr = np.hypot(d0s @ P.W, d0s @ P.V_)
res['outlet'] = dict(bore_axis_blocked=int(LID.inside(Q).sum()), bore_r4_4_blocked=int(LID.inside(ring).sum()),
                     smol_max_u_within_r6=round(float(su[sr < 6].max()), 2), inner_face_u=round(uf, 2),
                     boss_axis_solid_length_mm=round(float(0.1 * LID.inside(np.array([P.glob(u, 5.5, 0) for u in us])).sum()), 1))
# gland: hole open and nut space (r 10, 9 deep under the ceiling) free of module and spool
mx, my = P.MF_AT['x'], P.MF_AT['y']; ax_, ay_ = P.E.MF['aperture']
pts = np.array([[mx + dx, my + dy, z] for dx in np.linspace(-ax_ / 2 + 0.4, ax_ / 2 - 0.4, 9) for dy in np.linspace(-ay_ / 2 + 0.4, ay_ / 2 - 0.4, 5) for z in np.arange(120, 140, 0.5)])
col_r = merged(LID.column(mx, my + ay_ / 2 + 2.0))
roof = [(a, b) for a, b in col_r if a > 110]
screws = [int(LID.inside(np.array([[mx + sx * P.E.MF['screw_dx'] + 1.4 * np.cos(t), my + 1.4 * np.sin(t), z] for t in np.linspace(0, 6.28, 8) for z in np.arange(120, 140, 0.5)])).sum()) for sx in (-1, 1)]
plate_l = P.E.MF['plate'][0]; flat = []
for dx in np.linspace(-plate_l / 2, plate_l / 2, 9):
    for dy in (-11.0, 0.0, 11.0):
        c = merged(LID.column(mx + dx, my + dy)); flat.append(max(b for a, b in c) if c else None)
ceil = roof[0][0] if roof else None
res['microfit_plate'] = dict(aperture_blocked=int(LID.inside(pts).sum()), screw_holes_blocked=screws, roof=roof,
                             plate_seat_top_z=[min(f for f in flat if f), max(f for f in flat if f)],
                             space_under_roof_to_spool_mm=round(float(ceil - (SC[1] + np.sqrt(102.5 ** 2 - (mx - SC[0]) ** 2))), 1) if ceil else None,
                             module_within_20mm=int((np.hypot(allm[:, 0] - mx, allm[:, 1] - my) < 20).sum()))
# outlet thread present: crest/root hits on the bushing at r 4.8 (between minor 4.55 and major 5.15)
uq = np.arange(uf - 0.5, P.outlet_face() - P.E.GROOVE['depth'] - 0.2, 0.05)
probe = np.array([P.glob(u, 4.85, 0.0) for u in uq])
hit = LID.inside(probe)
res['outlet_thread'] = dict(solid_fraction_at_r4_85=round(float(hit.mean()), 2), transitions=int(np.abs(np.diff(hit.astype(int))).sum()))
# filament path: guide bore + axis under PREP, clear of carrier (r 0.9)
R = P.GUIDE['R']; ph = np.linspace(-np.radians(P.GUIDE['sweep']), 0, 80)
path = [P.glob(-50 + R * np.sin(p), 0, -R + R * np.cos(p)) for p in ph] + [P.glob(u, 0, 0) for u in np.arange(-50, uf + 8, 0.25)]
path = np.array(path)
tube = np.array([p + 0.9 * (np.cos(a) * P.W + np.sin(a) * P.V_) for p in path for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)])
liner = np.array([P.glob(-50 + R * np.sin(p), 0, -R + R * np.cos(p)) + 2.0 * (np.cos(a) * P.W + np.sin(a) * (np.sin(p) * P.A + np.cos(p) * P.V_) ) for p in ph[:-2] for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)])
def surf_pts(t, a2=0.003):
    a, b, c = t[:, 0], t[:, 1], t[:, 2]; rng = np.random.default_rng(1); out = [t.reshape(-1, 3)]
    n = np.clip((np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2 / a2).astype(int), 0, 400)
    for k in np.unique(n[n > 0]):
        m = n == k; q = rng.random((m.sum(), k, 2)); f = q.sum(2) > 1; q[f] = 1 - q[f]
        out.append((a[m][:, None] + q[..., :1] * (b - a)[m][:, None] + q[..., 1:] * (c - a)[m][:, None]).reshape(-1, 3))
    return np.concatenate(out)
# exact bore radius: nearest carrier surface to the guide arc axis (the r 2.0 point probe above is limited by the 0.25 grid)
Qc = surf_pts(mk.read_stl(OUT / '08c-feeder-carrier.stl')) - P.TF; Lc = np.column_stack([Qc @ P.A, Qc @ P.W, Qc @ P.V_])
phi_c = np.degrees(np.arctan2(Lc[:, 0] + 50, Lc[:, 2] + R)); r_c = np.hypot(np.hypot(Lc[:, 0] + 50, Lc[:, 2] + R) - R, Lc[:, 1])
m_c = (phi_c > -P.GUIDE['sweep'] + 0.5) & (phi_c < -2.0) & (r_c < 3)   # stop 0.7 mm short of the liner shoulder (rounded by the 0.4 mm grid)
res['guide_bore_min_radius_mm'] = round(float(r_c[m_c].min()), 3)
res['filament_path'] = dict(liner_od4_point_probe_hits=int(CAR.inside(liner).sum()), carrier_blocks=int(CAR.inside(tube).sum()), lid_blocks=int(LID.inside(tube).sum()),
                            smol_points_within_0p9=int((cKDTree(path).query(smol)[0] < 0.9).sum()))
# Smol bolts: tails of A and B pass the carrier inserts/relief
bolts = {}
for k, (u, w) in P.BOLTS.items():
    Q = np.array([P.glob(u, w, v) for v in np.arange(-8.7, P.BASE_V + 0.5, 0.1)])
    Qr = np.array([P.glob(u + 1.45 * np.cos(a), w + 1.45 * np.sin(a), v) for v in np.arange(-8.7, P.BASE_V, 0.5) for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)])
    bolts[k] = dict(axis_blocked=int(CAR.inside(Q).sum()), m3_shank_r1_45_blocked=int(CAR.inside(Qr).sum()),
                    insert_wall_solid=int(CAR.inside(np.array([P.glob(u + 2.6 * np.cos(a), w + 2.6 * np.sin(a), 2.0) for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)])).sum()))
res['smol_bolts'] = bolts
for k, v in res.items(): print(k, v)
json.dump(res, open(OUT / 'verify.json', 'w'), indent=1, default=float)
