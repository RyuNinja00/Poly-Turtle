"""Picture guide for the five measurements that finalize the cradle drive.
Writes docs/measurements/finalize/*.png and docs/PolyDryer-Finalize-Guide.pdf.
Every threshold is computed from the design parameters in cradle_drive.py."""
from pathlib import Path
import sys, textwrap, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent / 'tools'))
from cradle_drive import PITCH, ROD_Z, SPOOL_C, FLANGE_R, TREAD_R, tread_od_for_pitch
from scene3d import View, draw, frame, dim3d, callout, cuboid
import guide_scenes as gs
from guide_scenes import L, BRIDGE_Z

ROOT = Path(__file__).resolve().parents[2]
PH = ROOT / 'docs' / 'measurements' / 'photos'
OUT = ROOT / 'docs' / 'measurements' / 'finalize'; OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob('*.png'): f.unlink()
INK, GREEN, ORANGE, BLUE, GREY, LIGHT, TEAL = '#172F39', '#007968', '#C2461B', '#12658A', '#596E76', '#EAF1F1', '#4FB3A9'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'text.color': INK, 'axes.edgecolor': '#B6C8CA'})

# ------------------------------------------------------------------ thresholds (all derived from the design)
ROD_FRONT = PITCH + 4.0                                         # X of the front rod's front surface
P_MIN = round(L.CROSS_X[1] - ROD_FRONT + 1.0, 1)                # bracket cross member front face + 1 mm
P_DESIGN = 24.0                                                 # photo estimate the layout was drawn around
Z_CLEAR = float(np.floor(min(L.A_Z - L.PIN_OD / 2, L.FLOOR_TOP - 2.6) - 1.0))   # 1 mm under the pinion / motor floor
DEPTH_MIN = BRIDGE_Z - Z_CLEAR
SHIFT = SPOOL_C - gs.stock_spool_centre()                       # cradle-drive spool pose vs stock rollers
W_MIN = round(-SHIFT[0] + 1.0, 1)
STATIONS_X = (8, 16)                                            # bridge stations, mm in front of the rod's front surface
STATIONS_Y = (-35, 0, 10)                                       # key side, centre line, bearing side
SLOT_W = (13.9, 14.4); H_EXP = 28 - (ROD_Z - 7); F_MIN = 2 * 39.5; E_EXP = 88

TERMS = ['Front: the end where the new drive goes (nearest the lid\'s filament outlet). Rear: the other end.',
         'Key side: the front cradle you pick for the bracket\'s key tab. Bearing side: the other front cradle.',
         'Centre line: halfway between the two long side walls.   Z: height above the box floor.',
         'Rod front surface: the side of the front rod that faces the front wall.']

# ------------------------------------------------------------------ page helpers
PAGES = []
def page(title, sub):
    fig = plt.figure(figsize=(11, 8.5)); PAGES.append(fig)
    fig.text(0.04, 0.955, 'POLY-TURTLE  ·  CRADLE DRIVE  ·  FINAL MEASUREMENTS', fontsize=8.5, weight='bold', color=GREEN)
    fig.text(0.04, 0.905, title, fontsize=21, weight='bold'); fig.text(0.04, 0.873, sub, fontsize=10, color=GREY)
    fig.add_artist(plt.Line2D([0.04, 0.96], [0.86, 0.86], color='#B6C8CA', lw=0.8))
    return fig

def photo(fig, rect, name, crop, title=None):
    rect = list(rect); rect[3] = min(rect[3], 0.815 - rect[1])
    ax = fig.add_axes(rect); im = Image.open(PH / name).convert('RGB').crop(crop)
    ax.imshow(im, extent=(crop[0], crop[2], crop[3], crop[1])); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color('#B6C8CA')
    if title: fig.text(rect[0], rect[1] + rect[3] + 0.008, title, fontsize=9, color=GREY)
    return ax

def arrow(ax, p, q, color=ORANGE, lw=2.2, both=True):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='<|-|>' if both else '-|>', mutation_scale=13, color=color, lw=lw, zorder=5))

def tag(ax, xy, s, color=ORANGE, fs=10):
    ax.text(*xy, s, color='white', ha='center', va='center', fontsize=fs, weight='bold', zorder=6,
            bbox=dict(boxstyle='round,pad=0.25', fc=color, ec='none'))

