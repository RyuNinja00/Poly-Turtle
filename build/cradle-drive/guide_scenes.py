"""3D measurement scenes for the finalize guide.  Molded-box features are photo estimates and are
drawn only to show where the tools go; the tool positions match the real measuring surfaces."""
import pickle, numpy as np
from pathlib import Path
from scene3d import *
from cradle_drive import Layout, PITCH, ROD_Z, SPOOL_C, FLANGE_R, ENVELOPE_R, TREAD_R

L = Layout('fast')
RODC, BRG, PLATE, FLOOR, PLAT, TEALC, RIM, LOOP, WALL = '#6B757C', '#C0C6C9', '#CFE2EA', '#DDE3E6', '#E6EBED', '#5FC4BA', '#A9CBDA', '#BFD0DA', '#E9EEF0'
REAR_WALL_X = -62.0          # illustrative only: unknown, this is what measurement 5 finds
PLATE_Y = (40.5, 43.5)       # illustrative cradle plate (thickness unknown -> T)
BRIDGE_Z = 181.0             # top of the lid-ledge bridge used for the 2026-11-24 depth readings (crown 155 at Z 26)

def roller(x, y_half=46, bearings=True, rod_z=ROD_Z):
    out = [('rod', cylinder((x, -y_half, rod_z), (x, y_half, rod_z), 4, 40), RODC)]
    if bearings:
        for s in (-1, 1): out.append(('bearing', cylinder((x, s * 40, rod_z), (x, s * 44, rod_z), 7, 40, r_in=4.05), BRG))
    return out

def plates(x):
    return [('plate', plate_with_slot(x, *PLATE_Y), PLATE), ('plate', plate_with_slot(x, -PLATE_Y[1], -PLATE_Y[0]), PLATE)]

def box_context(rear=True, front=True, rollers=(True, True), walls=True, x_min=None):
    x0 = REAR_WALL_X if x_min is None else x_min
    out = [('floor', cuboid((x0, -51, -3), (PITCH + 46, 51, 0)), FLOOR),
           ('platform', cuboid((22, -45, 0), (85, 45, 10.5)), PLAT)]
    if front:
        out += [('front plug', cuboid((PITCH + 5, -38, 0), (PITCH + 26, 38, 4.8)), TEALC),
                ('rim', cuboid((PITCH + 24, -40, 0), (PITCH + 27, 40, 16.2)), RIM),
                ('end loop', cuboid((PITCH + 28, -18, 0), (PITCH + 31, 18, 52)), LOOP),
                ('end loop top', cuboid((PITCH + 28, -18, 49), (PITCH + 43, 18, 52)), LOOP)]
        out += plates(PITCH)
        if rollers[1]: out += roller(PITCH)
        if walls: out.append(('front wall', cuboid((PITCH + 43, -51, 0), (PITCH + 46, 51, 60)), WALL))
    if rear:
        out += [('rear plug', cuboid((-26, -38, 0), (-5, 38, 4.8)), TEALC)]
        out += plates(0)
        if rollers[0]: out += roller(0)
        if walls: out.append(('rear wall', cuboid((x0 - 3, -51, 0), (x0, 51, 60)), WALL))
    if walls: out.append(('far wall', cuboid((x0, 51, 0), (PITCH + 46, 54, 60)), WALL))
    return out

def place(parts, R=np.eye(3), t=(0, 0, 0)):
    return [(n, xform(vt, R, t), c) for n, vt, c in parts]

FLIP = rot('x', 180)                                     # inside jaws point down
VERT = np.column_stack([(0, 0, -1.0), (0, 1.0, 0), (1.0, 0, 0)])   # beam pointing down (depth-rod use)

# ------------------------------------------------------------------ scenes
def scene_pitch_A():
    return box_context(walls=False) + place(caliper(PITCH + 8), np.eye(3), (-4, 0, 54))

def scene_pitch_B():
    return box_context(walls=False) + place(caliper(PITCH - 8), FLIP, (4, 0, 49))

def scene_slot_S():
    return plates(PITCH)[:1] + [('floor', cuboid((PITCH - 14, 36, -2), (PITCH + 14, 48, 0)), FLOOR)] + \
        place(caliper(14.0), FLIP, (PITCH - 7, 42, 23.5 + 31))

def scene_slot_H():
    return plates(PITCH)[:1] + [('floor', cuboid((PITCH - 14, 36, -2), (PITCH + 14, 48, 0)), FLOOR)] + \
        place(caliper(13.0, depth_rod=13.0), VERT, (PITCH - 8, 42, 28 + 170))

