"""Clearance, assembly-sequence and mesh checks for the cradle drive (box coordinates).
Usage: python checks.py [--gearset fast|v1pinion]"""
import argparse, json, os, pickle, numpy as np
from pathlib import Path
from cradle_drive import *
from scipy.ndimage import map_coordinates
import mesh_check

ap = argparse.ArgumentParser(); ap.add_argument('--gearset', default='fast', choices=GEARSETS); args = ap.parse_args()
L = Layout(args.gearset)
parts = pickle.load(open(Path(__file__).parent / f'parts-{L.name}.pkl', 'rb'))
D = L.donor()
res = {'gearset': L.name}

def spool_clear(P):
    r = np.hypot(P[:, 0] - SPOOL_C[0], P[:, 2] - SPOOL_C[1]); ay = np.abs(P[:, 1]); c = np.full(len(P), np.inf)
    m = ay < Y['tread_r'][0]; c[m] = r[m] - ENVELOPE_R                       # between the narrowest flanges: filament only
    m = (ay >= Y['tread_r'][0]) & (ay <= SPOOL_W / 2); c[m] = r[m] - FLANGE_R  # any supported spool may put a flange here
    return c

def rotating_clear(P, skip_gear=False):
    r = np.hypot(P[:, 0] - PITCH, P[:, 2] - ROD_Z); y = P[:, 1]; lim = np.full(len(P), -np.inf)
    bands = [(Y['roller'], CORE_R), (Y['tread_l'], TREAD_R), (Y['tread_r'], TREAD_R), (Y['key'], 4.0), (Y['bearing'], 7.0)]
    if not skip_gear: bands.append(((L.Y['gear'][0], L.Y['chamfer'][1]), L.GEAR_OD / 2))
    for (a, b), R in bands:
        m = (y >= a) & (y <= b); lim[m] = np.maximum(lim[m], R)
    return r - lim

def box_clear(P, lo, hi):
    lo = np.array(lo); hi = np.array(hi); q = np.maximum(lo - P, P - hi)
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0)

FEATURES = {   # approximate molded features (photo-derived, +/-2-3 mm): see docs/measurements
    # positions relative to the front rod (photo estimates at pitch 107 shifted with PITCH)
    'front cradle plates (rod-9..rod+8, |y|39.5-45.5, z<=28, minus slot)': [((PITCH - 9, -45.5, 0), (PITCH + 8, -39.5, CRADLE_TOP)), ((PITCH - 9, 39.5, 0), (PITCH + 8, 45.5, CRADLE_TOP))],
    'plug-rim crest band (rod+17..rod+28, z<=16.2)': [((PITCH + 17, -45, 0), (PITCH + 28, 45, CREST_Z))],
    'end-wall loop (x>=rod+28, |y|<=20)': [((PITCH + 28, -20, 0), (PITCH + 43, 20, 55))],
    'floor / plug top under the rod (z<=4.8)': [((PITCH - 17, -45, 0), (PITCH + 28, 45, 4.8))],
}
slot = lambda P: (np.abs(P[:, 0] - PITCH) < 7.05) & (P[:, 2] > 14.9) & (np.abs(P[:, 1]) > 39.4)
def feat(P, name, is_rotor_or_key):
    c = np.min([box_clear(P, lo, hi) for lo, hi in FEATURES[name]], axis=0)
    if 'cradle' in name and is_rotor_or_key: c = c[~slot(P)]
    return c.min()

def ring(y0, y1, R, x0=PITCH, z0=ROD_Z, n=6000):
    rng = np.random.default_rng(0); t = rng.uniform(0, 2 * np.pi, n); y = rng.uniform(y0, y1, n)
    return np.column_stack([x0 + R * np.cos(t), y, z0 + R * np.sin(t)])

statics = {'motor bracket': parts['07d-Motor-bracket-cradle-key'][0], 'N20 (dense envelope)': D['n20_env'],
           'N20 (donor vertices)': D['n20'], 'pinion (tip circle)': ring(*L.Y['pinion'], L.PIN_OD / 2, L.A_X, L.A_Z)}
rotors = {'roller gear (tip circle)': ring(*L.Y['gear'], L.GEAR_OD / 2), 'roller': parts['07a-Roller-with-gear'][0],
          'treads': np.concatenate([parts['07b-Tread-sleeve-TPU-L'][0], parts['07b-Tread-sleeve-TPU-R'][0]])}
