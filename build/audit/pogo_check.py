"""Pogo disconnect rev 2: clearances of the lid pocket, the print-in-place box part, the bumpers and the connectors."""
import sys, json, pickle, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'build/cradle-drive/tools')); sys.path.insert(0, str(ROOT / 'build/lid'))
from scipy.spatial import cKDTree
import meshkit as mk, columns, pogo
src = open(HERE / 'assembly.py').read(); exec(src[src.index('H = 0.25'):src.index('res = {}')])
OUT = ROOT / 'cad/08-printed-lid'; M2B = np.array([54.5, 0.0, 113.498])
tri = lambda VT: VT[0][VT[1]]
lid = mk.read_stl(OUT / '08-Printed-lid.stl'); car = mk.read_stl(OUT / '08c-feeder-carrier.stl'); box = mk.read_stl(ROOT / 'cad/04-Printable-box-PROXY.stl')
env = {k: tri(v) for k, v in pogo.envelopes().items()}
frame, carrier = tri(pogo.frame()), tri(pogo.carrier()) - [0, 0, pogo.CAR['flange'][0] - pogo.FR['floor']]   # as installed: on the floor
bumps = np.concatenate([tri(pogo.bumper_placed(1)), tri(pogo.bumper_placed(-1))])
LID, CAR, BOX = Occ(lid), Occ(car), Occ(box)
res = {}
pair('male vs lid (clipped in)', env['male'], LID, res, 'flange rests on the pocket beams by design')
pair('male vs lid-side carrier (feeder)', env['male'], CAR, res)
moving = np.concatenate([carrier, env['female']])
for up in (0.0, 1.0, 1.6):      # lid seated as installed, or higher: magnets lift the carrier to follow
    pair(f'box part (carrier lifted {up} mm) vs lid {up:+.1f} mm', np.concatenate([frame, moving + [0, 0, up]]), Occ(lid + [0, 0, up]), res)
pair('box part + bumpers vs feeder carrier', np.concatenate([frame, moving, bumps]), CAR, res)
pair('frame vs box proxy', frame, BOX, res, 'bar ends stop 4+ mm short of the walls; the TPU bumpers take the gap')
SC = np.array([-6.072, 3.354])
def spool_gap(t):
    p = sample(t); m = np.abs(p[:, 1]) <= 39; return round(float((np.hypot(p[m, 0] - SC[0], p[m, 2] - SC[1]) - 102.5).min()), 2) if m.any() else None
res['spool gap'] = dict(frame=spool_gap(frame), carrier_and_female=spool_gap(moving), lid_pocket=spool_gap(tri(pogo.lid_pocket())))
drive = np.concatenate([mk.read_stl(p) - M2B for p in sorted((ROOT / 'cad/07-cradle-drive').glob('07*.stl'))])
res['drive to box part min mm'] = round(float(cKDTree(sample(drive)).query(sample(np.concatenate([frame, moving, bumps])))[0].min()), 1)
ck = json.load(open(OUT / 'checks.json')); M = np.array(ck['guide']['mouth_xyz'])
kd = cKDTree(sample(np.concatenate([frame, moving, bumps]), 0.3)); worst = 99
for row in ck['inlet_routing']:
    tx, tz = row['leaves_spool_at']
    for y0 in np.linspace(-39, 39, 27):
        seg = np.linspace([tx, y0, tz], M, 400); worst = min(worst, kd.query(seg)[0].min())
res['filament path to box part min mm'] = round(float(worst), 2)
# bumper reach vs proxy side walls at the bar height
res['bumper free reach |y|'] = pogo.report()['bumper']['free_reach_y']

# taped option: same carrier, frame with a flat wall face instead of the bar
tframe = tri(pogo.frame('tape'))
for up in (0.0, 1.6):
    pair(f'TAPE: block (carrier lifted {up} mm) vs lid {up:+.1f} mm', np.concatenate([tframe, moving + [0, 0, up]]), Occ(lid + [0, 0, up]), res)
pair('TAPE: block vs feeder carrier', np.concatenate([tframe, moving]), CAR, res)
pair('TAPE: block vs box proxy', tframe, BOX, res, 'gap = foam-tape thickness on the proxy')
res['TAPE: spool gap'] = spool_gap(tframe)
kd = cKDTree(sample(np.concatenate([tframe, moving]), 0.3)); worst = 99
for row in ck['inlet_routing']:
    tx, tz = row['leaves_spool_at']
    for y0 in np.linspace(-39, 39, 27):
        worst = min(worst, kd.query(np.linspace([tx, y0, tz], M, 400))[0].min())
res['TAPE: filament path min mm'] = round(float(worst), 2)
print(json.dumps(res, indent=1, default=float))
json.dump(res, open(HERE / 'pogo.json', 'w'), indent=1, default=float)
