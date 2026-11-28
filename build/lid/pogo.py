"""Lid-to-box N20 disconnect, rev 2 (print-in-place, no tape, no screws, no glue). Model frame, mm.

Connector: Yiwei 4-pin magnetic pogo pair, MG0P25AM (male, recessed spring pins) / MG0P25AF (female pads).

Lid side: the male clicks up into a pocket built into the lid (prints with it, rim down). Two flexing beams
on the bed layer catch the long edges of its flange. It is fixed; its face sits 0.2 mm below the rim plane.

Box side: one print-in-place part. A frame with a captive floating carrier: its flange sits on a flat floor
(slides +-1 mm sideways) under a lip (2 mm up), 0.35 mm gaps as printed, and a cross bar that spans the box's +X end just under the rim. The female clicks down into
the carrier (two bridge beams over its flange). TPU ring bumpers on the bar ends grip the side walls, so no
tape and no drilling. The lid places the bar: hang it on the male, close the lid, done.

Pins 1+2 -> N20 lead a, 3+4 -> lead b.
"""
import numpy as np
import extras as E

RIM = 60.21                      # lid rim plane (bed when printing the lid rim down)
XC, YC = 93.2, 23.0              # connector centre: +X end, +Y side
CON = dict(A=24.08, Wf=7.5, B=22.08, Wb=5.5, face=1.2, flange=1.0, rear=2.8, tail=1.75, pitch=2.54)
FIT, GAP = 0.15, 0.35            # connector fit; print-in-place gap
H = 0.1                          # SDF grid for the small parts

# ---------------------------------------------------------------- lid pocket (z relative to RIM)
LP = dict(out_x0=-7.2, out_hy=14.2, cav_hx=4.9, cav_hy=12.6, beam=(3.0, 3.8), beam_z=1.0, chamfer=0.6,
          ceil=2.4, rear_top=5.2, roof=6.8, slot=(12.5, 3.0))
F_MALE = RIM + LP['beam_z'] - CON['face']          # male face: flange resting on the beams -> 0.2 below the rim plane
SKIRT_X = 101.6

# ---------------------------------------------------------------- box part
F_FEM = F_MALE                                      # mated
CAR = dict(bx=4.8, by=13.6, h=5.2, flange=(1.5, 2.7), flange_out=2.6, post_y=12.2, beam=(3.0, 3.8), beam_h=0.75)
FLOAT = dict(side=1.0, up=2.0)
FR = dict(floor=1.0, wall=1.0, lip_t=0.8, chamfer_x=4.5, chamfer_y=3.0)
FR['open'] = FLOAT['side'] + 0.1                    # floor opening and lip opening: body + 1.1
FR['inner'] = CAR['flange_out'] + FLOAT['side'] + 0.1
CAR_TOP_REST = F_FEM - CON['face'] - CON['flange']  # female flange bottom = carrier top, carrier sitting on the floor (as installed)
Z_BED = CAR_TOP_REST + (CAR['flange'][0] - FR['floor']) - CAR['h']      # printed 0.5 above the floor (flat 2.6 mm overhang won't droop onto it)
FR['lip_z'] = FR['floor'] + (CAR['flange'][1] - CAR['flange'][0]) + FLOAT['up']   # lip underside, from the bed
FR['top'] = Z_BED + FR['lip_z'] + FR['lip_t']
BAR = dict(x=(98.6, 102.7), end=42.0, top_dz=3.55)      # bar kept low and off the inlet guide's collar
BUMP = dict(od=9.0, wall=1.6, sock=2.5, sock_wall=0.8)

# ---------------------------------------------------------------- SDF helpers
def rrect(X, Y, cx, cy, hx, hy, r):
    qx = np.abs(X - cx) - (hx - r); qy = np.abs(Y - cy) - (hy - r)
    return (np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r).astype(np.float32)
def stadium(X, Y, cx, cy, hl, hw): return rrect(X, Y, cx, cy, hw, hl, hw - 1e-4)
def slab(Z, z0, z1): return np.maximum(z0 - Z, Z - z1).astype(np.float32)
def box3(X, Y, Z, x0, x1, y0, y1, z0, z1):
    return np.maximum.reduce(np.broadcast_arrays(x0 - X, X - x1, y0 - Y, Y - y1, z0 - Z, Z - z1)).astype(np.float32)