def textbox(fig, rect, blocks, wrap=150):
    ax = fig.add_axes(rect); ax.axis('off'); y = 1.0
    hin = rect[3] * 8.5; lh = 0.2 / hin; hh = 0.27 / hin
    for head, lines, color in blocks:
        ax.text(0, y, head, fontsize=10.5, weight='bold', color=color, va='top', transform=ax.transAxes); y -= hh
        for s in lines:
            s = textwrap.fill(s, wrap, subsequent_indent='    ')
            ax.text(0.015, y, s, fontsize=9.2, va='top', transform=ax.transAxes); y -= lh * (1 + s.count('\n'))
        y -= lh * 0.45
    return ax

def schem(fig, rect, xlim, ylim, title):
    rect = list(rect); rect[3] = min(rect[3], 0.80 - rect[1])
    ax = fig.add_axes(rect); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, color=GREY, loc='left'); ax.tick_params(labelsize=7, colors=GREY); ax.grid(alpha=0.2)
    return ax

def r3d(fig, rect, scene, view, lo, hi, title):
    rect = list(rect); rect[3] = min(rect[3], 0.815 - rect[1])            # keep clear of the header rule
    ax = fig.add_axes(rect); draw(ax, view, scene); frame(ax, view, lo, hi)
    fig.text(rect[0], rect[1] + rect[3] + 0.008, title, fontsize=9, color=GREY); return ax

def box_edges(ax, view, lo, hi, color=ORANGE):
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    C = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    for i in range(8):
        for j in range(i + 1, 8):
            if np.sum(C[i] != C[j]) == 1:
                P = view.p(C[[i, j]]); ax.plot(P[:, 0], P[:, 1], '--', color=color, lw=1.3, zorder=9)

def note3d(fig):
    fig.text(0.04, 0.012, 'Molded-box shapes in the 3D pictures are drawn from your photos (±2–3 mm) only to show where the tools go. '
             'Tool positions match the real measuring surfaces.', fontsize=7.5, color=GREY)

# ================================================================ 0 overview
fig = page('Five measurements to finalize the cradle drive',
           'Everything else is already designed. These numbers confirm the fit and set the one dimension that changes: the tread diameter.')
v = View(-58, 32)
ax = r3d(fig, [0.03, 0.30, 0.56, 0.54], [it for it in gs.box_context(walls=True) if it[0] != 'front wall'], v, (-66, -51, 0), (PITCH + 46, 54, 40),
         'The box interior, near side wall and front end wall cut away (rear on the left, front on the right)')
for n, p, off in [('1', (PITCH / 2, 0, 30), (0, 28)), ('2', (PITCH, -42, 28), (-30, -32)), ('3', (PITCH, 20, 26), (6, 34)),
                  ('4', (PITCH + 16, 0, 12), (40, 22)), ('5', (gs.REAR_WALL_X, 0, 45), (25, -20))]:
    P = v.p1(p); ax.annotate(n, P, (P[0] + off[0], P[1] + off[1]), fontsize=12, weight='bold', color='white', ha='center', va='center', zorder=12,
                             bbox=dict(boxstyle='circle,pad=0.3', fc=ORANGE, ec='white'), arrowprops=dict(arrowstyle='-', color=ORANGE, lw=1.4))
ax.text(*v.p1((PITCH + 30, -51, 0)), 'FRONT', color=GREEN, weight='bold', fontsize=10, ha='center', va='top')
ax.text(*v.p1((-40, -51, 0)), 'REAR', color=GREEN, weight='bold', fontsize=10, ha='center', va='top')
textbox(fig, [0.61, 0.30, 0.36, 0.54], [
    ('The five measurements', ['1  Roller pitch: sets the tread diameter', '2  Front cradle slots and bearing spacing', '3  Factory front rod',
                               '4  Clear space in front of the front rod', '5  Rear-wall gap at spool-centre height'], INK),
    ('Tools', ['Digital calipers with a depth rod', 'Steel ruler, 150 mm or longer', 'The rigid bridge you used on the lid ledges', 'Flashlight and phone camera',
               'Your largest spool (measurement 5)'], INK),
    ('Before you start', ['Box out of the dock, lid off, spool out (it goes back in for 5).', 'Vent plugs installed, both factory rollers seated.',
                          'Take every reading twice and photograph it.'], INK)], wrap=60)
textbox(fig, [0.04, 0.04, 0.92, 0.23], [
    ('Words used in this guide', TERMS, GREEN),
    ('How the numbers are used', [f'Pitch → PITCH in build/cradle-drive/cradle_drive.py → tread OD (106 → {tread_od_for_pitch(106):.2f}, 107 → {tread_od_for_pitch(107):.2f}, '
                                  f'108 → {tread_od_for_pitch(108):.2f}, 109 → {tread_od_for_pitch(109):.2f}). Everything else is a pass/fail check; each page gives its limit. '
                                  'Fill in the record sheet on the last page and send it back with the photos.'], GREEN)])
