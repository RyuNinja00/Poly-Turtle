"""Lid-to-box N20 disconnect: Yiwei 4-pin magnetic pogo pair (male MG0P25AM 4P, female MG0P25AF 4P), model frame.

Male (recessed spring pins, carries power) hangs face-down in a holder built into the lid at the +X end.
It is glued into a printed puck that floats in the holder: down onto a lip plate flush with the rim plane
(gravity + magnets), up 2 mm to the holder roof, and sideways +-1.0 / +-0.5 mm. The lip plate screws on
from below (2 x M2), so the puck goes in and out from the rim side. The female (flat pads, motor side) is
glued into a fixed block stuck to the box's +X inner wall with VHB. Closing the lid, the magnets and the
female's pad island pull the male onto the female; the float takes up lid height and position error.

Long axis along Y. Pins 1+2 -> N20 lead a, 3+4 -> lead b.
"""
import numpy as np
import extras as E

RIM = 60.21                      # lid rim plane (bed when printing the lid rim down)
XC, YC = 92.0, 23.0              # connector centre: +X end, +Y side (clear of the inlet guide, the payout path and the spool)

# connector (4P, 2.54 pitch): flange A x 7.5 x 1.0, body B x 5.5, 1.2 face part above the flange, 2.8 behind it
CON = dict(A=24.08, Wf=7.5, B=22.08, Wb=5.5, face=1.2, flange=1.0, rear=2.8, tail=1.75, n=4, pitch=2.54)
FIT = 0.15
FLOAT = dict(x=1.0, y=0.5, up=2.0)   # puck float: sideways across / along the connector, and up
LIP = 1.0                            # lip plate thickness; it sits flush in a recess at the rim plane
WALL = 1.6
PUCK = dict(t=1.2, overlap=0.6, sleeve_wall=1.2)
SCREW = dict(pilot_r=0.8, clear_r=1.15, head_d=3.5, head_h=1.0)   # 2 x M2 x 5 button head (ISO 7380), from below
ROOF = dict(t=1.6, slot=(12.5, 3.0))
SKIRT_X = 101.6                      # holder merges into jojo's inner skirt (100.7-103.0)

def stadium(cx, cy, L, W, n=16):
    """oblong along Y: length L, width W"""
    return E.rounded_rect(cx, cy, W, L, W / 2 - 1e-6, n)

g = CON['face'] + CON['flange']                                         # face -> flange top
fx, fy = FLOAT['x'] + FIT, FLOAT['y'] + FIT
open_L, open_W = CON['A'] + 2 * fy, CON['Wf'] + 2 * fx
puck_L, puck_W = open_L + 2 * (fy + PUCK['overlap']), open_W + 2 * (fx + PUCK['overlap'])
cav_L, cav_W = puck_L + 2 * fy, puck_W + 2 * fx
sl_in_L, sl_in_W = CON['B'] + 2 * FIT, CON['Wb'] + 2 * FIT
sl_out_L, sl_out_W = sl_in_L + 2 * PUCK['sleeve_wall'], sl_in_W + 2 * PUCK['sleeve_wall']
SCREW_DY = cav_L / 2 + 1.9
out_L, out_W = 2 * (SCREW_DY + SCREW['clear_r'] + 0.6 + 0.8 + FIT), cav_W + 2 * WALL   # plate keeps 0.6 round the screw holes
rec_L, rec_W = out_L - 1.6, out_W - 1.6                                # lip-plate recess, 0.8 ring round it

F_LOW = RIM + LIP - g                    # male face with the puck on the lip (lid off): 1.2 below the rim plane
Z_CAP = F_LOW + g + CON['rear'] + FLOAT['up']      # holder roof underside: puck sleeve top + float
F_BOX = F_LOW + FLOAT['up'] / 2          # female face: mid float -> lid may sit 1 mm higher or lower
BLOCK = dict(x0=XC - CON['Wf'] / 2 - 1.5, wall_x=103.4, y=(YC - CON['A'] / 2 - 1.5, YC + CON['A'] / 2 + 1.5),
             z0=52.5, recess=0.8)
BLOCK['top'] = F_BOX - g + BLOCK['recess']
SCREWS = [(XC, YC - SCREW_DY), (XC, YC + SCREW_DY)]

def _outer():
    x0 = XC - out_W / 2
    return E.rounded_rect((x0 + SKIRT_X) / 2, YC, SKIRT_X - x0, out_L, 6.0)        # r 6: 1.7 mm past the Smol on drop-in