def U(*a): return np.minimum.reduce(np.broadcast_arrays(*a))
def I(*a): return np.maximum.reduce(np.broadcast_arrays(*a))
def D(a, *b): return np.maximum(a, -U(*b))

def _mesh(f, g):
    import printed_lid as P
    V, T = P.mc(f, g)
    return P.decimate(V, T, passes=30)
def _grid(lo, hi):
    import printed_lid as P
    g = P.Grid(lo, hi, H); return g, g.X(), g.Y(), g.Z()

# ---------------------------------------------------------------- parts
def lid_pocket():
    """built into the lid; prints from the bed (rim plane) up"""
    g, X, Y, Z = _grid((XC + LP['out_x0'] - 0.4, YC - LP['out_hy'] - 0.4, RIM - 0.3), (SKIRT_X + 0.3, YC + LP['out_hy'] + 0.4, RIM + LP['roof'] + 0.3))
    x, y, z = X - XC, Y - YC, Z - RIM
    x0, x1 = LP['out_x0'], SKIRT_X - XC
    outer = I(rrect(x, y, (x0 + x1) / 2, 0, (x1 - x0) / 2, LP['out_hy'], 2.0), slab(z, 0, LP['roof']))
    cav = I(rrect(x, y, 0, 0, LP['cav_hx'], LP['cav_hy'], 1.0), slab(z, -1, LP['ceil']))
    rear = I(stadium(x, y, 0, 0, CON['B'] / 2 + FIT, CON['Wb'] / 2 + FIT), slab(z, LP['ceil'] - 0.01, LP['rear_top']))
    slot = I(stadium(x, y, 0, 0, LP['slot'][0] / 2, LP['slot'][1] / 2), slab(z, LP['rear_top'] - 0.01, LP['roof'] + 1))
    b0, b1 = LP['beam']
    ax = np.abs(x)
    beam = I(np.maximum(b0 - ax, ax - b1), np.abs(y) - (LP['cav_hy'] + 0.4), slab(z, 0, LP['beam_z']),
             ((b0 + LP['chamfer'] - z) - ax) / np.sqrt(2))                      # 45 deg lead-in on the bottom inner edge
    f = U(D(outer, cav, rear, slot), beam)
    return _mesh(f, g)

def _d_body(x, y): return rrect(x, y, 0, 0, CAR['bx'], CAR['by'], 1.5)

def carrier(z_bot=None):
    """stem through the frame floor, flat flange over it (0.35 gap as printed), posts + bridge beams that clip the female"""
    z_bot = Z_BED if z_bot is None else z_bot
    top = z_bot + CAR['h']
    m = CAR['flange_out'] + 0.4
    g, X, Y, Z = _grid((XC - CAR['bx'] - m, YC - CAR['by'] - m, z_bot - 0.3), (XC + CAR['bx'] + m, YC + CAR['by'] + m, top + 2.2))
    x, y, z = X - XC, Y - YC, Z - z_bot
    db = _d_body(x, y)
    body = I(db, slab(z, 0, CAR['h']))
    flange = I(db - CAR['flange_out'], slab(z, *CAR['flange']))
    posts = I(db, CAR['post_y'] - np.abs(y), slab(z, 0, CAR['h'] + 1.05 + CAR['beam_h']))           # within the body outline
    b0, b1 = CAR['beam']; ax = np.abs(x); zb = CAR['h'] + 1.05
    beam = I(np.maximum(b0 - ax, ax - b1), np.abs(y) - (CAR['post_y'] + 0.4), slab(z, zb, zb + CAR['beam_h']),
             (z - (zb + 0.2 + (ax - b0) * 0.55 / 0.8)) / 1.2)                  # sloped top: lead-in for the flange
    pocket = I(stadium(x, y, 0, 0, CON['B'] / 2 + FIT, CON['Wb'] / 2 + FIT), slab(z, -1, CAR['h'] + 3))
    f = D(U(body, flange, posts, beam), pocket)
    return _mesh(f, g)