note3d(fig)

# ================================================================ 1 pitch
fig = page('1  Roller pitch — where the jaws go', 'Two caliper readings across the two factory rollers. Their average is the centre-to-centre pitch.')
v = View(-62, 30); lo, hi = (-12, -50, 0), (PITCH + 12, 50, 100)
ax = r3d(fig, [0.03, 0.30, 0.46, 0.55], gs.scene_pitch_A(), v, lo, hi, 'A — outside jaws over the outer edges of both rods')
dim3d(ax, v, (-4, 0, 30), (ROD_FRONT, 0, 30), 'A', ORANGE, off=(0, 6))
callout(ax, v, (-4, 0, 14), 'jaw touches the rear face\nof the rear rod', ORANGE, (-25, -35))
callout(ax, v, (ROD_FRONT, 0, 14), 'jaw touches the front face\nof the front rod', ORANGE, (10, -40))
ax = r3d(fig, [0.51, 0.30, 0.46, 0.55], gs.scene_pitch_B(), v, lo, hi, 'B — caliper upside down, inside jaws between the rods')
dim3d(ax, v, (4, 0, 30), (PITCH - 4, 0, 30), 'B', BLUE, off=(0, 6))
callout(ax, v, (4, 0, 20), 'inside jaw on the\nfront face of the rear rod', BLUE, (-15, -40))
callout(ax, v, (PITCH - 4, 0, 20), 'inside jaw on the\nrear face of the front rod', BLUE, (20, -40))
textbox(fig, [0.04, 0.05, 0.92, 0.22], [
    ('Why two readings', ['A = pitch + rod diameter and B = pitch − rod diameter, so (A + B) / 2 is the pitch exactly, whatever the rod diameter.'], INK),
    ('Where', ['Hold the beam level and square to the rods. Take A and B at three stations: the middle, and about 10 mm in from each end of the rods. '
               'The next page shows them on your photo.'], INK)])
note3d(fig)

fig = page('1  Roller pitch — steps', 'Centre-to-centre distance of the two factory rollers. This is the only number that changes a part (the tread OD).')
crop = (470, 380, 1080, 790)
ax = photo(fig, [0.03, 0.36, 0.5, 0.45], '1000017854.jpg', crop, 'Your overhead photo. Move the ruler out of the way before measuring.')
arrow(ax, (556, 540), (964, 540)); tag(ax, (760, 525), 'A  outside span')
arrow(ax, (591, 470), (929, 470), color=BLUE); tag(ax, (760, 455), 'B  inside span', BLUE)
for y, s in ((450, '1'), (560, '2'), (735, '3')):
    ax.plot([574, 946], [y, y], ':', color='white', lw=1); tag(ax, (1035, y), f'station {s}', GREY, 8)
tag(ax, (520, 400), 'rear rod', GREY); tag(ax, (990, 400), 'front rod', GREY)
ax2 = schem(fig, [0.56, 0.42, 0.4, 0.4], (-15, 125), (-55, 55), 'Schematic, top view')
for x in (0, PITCH): ax2.add_patch(Rectangle((x - 4, -46), 8, 92, fc='#7C868C'))
arrow(ax2, (-4, 10), (PITCH + 4, 10)); ax2.text(53.5, 15, 'A', color=ORANGE, weight='bold', ha='center')
arrow(ax2, (4, -10), (PITCH - 4, -10), color=BLUE); ax2.text(53.5, -20, 'B', color=BLUE, weight='bold', ha='center')
arrow(ax2, (0, 35), (PITCH, 35), color=GREEN, lw=1.4); ax2.text(53.5, 40, 'pitch = (A + B) / 2', color=GREEN, ha='center', weight='bold')
for y in (-36, 0, 36): ax2.plot([-12, 122], [y, y], ':', color=GREY, lw=0.6)
ax2.text(53.5, -50, 'three stations: both ends and the middle (dotted)', fontsize=7, ha='center', color=GREY)
textbox(fig, [0.04, 0.04, 0.92, 0.29], [
    ('Steps', ['1. Seat both factory rollers fully in their cradles. Remove the ruler.',
               '2. A: outside jaws across the outer edges of both rods. B: caliper upside down, inside jaws between the inner edges of the rods.',
               '3. Take A and B at all three stations and write them down.',
               '4. Pitch = (A + B) / 2 at each station.'], INK),
    ('What works', [f'106 – 109 is expected. Anything from 104 to 110 passes every check once PITCH is set. Below 105 the TPU tread wall gets thin '
                    f'({(tread_od_for_pitch(104) - 11.6) / 2:.1f} mm at 104).',
                    'If the three stations differ by more than 0.5 mm, the rods aren\'t parallel. Send all three readings.'], GREEN)])