def lid_holder():
    """built into the lid; prints rim down from the bed: ring round the lip-plate recess, walls, roof with a wire slot"""
    o = _outer(); rec = E.rounded_rect(XC, YC, rec_W, rec_L, 5.2)
    cav = E.rounded_rect(XC, YC, cav_W, cav_L, cav_W / 2 - 1e-6, 16)
    pil = [E.circle(x, y, SCREW['pilot_r'], 16) for x, y in SCREWS]
    return E.merge(E.prism(o, [rec], RIM, RIM + LIP), E.prism(o, [cav] + pil, RIM + LIP, Z_CAP),
                   E.prism(o, [stadium(XC, YC, *ROOF['slot'])], Z_CAP, Z_CAP + ROOF['t']))

def lip_plate(placed=False):
    """flush in the recess; the puck rests on it. Print flat."""
    o = E.rounded_rect(XC, YC, rec_W - 2 * FIT, rec_L - 2 * FIT, 5.05)
    holes = [stadium(XC, YC, open_L, open_W)] + [E.circle(x, y, SCREW['clear_r'], 24) for x, y in SCREWS]
    V, T = E.prism(o, holes, 0.0, LIP)
    return (V + [0, 0, RIM], T) if placed else (V - [XC, YC, 0], T)

def puck(at=None):
    """print flange down; at = male face z to place it in the model frame"""
    p = [E.prism(stadium(0, 0, puck_L, puck_W), [stadium(0, 0, sl_in_L, sl_in_W)], 0.0, PUCK['t']),
         E.prism(stadium(0, 0, sl_out_L, sl_out_W), [stadium(0, 0, sl_in_L, sl_in_W)], PUCK['t'], CON['rear'])]
    V, T = E.merge(*p)
    if at is not None: V = V + [XC, YC, at + g]
    return V, T

def box_block(placed=True):
    b = BLOCK; x0, x1 = b['x0'], b['wall_x']; y0, y1 = b['y']
    o = E.rounded_rect((x0 + x1) / 2, YC, x1 - x0, y1 - y0, 1.5)
    zt = b['top']; zr = zt - b['recess']
    p = [E.prism(o, [stadium(XC, YC, sl_in_L, sl_in_W)], b['z0'], zr),
         E.prism(o, [stadium(XC, YC, CON['A'] + 2 * FIT, CON['Wf'] + 2 * FIT)], zr, zt)]
    V, T = E.merge(*p)
    if not placed: V = (V - [XC, YC, zt]) * [1, 1, -1]; T = T[:, ::-1]    # print top face down
    return V, T

def screw_heads(dz=0.0):
    return E.merge(*[E.prism(E.circle(x, y, SCREW['head_d'] / 2, 24), [], RIM - SCREW['head_h'] + dz, RIM + dz) for x, y in SCREWS])

def envelopes():
    """connector bodies + tails + 4 mm of soldered wire, male at both float ends, female in place"""
    def body(face, sgn):          # sgn +1: body extends up from the face (male), -1: down (female)
        segs = [(0, CON['face'], CON['B'], CON['Wb']), (CON['face'], g, CON['A'], CON['Wf']),
                (g, g + CON['rear'], CON['B'], CON['Wb']), (g + CON['rear'], g + CON['rear'] + CON['tail'] + 4.0, 9.0, 2.5)]
        out = []
        for a, b, L, W in segs:
            z0, z1 = sorted((face + sgn * a, face + sgn * b))
            out.append(E.prism(stadium(XC, YC, L, W), [], z0, z1))
        return E.merge(*out)
    return dict(male_low=body(F_LOW, 1), male_high=body(F_LOW + FLOAT['up'], 1), female=body(F_BOX, -1))

def report():
    return dict(connector='Yiwei MG0P25AM (male) / MG0P25AF (female), 4 pin', centre_xy=[XC, YC],
                male_face_z=dict(lid_off=round(F_LOW, 2), float_top=round(F_LOW + FLOAT['up'], 2)),
                female_face_z=round(F_BOX, 2), lid_height_tolerance_mm=FLOAT['up'] / 2, side_float_mm=[FLOAT['x'], FLOAT['y']],
                lip_opening=[round(open_L, 2), round(open_W, 2)], puck=[round(puck_L, 2), round(puck_W, 2)],
                cavity=[round(cav_L, 2), round(cav_W, 2)], holder_roof_z=round(Z_CAP, 2), lip_plate_screws='2 x M2 x 5 button head, from below',
                box_block=dict(x=[round(BLOCK['x0'], 2), BLOCK['wall_x']], y=[round(v, 2) for v in BLOCK['y']],
                               z=[BLOCK['z0'], round(BLOCK['top'], 2)]))
