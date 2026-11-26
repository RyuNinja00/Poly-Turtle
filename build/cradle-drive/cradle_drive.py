"""Poly-Turtle cradle drive (revision 2c): the respool drive in the factory
front-roller cradles of the molded PolyDryer box, built for the fewest steps.

One printed roller carries the gear and both TPU treads and simply runs on the
factory Ø8 rod: torque goes motor -> pinion -> roller gear -> treads and never
through the rod, so there are no grub screws, press fits or spacers.  The N20
drops into an open-top bracket and is held by two zip ties.

Gear sets (pick with --gearset):
  fast      (default) printed 15T m1 roller gear + printed 17T m1 pinion on the N20,
            rewind surface speed 93 % of BoxTurtle V1.0.
  v1pinion  keeps the V1.0 15T m0.75 pinion on the N20; printed 30T m0.75 roller gear
            at the V1.0 centre distance, rewind surface speed 41 % of V1.0.

Box coordinates (mm): X forward from the rear factory axle, Y lateral from the
spool midplane (same sense as the archived fit study), Z up from the interior floor.
Archived fit-study model -> box: X = x + 54.5, Z = z - rz + 22, rz = -sqrt(106.5^2 - 54.5^2).
"""
import argparse, json, pickle, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent / 'tools'))
from meshkit import *

ROOT = Path(__file__).resolve().parents[2]
STEP01 = ROOT / 'cad' / '01-Single-lane-fit-study.step'   # run transport/restore.py first

# ------------------------------------------------------------------ datums (measured / archived)
RZ = -np.sqrt(106.5 ** 2 - 54.5 ** 2)
MODEL_TO_BOX = np.array([54.5, 0.0, 22.0 - RZ])
ROD_Z = 22.0                       # both factory axles (measured rear; front from photos)
PITCH = 107.0                      # nominal factory roller pitch (photos 106-109) -> MEASURE
FLANGE_R, ENVELOPE_R, SPOOL_W = 102.5, 97.5, 78.0
dx = -6.072124302839878            # archived spool centre (design.py)
dz = RZ + np.sqrt(106.5 ** 2 - (dx + 54.5) ** 2)
SPOOL_C = np.array([dx, dz]) + MODEL_TO_BOX[[0, 2]]
REAR = np.array([0.0, ROD_Z]); FRONT = np.array([PITCH, ROD_Z])
TREAD_R = np.linalg.norm(SPOOL_C - FRONT) - FLANGE_R          # keeps the spool on the archived pose
CRADLE_TOP, CREST_Z = 28.0, 16.2
V10_SURFACE_PER_MOTOR_REV = np.pi * 43.76 * 15 / 30           # V1.0: Ø43.76 tread, 15T:30T

def tread_od_for_pitch(p):
    return 2 * (np.hypot(SPOOL_C[0] - p, SPOOL_C[1] - ROD_Z) - FLANGE_R)

GEARSETS = {
    'fast':     dict(m=1.0, zg=15, zp=17, cd=16.0, a_z=29.5, gear_w=6.0, pinion='printed 17T m1'),
    'v1pinion': dict(m=0.75, zg=30, zp=15, cd=17.101, a_z=31.0, gear_w=8.0, pinion='V1.0 15T m0.75 (kept on the N20)'),
}

# ------------------------------------------------------------------ fixed V1.0 / donor references
PIN_AXIS_M = np.array([76.620, -74.855]); N20_FACE_YM = -5.45
u_old = np.array([81.06 - 72.16, 0, -75.45 + 74.11]); u_old /= np.linalg.norm(u_old)
d_old = np.array([0, -1.0, 0]); w_old = np.cross(d_old, u_old)
d_new, u_new = np.array([0, 1.0, 0]), np.array([0, 0, 1.0]); w_new = np.cross(d_new, u_new)
R_N20 = np.column_stack([w_new, d_new, u_new]) @ np.column_stack([w_old, d_old, u_old]).T   # shaft +Y, screw line +Z
BEARING_MODEL_C = np.array([74.075, -17.82, -91.765])
T_BEARING = np.array([PITCH, 42.0, ROD_Z]) - BEARING_MODEL_C
FACE_Y = 5.45                      # N20 gearbox face; pinion starts 1 mm beyond it, as on V1.0
CORE_R, BORE_R, BUSH_R = 6.0, 4.1, 4.15
TOP_Z, FLOOR_X0, CROSS_X = 36.0, 117.0, (128.8, 132.3)
Y = dict(key=(-44.0, -40.0), bearing=(40.0, 44.0), roller=(-39.5, 39.5),
         tread_l=(-39.0, -21.5), tread_r=(21.5, 39.0), motor=(FACE_Y - 25.2, FACE_Y))