# ================================================================ 2 cradle slots
fig = page('2  Front cradle slots — where the tools go', 'The key tab drops into one slot in place of a bearing, so the slot\'s size and position matter.')
vb = View(-30, 22)
ax = r3d(fig, [0.03, 0.47, 0.30, 0.38], gs.scene_bench_E(), vb, (PITCH - 20, -50, 0), (PITCH + 20, 50, 70), 'E — on the bench: bearing outer faces')
dim3d(ax, vb, (PITCH, -44, ROD_Z - 12), (PITCH, 44, ROD_Z - 12), 'E', ORANGE)
vs = View(-72, 16)
ax = r3d(fig, [0.35, 0.47, 0.30, 0.38], gs.scene_slot_S(), vs, (PITCH - 14, 36, 4), (PITCH + 14, 48, 44), 'S — inside jaws across the slot, just below the top')
dim3d(ax, vs, (PITCH - 7, 42, 27), (PITCH + 7, 42, 27), 'S', ORANGE, off=(0, -5))
ax = r3d(fig, [0.67, 0.47, 0.30, 0.38], gs.scene_slot_H(), vs, (PITCH - 14, 36, 4), (PITCH + 14, 48, 44), 'H — beam end across the slot, depth rod to the bottom')
dim3d(ax, vs, (PITCH + 9, 42, 28), (PITCH + 9, 42, 15), 'H', BLUE)
vf = View(-20, 30)
ax = r3d(fig, [0.03, 0.08, 0.30, 0.36], gs.scene_plates_F(), vf, (PITCH - 16, -50, 0), (PITCH + 16, 50, 45), 'F — roller out, inside jaws between the plates')
dim3d(ax, vf, (PITCH, -gs.PLATE_Y[0], 8), (PITCH, gs.PLATE_Y[0], 8), 'F', BLUE)
vt = View(-18, 24)
ax = r3d(fig, [0.35, 0.08, 0.30, 0.36], gs.plates(PITCH)[:1] + [('floor', cuboid((PITCH - 14, 36, -2), (PITCH + 14, 48, 0)), gs.FLOOR)],
         vt, (PITCH - 14, 36, 0), (PITCH + 14, 48, 30), 'T — plate thickness beside the slot')
callout(ax, vt, (PITCH + 7.5, (gs.PLATE_Y[0] + gs.PLATE_Y[1]) / 2, 28), 'T: thickness of this wall\n(caliper outside jaws)', GREEN, (14, 9))
textbox(fig, [0.68, 0.08, 0.29, 0.36], [
    ('Order', ['With the roller seated: nothing to read.', 'Lift the front roller out, then measure E on the bench.',
               'S, H, T, F in the empty box.', 'Do S, H, T on the key-side slot; F spans both.'], INK)], wrap=48)
note3d(fig)

fig = page('2  Front cradle slots — steps', 'The key tab replaces the bearing in the key-side slot. The other bearing stays in the bearing-side slot.')
crop = (150, 600, 760, 1180)
ax = photo(fig, [0.03, 0.36, 0.40, 0.45], '1000017860.webp', crop, 'Your photo: front roller lifted, bearing at its slot')
ax.add_patch(Circle((296, 966), 62, fill=False, ec=ORANGE, lw=2, ls='--'))
tag(ax, (296, 1080), 'bearing seat = slot', ORANGE); tag(ax, (520, 700), 'lift the roller straight up', GREY)
arrow(ax, (470, 760), (330, 900), color=GREY, lw=1.5, both=False)
ax2 = schem(fig, [0.46, 0.42, 0.25, 0.39], (94, 120), (-2, 34), 'Cradle plate, face view')
ax2.add_patch(Polygon([(98, 0), (115, 0), (115, 28), (114, 28), (114, 22), *[(107 + 7 * np.cos(t), 22 + 7 * np.sin(t)) for t in np.linspace(0, -np.pi, 30)],
                       (100, 22), (100, 28), (98, 28)], fc=LIGHT, ec=GREY))
