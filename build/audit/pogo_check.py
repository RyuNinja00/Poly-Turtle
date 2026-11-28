"""Pogo disconnect: clearances of the holder, puck, connectors and box block against everything around them."""
import sys, json, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'build/cradle-drive/tools')); sys.path.insert(0, str(ROOT / 'build/lid'))
import meshkit as mk, columns, printed_lid as P, pogo, extras as E
from scipy.spatial import cKDTree
src = open(HERE / 'assembly.py').read()
exec(src[src.index('H = 0.25'):src.index('res = {}')].split('res = {}')[0].replace("C / '", "ROOT / 'cad' / '"))
OUT = ROOT / 'cad/08-printed-lid'; M2B = np.array([54.5, 0.0, 113.498])
lid = mk.read_stl(OUT / '08-Printed-lid.stl'); car = mk.read_stl(OUT / '08c-feeder-carrier.stl'); box = mk.read_stl(ROOT / 'cad/04-Printable-box-PROXY.stl')
tri = lambda VT: VT[0][VT[1]]
env = {k: tri(v) for k, v in pogo.envelopes().items()}
block = tri(pogo.box_block(placed=True)); plate = tri(pogo.lip_plate(placed=True)); heads = tri(pogo.screw_heads()); holder = tri(pogo.lid_holder())
LIDP = np.concatenate([plate, heads])
puck_lo = tri(pogo.puck(at=pogo.F_LOW)); puck_hi = tri(pogo.puck(at=pogo.F_LOW + pogo.FLOAT['up']))
LID, CAR, BOX = Occ(lid), Occ(car), Occ(box)
res = {}
male_lo = np.concatenate([env['male_low'], puck_lo]); male_hi = np.concatenate([env['male_high'], puck_hi])
pair('male + puck, lid off (resting on the lip) vs lid', male_lo, LID, res)
pair('male + puck, top of float vs lid', male_hi, LID, res, 'puck touches the holder roof at the top of its float')
pair('male + puck vs lip plate', male_lo, Occ(LIDP), res, 'puck rests on the plate')
pair('male + puck vs carrier', male_hi, CAR, res)
fb = np.concatenate([env['female'], block])
for dz in (0.0, -1.0, 1.0):
    pair(f'female + box block vs lid, plate and screw heads, lid {dz:+.0f} mm', fb, Occ(np.concatenate([lid, LIDP]) + [0, 0, dz]), res)
pair('female + box block vs carrier', fb, CAR, res)
pair('box block vs box proxy', block, BOX, res, 'positive = gap to the proxy wall, filled with VHB')
pair('male (lid off) vs box proxy', male_lo, BOX, res)
SC = np.array([-6.072, 3.354])
def spool_gap(t):
    p = sample(t); m = np.abs(p[:, 1]) <= 39; return round(float((np.hypot(p[m, 0] - SC[0], p[m, 2] - SC[1]) - 102.5).min()), 2) if m.any() else None
res['spool gap'] = dict(block=spool_gap(fb), male_lid_off=spool_gap(male_lo), holder=spool_gap(holder), plate_and_heads=spool_gap(LIDP))
drive = np.concatenate([mk.read_stl(p) - M2B for p in sorted((ROOT / 'cad/07-cradle-drive').glob('07*.stl'))])
res['drive to block min mm'] = round(float(cKDTree(sample(drive)).query(sample(fb))[0].min()), 1)
# free filament: spool tangent points (checks.json inlet_routing) across the spool width, straight to the mouth
ck = json.load(open(OUT / 'checks.json')); M = np.array(ck['guide']['mouth_xyz'])
kd = cKDTree(sample(np.concatenate([fb, male_lo]), 0.3)); worst = 99
for row in ck['inlet_routing']:
    tx, tz = row['leaves_spool_at']
    for y0 in np.linspace(-39, 39, 27):
        seg = np.linspace([tx, y0, tz], M, 400); d = kd.query(seg)[0].min(); worst = min(worst, d)
res['filament path to pogo parts min mm'] = round(float(worst), 2)
print(json.dumps(res, indent=1, default=float))
json.dump(res, open(HERE / 'pogo.json', 'w'), indent=1, default=float)