def frame():
    """floor ring under the carrier flange, wall, lip over it; cross bar to both side walls"""
    zb = Z_BED; top = FR['top']
    hx, hy = CAR['bx'] + FR['inner'] + FR['wall'], CAR['by'] + FR['inner'] + FR['wall']
    yb0, yb1 = YC - hy, YC + hy
    g, X, Y, Z = _grid((XC - hx - 0.4, -BAR['end'] - 0.4, zb - 0.3), (BAR['x'][1] + 0.4, BAR['end'] + 0.4, top + 0.3))
    x, y, z = X - XC, Y - YC, Z - zb
    db = _d_body(x, y)
    outer = I(rrect(x, y, 0, 0, hx, hy, 2.0), slab(z, 0, top - zb))
    hole_floor = I(db - FR['open'], slab(z, -1, FR['floor']))
    cavity = I(db - FR['inner'], slab(z, FR['floor'] - 0.01, FR['lip_z']))
    hole_lip = I(db - FR['open'], slab(z, FR['lip_z'] - 0.01, top - zb + 1))
    bt = zb + BAR['top_dz']
    bar = U(box3(X, Y, Z, *BAR['x'], -BAR['end'], yb0 + 1.0, zb, bt), box3(X, Y, Z, *BAR['x'], yb1 - 1.0, BAR['end'], zb, bt))
    f = D(U(outer, bar), hole_floor, cavity, hole_lip)
    # spool side (-X) and filament side (-Y end) lower edges chamfered 45 deg
    xa = XC - hx
    f = np.maximum(f, ((FR['chamfer_x'] - (X - xa) - z) / np.sqrt(2)).astype(np.float32))
    wedge = np.maximum(((Y - yb0) + z - FR['chamfer_y']) / np.sqrt(2), X - 97.5)
    f = np.maximum(f, -wedge.astype(np.float32))
    return _mesh(f, g)

def bumper():
    """TPU ring bumper; slides on a bar end. Local: bar end at y = 0, bar along -y. Print upright."""
    h = BAR['top_dz']; bw = BAR['x'][1] - BAR['x'][0]
    import printed_lid as P
    lo, hi = (-BUMP['od'] / 2 - 0.4, -BUMP['sock'] - 0.4, -0.3), (BUMP['od'] / 2 + 0.4, BUMP['sock_wall'] + BUMP['od'] + 0.4, h + 0.3)
    g = P.Grid(lo, hi, H); X, Y, Z = g.X(), g.Y(), g.Z()
    sock_hx = bw / 2 + 0.05 + BUMP['sock_wall']
    sock = D(box3(X, Y, Z, -sock_hx, sock_hx, -BUMP['sock'], BUMP['sock_wall'], 0, h),
             box3(X, Y, Z, -bw / 2 - 0.05, bw / 2 + 0.05, -BUMP['sock'] - 1, 0, -1, h + 1))
    cy = BUMP['sock_wall'] + BUMP['od'] / 2 - 0.01
    r = np.hypot(X, Y - cy)
    ring = I(np.maximum(r - BUMP['od'] / 2, BUMP['od'] / 2 - BUMP['wall'] - r), slab(Z, 0, h))
    return _mesh(U(sock, ring), g)

def bumper_placed(side):
    V, T = bumper(); s = 1 if side > 0 else -1
    V = V * [1, s, 1] + [(BAR['x'][0] + BAR['x'][1]) / 2, s * BAR['end'], Z_BED]
    return V, (T if s > 0 else T[:, ::-1])

def envelopes():
    """connector bodies (+ tails and 4 mm of soldered wire), as mated"""
    def body(face, sgn):
        g_ = CON['face'] + CON['flange']
        segs = [(0, CON['face'], CON['B'], CON['Wb']), (CON['face'], g_, CON['A'], CON['Wf']),
                (g_, g_ + CON['rear'], CON['B'], CON['Wb']), (g_ + CON['rear'], g_ + CON['rear'] + CON['tail'] + 4.0, 9.0, 2.5)]
        parts = []
        for a, b, L, W in segs:
            z0, z1 = sorted((face + sgn * a, face + sgn * b))
            parts.append(E.prism(E.rounded_rect(XC, YC, W, L, W / 2 - 1e-6, 16), [], z0, z1))
        return E.merge(*parts)
    return dict(male=body(F_MALE, 1), female=body(F_FEM, -1))

def report():
    return dict(connector='Yiwei MG0P25AM (male, lid) / MG0P25AF (female, box), 4 pin', centre_xy=[XC, YC],
                faces_z=round(F_MALE, 2), carrier_float_mm=dict(up=FLOAT['up'], side=FLOAT['side']),
                box_part_z=[round(Z_BED, 2), round(FR['top'], 2)], bar_x=list(BAR['x']), bar_ends_y=BAR['end'],
                bumper=dict(od=BUMP['od'], free_reach_y=round(BAR['end'] + BUMP['sock_wall'] + BUMP['od'], 1)))