ax2.add_patch(Circle((107, 22), 4, fc='#8A949A')); ax2.text(107, 22, 'rod', ha='center', va='center', fontsize=6, color='white')
arrow(ax2, (100, 30.5), (114, 30.5)); ax2.text(107, 31.6, 'S', color=ORANGE, weight='bold', ha='center')
arrow(ax2, (117, 28), (117, 15), color=BLUE); ax2.text(118, 21.5, 'H', color=BLUE, weight='bold')
arrow(ax2, (96.5, 0), (96.5, 8), color=BLUE, lw=1.2); ax2.text(96, 4, 'F\nhere', fontsize=6.5, ha='right', color=BLUE)
ax2.text(96, 28.4, 'top\nZ 28', fontsize=6.5, ha='right', color=GREY)
ax3 = schem(fig, [0.73, 0.42, 0.24, 0.39], (86, 124), (-52, 52), 'Front cradles, top view')
for sgn in (-1, 1): ax3.add_patch(Rectangle((98, gs.PLATE_Y[0] if sgn > 0 else -gs.PLATE_Y[1]), 17, gs.PLATE_Y[1] - gs.PLATE_Y[0], fc=LIGHT, ec=GREY))
ax3.add_patch(Rectangle((103, -44), 8, 88, fc='#8A949A', alpha=0.35))
for sgn in (-1, 1): ax3.add_patch(Rectangle((100, sgn * 42 - 2), 14, 4, fc='#C0C6C9', ec=GREY, alpha=0.6))
arrow(ax3, (119, -44), (119, 44)); ax3.text(120, 0, 'E', color=ORANGE, weight='bold')
arrow(ax3, (95, -gs.PLATE_Y[0]), (95, gs.PLATE_Y[0]), color=BLUE); ax3.text(93.5, 0, 'F', color=BLUE, weight='bold', ha='right')
arrow(ax3, (90, gs.PLATE_Y[0]), (90, gs.PLATE_Y[1]), color=GREEN, lw=1.2); ax3.text(89, 47, 'T', color=GREEN, weight='bold', fontsize=8, ha='right')
ax3.text(105, -50, 'key side', fontsize=7, color=GREY, ha='center'); ax3.text(105, 49, 'bearing side', fontsize=7, color=GREY, ha='center')
textbox(fig, [0.04, 0.03, 0.92, 0.31], [
    ('Steps', ['1. Lift the front roller straight out. E: on the bench, outside jaws across the outer faces of its two bearings.',
               '2. S: caliper upside down, inside jaws across the key-side slot just below the plate top.  H: rest the end of the beam across the slot top and lower the depth rod to the slot bottom.',
               '3. T: plate thickness beside the slot.  F: inside jaws between the inboard faces of the two front plates, below the slots (about 5–10 mm above the floor).',
               '4. Photograph the key-side slot straight on. Do its walls run straight up from the curve, or do they flare or have a lip?'], INK),
    ('What works', [f'S {SLOT_W[0]} – {SLOT_W[1]} (the key tab is {SLOT_W[0]} wide).   H ≈ {H_EXP:.0f} (the key tab sits like a bearing, 7 below the rod centre).',
                    f'F ≥ {F_MIN:.0f} (treads end 39 from the centre line).   E ≈ {E_EXP}: (E − 4) / 2 is each slot\'s distance from the centre line; 40 – 44 is an easy adjustment.   T: record it.'], GREEN)])

# ================================================================ 3 rod
fig = page('3  Factory front rod', 'The printed roller runs on this rod. Only the key-side bearing has to come off.')
vb = View(-30, 22)
ax = r3d(fig, [0.03, 0.40, 0.45, 0.44], gs.scene_bench_L(), vb, (PITCH - 20, -52, 0), (PITCH + 20, 52, 60), 'L — on the bench: outside jaws over the rod ends')
dim3d(ax, vb, (PITCH, -47, ROD_Z - 9), (PITCH, 47, ROD_Z - 9), 'L', ORANGE)
callout(ax, vb, (PITCH, -42, ROD_Z + 7), 'key-side bearing:\ntry to slide it off', ORANGE, (45, -45))
crop = (150, 560, 720, 1060)
ax = photo(fig, [0.52, 0.40, 0.45, 0.44], '1000017860.webp', crop, 'Your photo: factory front roller lifted')
arrow(ax, (296, 966), (483, 686)); tag(ax, (330, 790), 'L  overall length')
tag(ax, (560, 640), 'bearing-side bearing stays', GREY); tag(ax, (250, 1035), 'key-side bearing comes off', ORANGE)
textbox(fig, [0.04, 0.05, 0.92, 0.3], [
    ('Steps', ['1. L: overall rod length, end to end.  d: rod diameter in three places.',
               '2. Bearings: outer diameter, width, and the distance from each bearing\'s outer face to its rod end.',
               '3. Try to slide the key-side bearing off by hand with a light twist. Don\'t force or hammer it. Note one of: slides off / snug / pressed or glued / retaining ring.'], INK),
    ('What works', ['d = 8.0 (the roller bore is 8.2 and runs on the rod).  L ≥ E from measurement 2; about 88 – 95 is expected.',
                    'If the bearing won\'t come off, use a V1.0 MR148 on a new Ø8 rod cut to length L. Everything else stays the same.'], GREEN)])