for n, P in statics.items():
    r = {'spool': spool_clear(P).min(), 'rotating drive' + (' (gear band skipped: meshing)' if 'pinion' in n else ''): rotating_clear(P, 'pinion' in n).min()}
    for f in FEATURES: r[f] = feat(P, f, n == 'motor bracket')
    res[n] = {k: round(float(v), 2) for k, v in r.items()}
for n, P in rotors.items():
    r = {'spool (tread contact = 0 by design)': spool_clear(P).min()}
    for f in FEATURES: r[f] = feat(P, f, True)
    res[n] = {k: round(float(v), 2) for k, v in r.items()}

res['tread tangency |C-front| - (R_flange + R_tread)'] = round(float(np.linalg.norm(SPOOL_C - FRONT) - FLANGE_R - TREAD_R), 6)
res['rear roller tangency |C-rear| - (R_flange + 4)'] = round(float(np.linalg.norm(SPOOL_C - REAR) - FLANGE_R - 4), 6)
s, g = L.bracket(sdf_only=True)
sd = lambda P: map_coordinates(s, ((P - g.lo) / g.h).T, order=1, mode='nearest')
res['N20 vs bracket: deepest point (negative = inside)'] = round(float(sd(np.concatenate([D['n20'], D['n20_env']])).min()), 2)
res['N20 resting gap above the motor floor'] = round(float(L.A_Z - 6.53 - L.FLOOR_TOP), 2)
res['N20 to cross member (zip-tie gap)'] = round(float(L.CROSS_X[0] - (L.A_X + 5.69)), 2)
res['pinion vs bracket (SDF)'] = round(float(sd(statics['pinion (tip circle)']).min()), 2)
if L.name == 'v1pinion': res['V1.0 pinion vertices vs bracket (SDF)'] = round(float(sd(D['v1_pinion']).min()), 2)
res['pinion to bracket floor (axial)'] = round(float(L.Y['pinion'][0] - FACE_Y), 2)
res['gear centre distance'] = round(float(np.hypot(L.A_X - PITCH, L.A_Z - ROD_Z)), 3)
w, gmin, tip = mesh_check.run(L.Z_GEAR, L.Z_PIN, m=L.M, cd=L.CD)
res['gear mesh over a tooth cycle: interference / min flank distance / tip-to-root'] = [round(w, 3), round(gmin, 3), round(tip, 2)]
Pb = parts['07d-Motor-bracket-cradle-key'][0]; rc = rotating_clear(Pb); kb = (Pb[:, 1] >= Y['key'][0] - 0.01) & (Pb[:, 1] <= Y['key'][1] + 0.01)
res['bracket vs rotating, outside the key bushing'] = round(float(rc[~kb].min()), 2)
res['key bushing radial clearance on Ø8 rod'] = round(float(rc[kb].min()), 2)
# assembly: bracket on rod -> roller (treads on) slid on from +Y -> bearing -> drop into cradles -> N20 dropped in from above
res['assembly: treads passing the motor floor (radial)'] = round(float(L.FLOOR_X0 - (PITCH + TREAD_R)), 2)
res['assembly: roller gear never passes a bracket part (gear starts past the bracket by)'] = round(float(L.Y['gear'][0] - FACE_Y), 2)
dz = np.linspace(0, 40, 401)
res['assembly: N20 lowered vertically, min distance to rod axis - CD'] = round(float(np.hypot(L.A_X - PITCH, L.A_Z + dz - ROD_Z).min() - L.CD), 4)
res['axial gaps key | roller | bearing'] = [round(Y['roller'][0] - Y['key'][1], 2), round(Y['bearing'][0] - Y['roller'][1], 2)]
res['narrowest spool fully on treads (mm)'] = 2 * Y['tread_r'][0]
res['tread OD needed for pitch 106 / 107 / 108 / 109'] = [round(tread_od_for_pitch(p), 2) for p in (106, 107, 108, 109)]
res['negative clearances'] = [(k, kk, vv) for k, v in res.items() if isinstance(v, dict) for kk, vv in v.items() if vv < 0]
print(json.dumps(res, indent=1, ensure_ascii=False))
out = Path(os.environ.get('POLYTURTLE_CHECKS_OUT', L.OUT / 'checks.json'))
json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