class Layout:
    def __init__(self, gearset='fast'):
        g = GEARSETS[gearset]; self.name = gearset; self.g = g
        self.M, self.Z_GEAR, self.Z_PIN, self.CD = g['m'], g['zg'], g['zp'], g['cd']
        self.GEAR_OD, self.PIN_OD = self.M * (self.Z_GEAR + 2), self.M * (self.Z_PIN + 2)
        self.A_Z = g['a_z']; self.A_X = PITCH + np.sqrt(self.CD ** 2 - (self.A_Z - ROD_Z) ** 2)
        self.A = np.array([self.A_X, self.A_Z])
        self.T_N20 = np.array([self.A_X, FACE_Y, self.A_Z]) - R_N20 @ np.array([PIN_AXIS_M[0], N20_FACE_YM, PIN_AXIS_M[1]])
        band = (FACE_Y + 1.0, FACE_Y + 1.0 + g['gear_w'])
        self.Y = dict(Y, pinion=band, gear=band)
        self.Y['chamfer'] = (band[1], band[1] + (self.GEAR_OD / 2 - CORE_R))     # 45 deg support under the teeth
        self.FLOOR_TOP = self.A_Z - 6.53 - 0.05
        self.OUT = ROOT / 'cad' / '07-cradle-drive' / ('' if gearset == 'fast' else 'v1-pinion-variant')
        self.OUT.mkdir(parents=True, exist_ok=True)

    def summary(self):
        surf = self.Z_PIN / self.Z_GEAR * np.pi * 2 * TREAD_R
        return dict(gearset=self.name, pitch=PITCH, rod_z=ROD_Z, spool_centre=SPOOL_C.round(3).tolist(),
                    tread_od=round(2 * TREAD_R, 3), roller_gear=f'printed {self.Z_GEAR}T m{self.M}', pinion=self.g['pinion'],
                    centre_distance=self.CD, roller_turns_per_motor_turn=round(self.Z_PIN / self.Z_GEAR, 4),
                    rewind_surface_speed_vs_V10=round(surf / V10_SURFACE_PER_MOTOR_REV, 3),
                    n20_axis=self.A.round(3).tolist(), lateral=self.Y)

    # -------------------------------------------------------------- printed parts
    def roller(self):
        """One piece: bore runs on the rod, end lips touch only the bearing inner race / key face,
        integrated gear with a 45 deg chamfer under the teeth.  Prints upright, +Y end on the bed."""
        ang, gear_ring = monotone_ring(involute_gear(self.M, self.Z_GEAR, backlash=0.12))
        c = lambda r: circle_ring(ang, r)
        rg = np.linalg.norm(gear_ring, axis=1)
        clip = lambda r: gear_ring * (np.minimum(rg, r) / rg)[:, None]
        y0, y1 = self.Y['roller']; gy0, gy1 = self.Y['gear']; ch1 = self.Y['chamfer'][1]
        path = [(y0, c(5.0)), (y0 + 0.6, c(5.0)), (y0 + 0.6, c(CORE_R)), (gy0, c(CORE_R)), (gy0, gear_ring), (gy1, gear_ring)]
        for t in np.linspace(0, 1, 9)[1:]:
            path.append((gy1 + t * (ch1 - gy1), clip(self.GEAR_OD / 2 - t * (self.GEAR_OD / 2 - CORE_R))))
        path += [(y1 - 0.6, c(CORE_R)), (y1 - 0.6, c(5.0)), (y1, c(5.0))]
        return axial_stack(path, c(BORE_R), PITCH, ROD_Z)

    def pinion(self):
        ang, ring = monotone_ring(involute_gear(self.M, self.Z_PIN, backlash=0.12))
        return axial_stack([(self.Y['pinion'][0], ring), (self.Y['pinion'][1], ring)], d_ring(ang, 1.55, 1.05), self.A_X, self.A_Z)

    def treads(self):
        return {k: tube_y(TREAD_R, 5.8, *Y[k], x0=PITCH, z0=ROD_Z, n=160) for k in ('tread_l', 'tread_r')}

    def bracket(self, h=0.2, sdf_only=False):
        """Cradle key (replaces the left bearing in its slot) + bar on the cradle top + cross member
        + open-top motor floor with a rear stop and two zip-tie slots."""
        g = Grid((PITCH - 9, Y['key'][0] - 1.5, 13.0), (CROSS_X[1] + 2, FACE_Y + 1.5, TOP_Z + 1.5), h)
        x0, z0, w = PITCH, ROD_Z, 6.95
        key = union(cyl_y(g, x0, z0, w, *Y['key']), box(g, (x0 - w, Y['key'][0], z0), (x0 + w, Y['key'][1], CRADLE_TOP + 0.6)))
        bar = box(g, (x0 - 7.0, Y['key'][0], CRADLE_TOP + 0.4), (CROSS_X[1], Y['key'][1] - 1.0, TOP_Z))
        fz0 = self.FLOOR_TOP - 2.6
        cross = box(g, (CROSS_X[0], Y['key'][0], fz0), (CROSS_X[1], FACE_Y, TOP_Z))
        floor = box(g, (FLOOR_X0, Y['motor'][0] - 1.65, fz0), (CROSS_X[0] + 0.5, FACE_Y, self.FLOOR_TOP))
        stop = box(g, (FLOOR_X0, Y['motor'][0] - 1.65, fz0), (CROSS_X[0] + 0.5, Y['motor'][0] - 0.2, self.A_Z - 4.0))
        s = union(key, bar, cross, floor, stop)
        holes = [cyl_y(g, x0, z0, BUSH_R, -100, 100)]
        for yc in (-13.0, 0.5):
            holes.append(box(g, (self.A_X + 5.74, yc - 1.6, fz0 - 1), (CROSS_X[0], yc + 1.6, self.FLOOR_TOP + 1)))
        s = subtract(s, *holes)
        return (s, g) if sdf_only else surface_nets(s, g)

    def parts(self):
        p = {'07a-Roller-with-gear': self.roller(), '07d-Motor-bracket-cradle-key': self.bracket()}
        t = self.treads(); p['07b-Tread-sleeve-TPU-L'] = t['tread_l']; p['07b-Tread-sleeve-TPU-R'] = t['tread_r']
        if self.name == 'fast': p['07c-Pinion-17T-N20'] = self.pinion()
        return p

    # -------------------------------------------------------------- reference geometry
    def n20_envelope(self, step=0.25):
        pts = []
        def boxs(lo, hi):
            lo = np.array(lo); hi = np.array(hi)
            for ax in range(3):
                o = [k for k in range(3) if k != ax]
                a = np.arange(lo[o[0]], hi[o[0]] + 1e-9, step); b = np.arange(lo[o[1]], hi[o[1]] + 1e-9, step)
                AA, BB = np.meshgrid(a, b, indexing='ij')
                for v in (lo[ax], hi[ax]):
                    P = np.zeros((AA.size, 3)); P[:, o[0]] = AA.ravel(); P[:, o[1]] = BB.ravel(); P[:, ax] = v; pts.append(P)
        boxs((self.A_X - 5.69, FACE_Y - 9.45, self.A_Z - 6.53), (self.A_X + 5.69, FACE_Y, self.A_Z + 6.53))
        t = np.linspace(0, 2 * np.pi, 160); yy = np.arange(FACE_Y - 25.2, FACE_Y - 9.45, step)
        TT, YY = np.meshgrid(t, yy)
        X = np.clip(self.A_X + 6.0 * np.cos(TT), self.A_X - 5.43, self.A_X + 5.43); Zc = self.A_Z + 6.0 * np.sin(TT)
        pts.append(np.column_stack([X.ravel(), YY.ravel(), Zc.ravel()]))
        return np.concatenate(pts)

    def donor(self):
        cache = Path(__file__).parent / 'donor-verts-v2.pkl'
        if not cache.exists():
            from steplib import load, components, closure, rep_bodies, point, refs
            _, ents = load(STEP01); comps = components(ents); V = {}
            for n in ['N20-0', 'Pinion-0', 'Driven-gear-0', 'Spacer-0', 'Smol_feeder_with_LOAD', 'PREP_position']:
                ids = closure(ents, rep_bodies(ents, comps[n]['rep']))
                V[n] = np.array([point(ents, refs(ents[i])[0]) for i in ids if ents[i].startswith('VERTEX_POINT')])
            pickle.dump(V, open(cache, 'wb'))
        V = pickle.load(open(cache, 'rb'))
        return dict(n20=V['N20-0'] @ R_N20.T + self.T_N20, v1_pinion=V['Pinion-0'] @ R_N20.T + self.T_N20,
                    n20_env=self.n20_envelope())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--gearset', default='fast', choices=GEARSETS); a = ap.parse_args()
    L = Layout(a.gearset); S = L.summary(); print(json.dumps(S, indent=1))
    parts = L.parts()
    for n, (V, T) in parts.items():
        print(n, check_mesh(V, T), V.min(0).round(2), V.max(0).round(2))
        write_stl(L.OUT / f'{n}.stl', V, T)
    pickle.dump(parts, open(Path(__file__).parent / f'parts-{L.name}.pkl', 'wb'))
    json.dump(S, open(L.OUT / 'layout.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