note3d(fig)

# ================================================================ 4 clear space
fig = page('4  Clear space in front of the front rod', 'The motor, pinion and bracket sit in this space. P is the room in front of the rod; nothing may rise into the dashed box.')
v = View(-58, 30); lo, hi = (PITCH - 14, -50, 0), (PITCH + 32, 50, 55)
ax = r3d(fig, [0.03, 0.40, 0.46, 0.45], gs.scene_front_parts(), v, lo, hi, 'What will sit here (printed parts and the N20)')
box_edges(ax, v, (ROD_FRONT, -44, Z_CLEAR), (L.CROSS_X[1], 12, 37))
callout(ax, v, (L.CROSS_X[1], -44, Z_CLEAR), f'must be empty:\nZ {Z_CLEAR:.0f} – 37, from the rod\nto {L.CROSS_X[1] - ROD_FRONT:.1f} in front of it', ORANGE, (55, 75))
ax = r3d(fig, [0.51, 0.40, 0.46, 0.45], gs.scene_front_P(), v, lo, hi, 'P — caliper upside down, inside jaws from rod to loop')
dim3d(ax, v, (ROD_FRONT, 0, 30), (ROD_FRONT + P_DESIGN, 0, 30), 'P', BLUE, off=(0, 5))
callout(ax, v, (ROD_FRONT, 0, ROD_Z), 'jaw on the rod\nfront surface', BLUE, (-30, -35))
callout(ax, v, (ROD_FRONT + P_DESIGN, 0, ROD_Z + 2), 'jaw on the first surface\n(here the end-wall loop)', BLUE, (30, -30))
textbox(fig, [0.04, 0.05, 0.92, 0.3], [
    ('P: room in front of the rod', ['Front roller seated. Caliper upside down, beam above the rod, inside jaws pointing down. One jaw on the rod front surface, the other on the first surface it reaches toward '
                                      'the front: the clear loop, or the front end wall where there is no loop. Hold it at about rod height. Read P at three spots across: key side (35 from the centre line), centre line, and 10 toward the bearing side.'], INK),
    ('What works', [f'P ≥ {P_MIN} everywhere (the bracket\'s cross member ends {L.CROSS_X[1] - ROD_FRONT:.1f} in front of the rod surface, plus 1 mm). '
                    f'The layout was drawn for P ≈ {P_DESIGN:.0f}. If P is smaller, the cross member can move or get thinner, so send the number.',
                    f'The second check, on the next page, makes sure nothing in that space rises above Z {Z_CLEAR:.0f}.'], GREEN)])
note3d(fig)

fig = page('4  Clear space — height check with the bridge', f'Same bridge on the lid ledges as your earlier depth readings (crown read 155 there, so the bridge top is at Z {BRIDGE_Z:.0f}).')
v = View(-58, 22)
ax = r3d(fig, [0.03, 0.36, 0.42, 0.5], gs.scene_front_bridge(STATIONS_X[1] + 4), v, (PITCH - 14, -60, 0), (PITCH + 32, 60, BRIDGE_Z + 30),
         'Depth rod from the bridge top down to the highest surface')
dim3d(ax, v, (PITCH + STATIONS_X[1] + 4 + 9, 0, BRIDGE_Z), (PITCH + STATIONS_X[1] + 4 + 9, 0, 16.2), 'depth', BLUE, off=(14, 0))
ax2 = schem(fig, [0.48, 0.48, 0.49, 0.37], (PITCH - 40, PITCH + 34), (-52, 52), 'Where to probe (top view): 6 readings')
ax2.set_yticklabels([])
ax2.add_patch(Rectangle((PITCH - 4, -46), 8, 92, fc='#8A949A')); ax2.text(PITCH, 47.5, 'front rod', fontsize=7, ha='center')
ax2.add_patch(Rectangle((PITCH + 28, -18), 3, 36, fc='#BFD0DA')); ax2.text(PITCH + 29.5, 20, 'loop\n(est.)', fontsize=7, ha='center', color=GREY)
ax2.add_patch(Rectangle((ROD_FRONT, -44), L.CROSS_X[1] - ROD_FRONT, 56, fc='none', ec=ORANGE, ls='--', lw=1.3))
for sx in STATIONS_X:
    for sy in STATIONS_Y:
        ax2.add_patch(Circle((ROD_FRONT + sx, sy), 1.4, fc=BLUE, zorder=5))