def scene_plates_F():
    sc = [('floor', cuboid((PITCH - 16, -50, -2), (PITCH + 16, 50, 0)), FLOOR)] + plates(PITCH)
    return sc + place(caliper(2 * PLATE_Y[0]), rot('z', 90) @ FLIP, (PITCH, -PLATE_Y[0], 8 + 31))

def scene_bench_E(rod_len=94.0):
    sc = roller(PITCH, y_half=rod_len / 2)
    return sc + place(caliper(88.0), rot('z', 90), (PITCH, -44, ROD_Z + 18))

def scene_bench_L(rod_len=94.0):
    sc = roller(PITCH, y_half=rod_len / 2)
    return sc + place(caliper(rod_len), rot('z', 90), (PITCH, -rod_len / 2, ROD_Z + 13))

def scene_front_P(y=0.0):
    return box_context(rear=False, walls=False, x_min=60) + place(caliper(28.0), FLIP, (PITCH + 4, y, ROD_Z + 31))

def scene_front_bridge(x_rel=16.0):
    """lid-ledge bridge (straightedge) and caliper depth rod down to the surface in front of the rod"""
    br = [('bridge', cuboid((PITCH + x_rel - 6, -60, BRIDGE_Z), (PITCH + x_rel + 6, 60, BRIDGE_Z + 4)), '#8E9AA1')]
    return box_context(rear=False, walls=False, x_min=60) + br + \
        place(caliper(BRIDGE_Z - 16.2, depth_rod=BRIDGE_Z - 16.2), VERT, (PITCH + x_rel - 8, 0, BRIDGE_Z + 170))

def scene_front_parts():
    parts = pickle.load(open(Path(__file__).parent / 'parts-fast.pkl', 'rb'))
    col = {'07a-Roller-with-gear': '#E07A2E', '07b-Tread-sleeve-TPU-L': '#2B2D31', '07b-Tread-sleeve-TPU-R': '#2B2D31',
           '07d-Motor-bracket-cradle-key': '#2F6FA8', '07c-Pinion-17T-N20': '#3F8F6B'}
    sc = box_context(rear=False, walls=False, rollers=(False, False), x_min=60)
    sc += [(n, vt, col[n]) for n, vt in parts.items()]
    sc += [('rod', cylinder((PITCH, -46, ROD_Z), (PITCH, 46, ROD_Z), 4, 40), RODC),
           ('bearing', cylinder((PITCH, 40, ROD_Z), (PITCH, 44, ROD_Z), 7, 40, r_in=4.05), BRG),
           ('N20', cuboid((L.A_X - 5.69, -19.75, L.A_Z - 6.53), (L.A_X + 5.69, 5.45, L.A_Z + 6.53)), '#B9B9B9')]
    return sc

def stock_spool_centre():
    return np.array([PITCH / 2, ROD_Z + np.sqrt(106.5 ** 2 - (PITCH / 2) ** 2)])

def scene_rear_W():
    c = stock_spool_centre()
    sp = [('flange', cylinder((c[0], s * 37, c[1]), (c[0], s * 39, c[1]), FLANGE_R, 96), '#C9A46B') for s in (-1, 1)]
    sp += [('filament', cylinder((c[0], -37, c[1]), (c[0], 37, c[1]), ENVELOPE_R, 96), '#7FA7C9'),
           ('hub', cylinder((c[0], -40, c[1]), (c[0], 40, c[1]), 27.5, 40, r_in=26), '#C9A46B')]
    W = (c[0] - FLANGE_R) - REAR_WALL_X
    ru = place(ruler(60, 13, 0.8), rot('x', 90), (REAR_WALL_X, -40.2, c[1] - 6.5))
    return box_context(front=True, walls=True) + sp + ru, W

if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    tests = [('A', scene_pitch_A(), View(-62, 30)), ('B', scene_pitch_B(), View(-62, 30)), ('S', scene_slot_S(), View(-35, 25)),
             ('H', scene_slot_H(), View(-35, 25)), ('F', scene_plates_F(), View(-25, 28)), ('E', scene_bench_E(), View(-30, 25)),
             ('P', scene_front_P(), View(-60, 28)), ('bridge', scene_front_bridge(), View(-60, 22)), ('parts', scene_front_parts(), View(-55, 30)),
             ('W', scene_rear_W()[0], View(-70, 18))]
    fig, axs = plt.subplots(2, 5, figsize=(25, 10))
    for ax, (n, sc, v) in zip(axs.ravel(), tests):
        draw(ax, v, sc); ax.set_title(n)
    fig.tight_layout(); fig.savefig('/tmp/scenes.png', dpi=70); print('ok')