for sx in STATIONS_X: ax2.text(ROD_FRONT + sx, -42, f'{sx}', color=BLUE, fontsize=8, ha='center', weight='bold')
ax2.text(ROD_FRONT + 12, -49, 'mm in front of the rod front surface', color=BLUE, fontsize=7, ha='center')
for sy, nme in zip(STATIONS_Y, ('key side', 'centre line', 'bearing side')): ax2.text(PITCH - 6, sy, nme, fontsize=7, ha='right', va='center', color=GREY)
textbox(fig, [0.04, 0.05, 0.92, 0.27], [
    ('Steps', [f'1. Lay the bridge across the lid ledges, square to the long walls, above each probe station (blue dots: {STATIONS_X[0]} and {STATIONS_X[1]} mm in front of the rod front surface; '
               'key side, centre line, bearing side).',
               '2. Lower the depth rod straight down to the first surface it meets and record the depth. That is 6 readings.'], INK),
    ('What works', [f'Every depth ≥ {DEPTH_MIN:.0f}, meaning the surface is at or below Z {Z_CLEAR:.0f} (surface Z = {BRIDGE_Z:.0f} − depth). Your earlier readings of 176 at the '
                    'outer tracks (Z 5) already pass. A plug-rim crest at Z 16.2 reads about 165, which also passes.'], GREEN)])
note3d(fig)

# ================================================================ 5 rear wall
fig = page('5  Rear-wall gap at spool-centre height', f'The cradle drive sits the spool {-SHIFT[0]:.1f} mm further back and {SHIFT[1]:.1f} mm higher than the stock rollers do.')
scene, W_illus = gs.scene_rear_W(); v = View(-88, 14)
ax = r3d(fig, [0.03, 0.36, 0.45, 0.5], scene, v, (gs.REAR_WALL_X - 5, -51, 0), (PITCH + 46, 51, 225), 'Spool on the stock rollers, side view (near wall removed)')
c = gs.stock_spool_centre()
dim3d(ax, v, (gs.REAR_WALL_X, -41, c[1] + 12), (c[0] - FLANGE_R, -41, c[1] + 12), 'W', BLUE, off=(0, 9))
callout(ax, v, (gs.REAR_WALL_X, -41, c[1] - 6), 'ruler end against the rear wall\n(the wall is seen edge-on here)', BLUE, (20, -70))
callout(ax, v, (c[0], -41, c[1]), 'hub centre height', ORANGE, (40, 30))
ax2 = schem(fig, [0.52, 0.40, 0.45, 0.45], (-75, 160), (-5, 225), 'Stock pose (dashed) vs. cradle-drive pose')
ax2.add_patch(Circle(c, FLANGE_R, fill=False, ec=GREY, ls='--')); ax2.add_patch(Circle(SPOOL_C, FLANGE_R, fill=False, ec='#8C6B3F', lw=1.5))
for x in (0, PITCH): ax2.add_patch(Circle((x, ROD_Z), 4, fc='#5B6770'))
ax2.plot([gs.REAR_WALL_X] * 2, [0, 220], color=INK, lw=2, ls='--'); ax2.text(gs.REAR_WALL_X - 2, 40, 'rear wall (position unknown)', ha='right', va='bottom', fontsize=7.5, rotation=90)
arrow(ax2, (gs.REAR_WALL_X, c[1]), (c[0] - FLANGE_R, c[1]), color=BLUE); ax2.text(gs.REAR_WALL_X + 4, c[1] + 8, 'W', color=BLUE, weight='bold', fontsize=12)
ax2.text(SPOOL_C[0], SPOOL_C[1] + 12, f'cradle-drive pose:\n{-SHIFT[0]:.1f} back, {SHIFT[1]:.1f} up', ha='center', fontsize=7.5, color='#8C6B3F')
textbox(fig, [0.04, 0.05, 0.92, 0.28], [
    ('Steps', ['1. Put your largest spool on the stock rollers. Record its flange outer diameter and overall width.',
               '2. Hold the steel ruler level on its edge at the height of the spool\'s hub centre, with its end against the rear wall inside the box. Read W where the flange rim crosses the ruler. '
               'You can also use the caliper depth rod from the flange rim to the wall.',
               '3. Also measure the gap from the top of the flange to the underside of the closed lid.'], INK),
    ('What works', [f'W ≥ {W_MIN} (the gap with the cradle drive is W − {-SHIFT[0]:.1f}, and it must stay at least 1 mm).',
                    f'If W < {W_MIN}, send the number. The fixes are a smaller tread with the spool slightly lower (the lid has about 1.4 mm to give) or a lower spool-size limit.'], GREEN)])
note3d(fig)

# ================================================================ 6 record sheet
fig = page('Record sheet', 'Write each reading twice. Send this page with one photo per measurement.')
ax = fig.add_axes([0.04, 0.05, 0.92, 0.80]); ax.axis('off')
rows = [('1', 'A outside span, stations 1 / 2 / 3', '', '', ''), ('1', 'B inside span, stations 1 / 2 / 3', '', '', ''),
        ('1', 'Pitch = (A + B) / 2', '', '', '104 – 110 (106 – 109 expected)'),
        ('2', 'E bearing outer faces (on the bench)', '', '', f'≈ {E_EXP}'), ('2', 'S key-side slot width', '', '', f'{SLOT_W[0]} – {SLOT_W[1]}'),
        ('2', 'H slot top → slot bottom', '', '', f'≈ {H_EXP:.0f}'), ('2', 'T plate thickness', '', '', 'record'),
        ('2', 'F inboard plate faces, below the slots', '', '', f'≥ {F_MIN:.0f}'), ('2', 'Slot walls straight? (yes/no, photo)', '', '', ''),
        ('3', 'L rod length  /  d rod diameter', '', '', 'L ≥ E  /  d = 8.0'), ('3', 'Key-side bearing: slides / snug / pressed / ring', '', '', ''),
        ('4', 'P rod front → first surface: key / centre / bearing side', '', '', f'all ≥ {P_MIN}'),
        ('4', f'Bridge depth at {STATIONS_X[0]} mm: key / centre / bearing side', '', '', f'all ≥ {DEPTH_MIN:.0f}'),
        ('4', f'Bridge depth at {STATIONS_X[1]} mm: key / centre / bearing side', '', '', f'all ≥ {DEPTH_MIN:.0f}'),
        ('5', 'Spool flange OD  /  overall width', '', '', ''), ('5', 'W flange rim → rear wall at hub height', '', '', f'≥ {W_MIN}'),
        ('5', 'Flange top → closed lid', '', '', '')]
cols = [0.0, 0.04, 0.47, 0.61, 0.75]; heads = ['#', 'Measurement', 'Reading 1', 'Reading 2', 'Works if']
for x, h in zip(cols, heads): ax.text(x, 1.0, h, weight='bold', color=GREEN, fontsize=10, transform=ax.transAxes, va='top')
y = 0.955; rh = 0.051
for r in rows:
    ax.add_patch(Rectangle((0, y - rh), 1, rh, transform=ax.transAxes, fc=LIGHT if int(r[0]) % 2 else 'white', ec='#D5E0E1', lw=0.6))
    for x, s in zip(cols, r): ax.text(x + 0.005, y - rh / 2, s, fontsize=9, va='center', transform=ax.transAxes)
    y -= rh
ax.text(0, y - 0.035, 'Pitch sets the tread OD; everything else is pass/fail. Out-of-range numbers are fixable in the scripts. Send them and the CAD gets regenerated.',
        fontsize=9, color=GREY, transform=ax.transAxes)

# ------------------------------------------------------------------ write
names = ['p00-overview', 'p01-pitch-3d', 'p02-pitch-steps', 'p03-slots-3d', 'p04-slots-steps', 'p05-front-rod', 'p06-clear-space-3d',
         'p07-clear-space-bridge', 'p08-rear-wall-gap', 'p09-record-sheet']
n = len(PAGES)
with PdfPages(ROOT / 'docs' / 'PolyDryer-Finalize-Guide.pdf') as pdf:
    for i, (f, nm) in enumerate(zip(PAGES, names)):
        f.text(0.96, 0.955, f'{i + 1} / {n}', fontsize=9, weight='bold', color=GREY, ha='right')
        f.savefig(OUT / f'{nm}.png', dpi=130); pdf.savefig(f); plt.close(f)
print('ok', n, 'pages; P_MIN', P_MIN, 'Z_CLEAR', Z_CLEAR, 'DEPTH_MIN', DEPTH_MIN, 'W_MIN', W_MIN, 'H', H_EXP)
