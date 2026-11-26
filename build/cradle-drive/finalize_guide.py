"""Picture guide for the five measurements that finalize the cradle drive.
Writes docs/measurements/finalize/*.png and docs/PolyDryer-Finalize-Guide.pdf."""
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon, Wedge, FancyBboxPatch
from PIL import Image
import textwrap
from cradle_drive import Layout, PITCH, ROD_Z, SPOOL_C, FLANGE_R, TREAD_R, CROSS_X, tread_od_for_pitch

ROOT = Path(__file__).resolve().parents[2]
PH = ROOT / 'docs' / 'measurements' / 'photos'
OUT = ROOT / 'docs' / 'measurements' / 'finalize'; OUT.mkdir(parents=True, exist_ok=True)
L = Layout('fast')
INK, GREEN, ORANGE, BLUE, GREY, LIGHT, TEAL = '#172F39', '#007968', '#C2461B', '#12658A', '#596E76', '#EAF1F1', '#4FB3A9'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'text.color': INK, 'axes.edgecolor': '#B6C8CA'})

def page(num, title, sub):
    fig = plt.figure(figsize=(11, 8.5))
    fig.text(0.04, 0.955, 'POLY-TURTLE  ·  CRADLE DRIVE  ·  FINAL MEASUREMENTS', fontsize=8.5, weight='bold', color=GREEN)
    fig.text(0.96, 0.955, num, fontsize=9, weight='bold', color=GREY, ha='right')
    fig.text(0.04, 0.905, title, fontsize=21, weight='bold')
    fig.text(0.04, 0.873, sub, fontsize=10, color=GREY)
    fig.add_artist(plt.Line2D([0.04, 0.96], [0.86, 0.86], color='#B6C8CA', lw=0.8))
    return fig

def photo(fig, rect, name, crop, title=None):
    ax = fig.add_axes(rect); im = Image.open(PH / name).convert('RGB').crop(crop)
    ax.imshow(im, extent=(crop[0], crop[2], crop[3], crop[1])); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color('#B6C8CA')
    if title: ax.set_title(title, fontsize=9, color=GREY, loc='left')
    return ax

def arrow(ax, p, q, color=ORANGE, lw=2.2, both=True, z=5):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='<|-|>' if both else '-|>', mutation_scale=13, color=color, lw=lw, zorder=z))

def tag(ax, xy, s, color=ORANGE, ha='center', va='center', fs=10, box=True):
    ax.text(*xy, s, color='white' if box else color, ha=ha, va=va, fontsize=fs, weight='bold', zorder=6,
            bbox=dict(boxstyle='round,pad=0.25', fc=color, ec='none') if box else None)

def textbox(fig, rect, blocks):
    ax = fig.add_axes(rect); ax.axis('off'); y = 1.0
    hin = rect[3] * 8.5; lh = 0.215 / hin; hh = 0.27 / hin          # line heights in axes fraction
    for head, lines, color in blocks:
        ax.text(0, y, head, fontsize=10.5, weight='bold', color=color, va='top', transform=ax.transAxes); y -= hh
        for s in lines:
            s = textwrap.fill(s, 168, subsequent_indent='    ')
            ax.text(0.015, y, s, fontsize=9.2, va='top', transform=ax.transAxes); y -= lh * (1 + s.count('\n'))
        y -= lh * 0.5
    return ax

def schem(fig, rect, xlim, ylim, title):
    ax = fig.add_axes(rect); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, color=GREY, loc='left'); ax.tick_params(labelsize=7, colors=GREY); ax.grid(alpha=0.2)
    return ax

def save(fig, name, pdf):
    fig.savefig(OUT / f'{name}.png', dpi=130); pdf.savefig(fig); plt.close(fig)

pdf = PdfPages(ROOT / 'docs' / 'PolyDryer-Finalize-Guide.pdf')

# ================================================================ 0 overview
fig = page('0 / 6', 'Five measurements to finalize the cradle drive',
           'Everything else is already designed. These numbers confirm the fit and set the one dimension that changes: the tread diameter.')
ax = schem(fig, [0.04, 0.33, 0.55, 0.5], (-25, 160), (-60, 60), 'Box floor, top view (mm).  FRONT = the end where the new drive goes (nearest the lid outlet).')
ax.add_patch(Rectangle((-4, -47), 8, 94, fc='#5B6770')); ax.add_patch(Rectangle((PITCH - 4, -47), 8, 94, fc='#8A949A'))
for yy in (-42, 42):
    for xx in (0, PITCH): ax.add_patch(Rectangle((xx - 7, yy - 2), 14, 4, fc='#C0C6C9', ec=GREY, lw=0.6))
for yy in (-45.5, 39.5): ax.add_patch(Rectangle((98, yy), 17, 6, fc=LIGHT, ec=GREY, ls=':'))
ax.add_patch(Rectangle((112, -40), 23, 80, fc='#CFE9E6', ec=TEAL, ls=':')); ax.text(123, 0, 'front plug\n+ rim', ha='center', fontsize=7, color=TEAL)
ax.add_patch(Rectangle((135, -20), 15, 40, fc='#EEF1F2', ec=GREY, ls=':')); ax.text(142.5, 0, 'end\nloop', ha='center', fontsize=7, color=GREY)
ax.plot([-20, -20], [-55, 55], color=INK, lw=2); ax.text(-22, 50, 'rear\nwall', ha='right', fontsize=7)
ax.text(0, 52, 'rear roller', ha='center', fontsize=7.5); ax.text(PITCH, 52, 'front roller', ha='center', fontsize=7.5)
for n, xy in [('1', (53, 0)), ('2', (PITCH, -42)), ('3', (PITCH, 20)), ('4', (128, 30)), ('5', (-12, -25))]:
    ax.add_patch(Circle(xy, 6, fc=ORANGE, ec='white', lw=1.5, zorder=8)); ax.text(*xy, n, color='white', weight='bold', ha='center', va='center', zorder=9)
arrow(ax, (4, 0), (PITCH - 4, 0), color=ORANGE, lw=1.4)
textbox(fig, [0.62, 0.33, 0.35, 0.5], [
    ('The five measurements', ['1  Roller pitch (sets the tread diameter)', '2  Front cradle slots: width, depth, spacing', '3  Factory front rod: length, does the bearing come off',
                               '4  Front-end features: plug-rim crest and end loop', '5  Rear-wall gap at spool-centre height'], INK),
    ('Tools', ['Digital calipers with a depth rod', '150 mm or longer steel ruler', 'Flashlight; phone for a photo of each reading', 'For 5: your largest spool'], INK),
    ('Before you start', ['Box out of the dock, lid off, spool out.', 'Leave the vent plugs installed.', 'Seat both factory rollers fully.', 'Take every reading twice; record both.'], INK)])
textbox(fig, [0.04, 0.05, 0.92, 0.24], [
    ('How the numbers are used', ['Pitch → PITCH in build/cradle-drive/cradle_drive.py → tread OD (106 → 16.91, 107 → 17.96, 108 → 19.02, 109 → 20.09).',
                                  'Slots, rod and front-end features are pass/fail checks. Each page gives the range that works with the printed parts as they are now.',
                                  'Rear-wall gap decides whether a Ø205 spool fits with the drive sitting 5.1 mm further back than stock.',
                                  'Fill in the record sheet on page 6 and send it back with the photos.'], GREEN)])
save(fig, 'p0-overview', pdf)

# ================================================================ 1 pitch
fig = page('1 / 6', '1  Roller pitch', 'Centre-to-centre distance of the two factory rollers. This is the only number that changes a part (the tread OD).')
crop = (470, 380, 1080, 790)
ax = photo(fig, [0.03, 0.36, 0.5, 0.45], '1000017854.jpg', crop, 'Your overhead photo. Move the ruler out of the way before measuring.')
arrow(ax, (556, 540), (964, 540)); tag(ax, (760, 525), 'A  outside span')
arrow(ax, (591, 470), (929, 470), color=BLUE); tag(ax, (760, 455), 'B  inside span', BLUE)
for y in (450, 560, 735): ax.plot([574, 946], [y, y], ':', color='white', lw=0.8)
tag(ax, (520, 430), 'rear rod', GREY); tag(ax, (1010, 430), 'front rod', GREY)
ax2 = schem(fig, [0.56, 0.42, 0.4, 0.4], (-15, 125), (-55, 55), 'Schematic (top view)')
for x in (0, PITCH): ax2.add_patch(Rectangle((x - 4, -46), 8, 92, fc='#7C868C'))
arrow(ax2, (-4, 10), (PITCH + 4, 10)); ax2.text(53.5, 15, 'A', color=ORANGE, weight='bold', ha='center')
arrow(ax2, (4, -10), (PITCH - 4, -10), color=BLUE); ax2.text(53.5, -20, 'B', color=BLUE, weight='bold', ha='center')
arrow(ax2, (0, 35), (PITCH, 35), color=GREEN, lw=1.4); ax2.text(53.5, 40, 'pitch = (A + B) / 2', color=GREEN, ha='center', weight='bold')
for y in (-40, 0, 40): ax2.plot([-12, 122], [y, y], ':', color=GREY, lw=0.6)
ax2.text(53.5, -48, 'measure at 3 stations: both ends + middle (dotted lines)', fontsize=7, ha='center', color=GREY)
textbox(fig, [0.04, 0.04, 0.92, 0.29], [
    ('Steps', ['1. Seat both rollers fully in their cradles. Remove the ruler.',
               '2. A: outside caliper jaws across the outer edges of both rods. B: inside jaws between the inner edges of the rods.',
               '3. Take A and B in the middle and about 10 mm in from each end (3 stations). The spread shows whether the rods are parallel.',
               '4. Pitch = (A + B) / 2. Rod diameter cancels out, so you don\'t need to know it.'], INK),
    ('Expected and what it changes', ['Expect 106 – 109 (photo estimate 106.3 – 107). Anything 104 – 110 works; only the tread OD changes.',
                                       'If the 3 stations differ by more than 0.5 mm, record all three. The rods are not parallel and the tread should match the narrower end.'], GREEN)])
save(fig, 'p1-roller-pitch', pdf)

# ================================================================ 2 cradle slots
fig = page('2 / 6', '2  Front cradle slots', 'The bracket\'s key tab replaces one bearing in its slot (the key side); the other bearing stays in its slot.')
crop = (150, 600, 760, 1180)
ax = photo(fig, [0.03, 0.36, 0.40, 0.45], '1000017860.webp', crop, 'Your photo: front roller lifted, bearing at its slot')
ax.add_patch(Circle((296, 966), 62, fill=False, ec=ORANGE, lw=2, ls='--'))
tag(ax, (296, 1080), 'bearing seat = slot', ORANGE); tag(ax, (520, 700), 'lift the roller straight up', GREY)
arrow(ax, (470, 760), (330, 900), color=GREY, lw=1.5, both=False)
ax2 = schem(fig, [0.45, 0.45, 0.25, 0.36], (94, 120), (-2, 34), 'Cradle plate, face view (X–Z)')
ax2.add_patch(Polygon([(98, 0), (115, 0), (115, 28), (114, 28), (114, 22), *[(107 + 7 * np.cos(t), 22 + 7 * np.sin(t)) for t in np.linspace(0, -np.pi, 30)], (100, 22), (100, 28), (98, 28)], fc=LIGHT, ec=GREY))
ax2.add_patch(Circle((107, 22), 7, fill=False, ec='#999', ls=':')); ax2.add_patch(Circle((107, 22), 4, fc='#8A949A'))
arrow(ax2, (100, 30.5), (114, 30.5)); ax2.text(107, 31.6, 'S', color=ORANGE, weight='bold', ha='center')
arrow(ax2, (117, 28), (117, 15), color=BLUE); ax2.text(118, 21.5, 'H', color=BLUE, weight='bold')
ax2.text(96, 28.4, 'top\nZ 28', fontsize=6.5, ha='right', color=GREY)
ax3 = schem(fig, [0.72, 0.45, 0.25, 0.36], (88, 124), (-52, 52), 'Front roller, top view')
for sgn in (-1, 1):
    ax3.add_patch(Rectangle((98, 39.5 if sgn > 0 else -45.5), 17, 6, fc=LIGHT, ec=GREY, ls=':'))
ax3.add_patch(Rectangle((103, -44), 8, 88, fc='#8A949A'))
for sgn in (-1, 1): ax3.add_patch(Rectangle((100, sgn * 42 - 2), 14, 4, fc='#C0C6C9', ec=GREY))
ax3.text(106.5, 47, 'cradle plate', fontsize=6.5, ha='center', color=GREY)
arrow(ax3, (118, -44), (118, 44)); ax3.text(119, 0, 'E', color=ORANGE, weight='bold')
arrow(ax3, (97, -39.5), (97, 39.5), color=BLUE); ax3.text(95.5, 0, 'F', color=BLUE, weight='bold', ha='right')
arrow(ax3, (94, 39.5), (94, 45.5), color=GREEN, lw=1.2); ax3.text(93, 42.5, 'T', color=GREEN, weight='bold', fontsize=8, ha='right')
textbox(fig, [0.04, 0.03, 0.92, 0.31], [
    ('Steps', ['1. Roller seated. E: outside jaws across the outer faces of both front bearings.',
               '2. Lift the front roller out. S: inside jaws across the slot, just below the cradle top.  H: depth rod from the cradle top down to the bottom of the slot.',
               '3. T: thickness of the cradle plate beside the slot.  F: inside jaws between the inboard faces of the left and right cradle plates, at about rod height.',
               '4. Photograph one slot straight on. Do its walls run straight up from the curve, or do they flare or have a lip?'], INK),
    ('What works with the parts as printed', ['S 13.9 – 14.4 (key tab is 13.9 wide)    H ≈ 13 (key tab bottom sits 7 below the rod centre, like the bearing)',
                                               'F ≥ 79 (treads end at ±39)    (E − 4) / 2 ≈ 42 = slot centre distance from the middle (any value 40 – 44 is easy to adjust)    T: just record it'], GREEN)])
save(fig, 'p2-cradle-slots', pdf)

# ================================================================ 3 rod
fig = page('3 / 6', '3  Factory front rod', 'The roller runs on this rod. Only the bearing on the key side (your choice of end) has to come off.')
crop = (150, 560, 720, 1060)
ax = photo(fig, [0.03, 0.36, 0.42, 0.45], '1000017860.webp', crop, 'Your photo: factory front roller lifted')
arrow(ax, (296, 966), (483, 686)); tag(ax, (330, 790), 'L  overall length')
tag(ax, (560, 640), 'other bearing stays', GREY); tag(ax, (250, 1035), 'key-side bearing comes off', ORANGE)
ax2 = schem(fig, [0.49, 0.5, 0.47, 0.32], (-52, 52), (-14, 16), 'Rod with its two bearings (side view)')
ax2.add_patch(Rectangle((-46, -4), 92, 8, fc='#8A949A'))
for s in (-1, 1): ax2.add_patch(Rectangle((s * 42 - 2, -7), 4, 14, fc='#C0C6C9', ec=GREY))
arrow(ax2, (-46, 11), (46, 11)); ax2.text(0, 12.5, 'L', color=ORANGE, weight='bold', ha='center')
arrow(ax2, (-44, -11), (44, -11), color=BLUE); ax2.text(0, -13.8, 'E (page 2)', color=BLUE, ha='center', fontsize=8)
arrow(ax2, (-30, -4), (-30, 4), color=GREEN, lw=1.2); ax2.text(-28, 0, 'd', color=GREEN, weight='bold')
textbox(fig, [0.04, 0.04, 0.92, 0.3], [
    ('Steps', ['1. L: overall rod length, end to end.  d: rod diameter in 3 places.',
               '2. Bearings: OD, width, and how far each one sits from its rod end.',
               '3. Try to slide one bearing off by hand with a light twist. Don\'t force it or hammer it. Note one of: slides off / snug / pressed or glued / retaining ring.'], INK),
    ('What works', ['d = 8.0 (roller bore is 8.2; it runs on the rod).  L must be at least E (page 2); about 88 is expected.',
                    'If the bearing won\'t come off: use a V1.0 MR148 on a new Ø8 rod cut to L. Everything else stays the same.'], GREEN)])
save(fig, 'p3-front-rod', pdf)

# ================================================================ 4 front end
fig = page('4 / 6', '4  Front-end features', 'Confirms the motor bracket and pinion clear the plug rim and the end-wall loop. Measure on the centre line.')
crop = (1050, 560, 1450, 960)
ax = photo(fig, [0.03, 0.36, 0.40, 0.45], '1000017858.jpg', crop, 'Your side photo, front end (bearing = front roller)')
ax.add_patch(Circle((1133, 822), 45, fill=False, ec=GREY, lw=1.5, ls='--'))
arrow(ax, (1159, 845), (1262, 845)); tag(ax, (1210, 880), 'C', ORANGE)
arrow(ax, (1159, 760), (1362, 760), color=BLUE); tag(ax, (1260, 735), 'P', BLUE)
tag(ax, (1290, 900), 'plug-rim crest (est.)', TEAL); tag(ax, (1395, 640), 'end loop\n(est.)', GREY)
ax2 = schem(fig, [0.46, 0.40, 0.51, 0.42], (95, 152), (-2, 42), 'What has to clear (side view, centre line)')
ax2.add_patch(Rectangle((95, -2), 57, 2, fc='#DDE3E6'))
ax2.add_patch(Rectangle((124, 4.8), 11, 11.4, fc='#CFE9E6', ec=TEAL, ls=':')); ax2.text(129.5, 9, 'crest\n(est.)', ha='center', fontsize=7, color=TEAL)
ax2.add_patch(Rectangle((135, 0), 17, 42, fc='#EEF1F2', ec=GREY, ls=':')); ax2.text(143.5, 20, 'end loop\n(est.)', ha='center', fontsize=7, color=GREY)
ax2.add_patch(Circle((PITCH, ROD_Z), 4, fc='#8A949A')); ax2.add_patch(Circle((PITCH, ROD_Z), TREAD_R, fill=False, ec='#2B2D31'))
ax2.add_patch(Circle(L.A, L.PIN_OD / 2, fc='#3F8F6B', alpha=0.5)); ax2.add_patch(Rectangle((L.A_X - 5.69, L.A_Z - 6.53), 11.38, 13.06, fc='#B9B9B9', alpha=0.8))
ax2.add_patch(Rectangle((CROSS_X[0], L.FLOOR_TOP - 2.6), CROSS_X[1] - CROSS_X[0], 36 - L.FLOOR_TOP + 2.6, fc='#2F6FA8', alpha=0.6))
ax2.text(L.A_X, L.A_Z, 'N20', ha='center', va='center', fontsize=7); ax2.text(CROSS_X[1] + 0.5, 37, 'bracket', fontsize=7, color='#2F6FA8')
ax2.text(L.A_X, L.A_Z - L.PIN_OD / 2 - 2.3, f'pinion low point Z {L.A_Z - L.PIN_OD / 2:.1f}', ha='center', fontsize=7, color='#3F8F6B')
arrow(ax2, (PITCH + 4, 13), (130, 13)); ax2.text(118, 14, 'C → crest top', color=ORANGE, fontsize=8)
arrow(ax2, (PITCH + 4, 39), (135, 39), color=BLUE); ax2.text(118, 40, 'P → loop face', color=BLUE, fontsize=8)
textbox(fig, [0.04, 0.03, 0.92, 0.31], [
    ('Steps (front roller seated, on the box centre line)', ['1. C: from the front surface of the front rod forward to the highest point of the clear rim around the vent plug. Also note the height of that point (measured before as 16.2).',
               '2. P: from the front surface of the front rod forward to the nearest face of the clear loop/bracket at the front end wall, at about cradle-top height (Z 20 – 36).',
               '3. Note how wide the loop is side to side, and photograph the front end from the side and from above.'], INK),
    ('What works', [f'P ≥ 24 (loop at X ≥ 135; the bracket ends at X {CROSS_X[1]:.1f}).    Under the pinion (X 112 – 131) the rim must stay below Z {L.A_Z - L.PIN_OD / 2 - 1:.0f}.',
                    'If P is smaller, the cross member can move back about 1.5 mm or get thinner. Send the number.'], GREEN)])
save(fig, 'p4-front-end', pdf)

# ================================================================ 5 rear wall
fig = page('5 / 6', '5  Rear-wall gap at spool-centre height', 'The cradle drive sits the spool 5.1 mm further back (and 2.8 mm higher) than the stock rollers do.')
crop = (240, 170, 1220, 1010)
ax = photo(fig, [0.03, 0.36, 0.42, 0.45], '1000017856.jpg', crop, 'Your side photo. Do this with a spool seated on the stock rollers.')
ax.plot([300, 1180], [466, 466], '--', color=ORANGE, lw=1.3); tag(ax, (750, 440), 'spool-centre height (hub)', ORANGE)
arrow(ax, (335, 500), (420, 500), color=BLUE); tag(ax, (380, 540), 'W', BLUE)
ax.text(330, 600, 'rear\nwall', color='white', fontsize=8, weight='bold')
ax2 = schem(fig, [0.47, 0.38, 0.5, 0.44], (-75, 160), (-5, 225), 'Spool on the stock rollers vs. the cradle drive')
stock = np.array([PITCH / 2, ROD_Z + np.sqrt(106.5 ** 2 - (PITCH / 2) ** 2)])
ax2.add_patch(Circle(stock, FLANGE_R, fill=False, ec=GREY, ls='--')); ax2.add_patch(Circle(SPOOL_C, FLANGE_R, fill=False, ec='#8C6B3F', lw=1.5))
for x in (0, PITCH): ax2.add_patch(Circle((x, ROD_Z), 4, fc='#5B6770'))
ax2.plot([-62, -62], [0, 220], color=INK, lw=2, ls='--'); ax2.text(-64, 160, 'rear wall (position unknown)', ha='right', fontsize=7.5, rotation=90)
arrow(ax2, (-62, stock[1]), (stock[0] - FLANGE_R, stock[1]), color=BLUE, lw=2.6); ax2.text(-56, stock[1] + 8, 'W', color=BLUE, weight='bold', fontsize=12)
ax2.text(stock[0], stock[1] - 20, 'stock pose (dashed)', ha='center', fontsize=7.5, color=GREY)
ax2.text(SPOOL_C[0], SPOOL_C[1] + 12, 'cradle-drive pose:\n5.1 back, 2.8 up', ha='center', fontsize=7.5, color='#8C6B3F')
textbox(fig, [0.04, 0.03, 0.92, 0.31], [
    ('Steps', ['1. Put your largest spool on the stock rollers. Record its flange OD and overall width.',
               '2. At the height of the spool hub centre, measure horizontally from the flange\'s rear edge to the rear end wall inside the box: W. Use the depth rod or a ruler.',
               '3. Also measure the gap at the top: flange to the underside of the closed lid.'], INK),
    ('What works', ['Gap with the cradle drive ≈ W − 5.1. It must stay at least 1 mm.',
                    'If W < 6: tell me. The fix is a smaller tread with the spool slightly lower (the lid has 1.4 mm to give), or a slightly smaller spool limit.'], GREEN)])
save(fig, 'p5-rear-wall-gap', pdf)

# ================================================================ 6 record sheet
fig = page('6 / 6', 'Record sheet', 'Write each reading twice. Send this page with one photo per measurement.')
ax = fig.add_axes([0.04, 0.06, 0.92, 0.78]); ax.axis('off')
rows = [('1', 'A outside span (mid / end 1 / end 2)', '', '', ''), ('1', 'B inside span (mid / end 1 / end 2)', '', '', ''),
        ('1', 'Pitch = (A + B) / 2', '', '', '106 – 109 expected'),
        ('2', 'E outer faces of both front bearings', '', '', '≈ 88'), ('2', 'S slot width', '', '', '13.9 – 14.4'),
        ('2', 'H cradle top → slot bottom', '', '', '≈ 13'), ('2', 'T cradle plate thickness', '', '', 'record'),
        ('2', 'F between inboard plate faces', '', '', '≥ 79'), ('2', 'Slot walls straight? (y/n, photo)', '', '', ''),
        ('3', 'L rod length  /  d rod diameter', '', '', '≥ E  /  8.0'), ('3', 'Bearing removal: slides / snug / pressed / ring', '', '', ''),
        ('4', 'C rod front → rim crest  (+ crest height)', '', '', 'crest < Z 19 under pinion'), ('4', 'P rod front → end-loop face  (+ loop width)', '', '', '≥ 24'),
        ('5', 'Spool flange OD  /  width', '', '', ''), ('5', 'W flange → rear wall at hub height', '', '', '≥ 6'), ('5', 'Flange top → closed lid', '', '', '')]
cols = [0.0, 0.05, 0.48, 0.62, 0.76]; heads = ['#', 'Measurement', 'Reading 1', 'Reading 2', 'Works if']
for x, h in zip(cols, heads): ax.text(x, 1.0, h, weight='bold', color=GREEN, fontsize=10, transform=ax.transAxes, va='top')
y = 0.95
for r in rows:
    ax.add_patch(Rectangle((0, y - 0.052), 1, 0.052, transform=ax.transAxes, fc=LIGHT if int(r[0]) % 2 else 'white', ec='#D5E0E1', lw=0.6))
    for x, s in zip(cols, r): ax.text(x + 0.005, y - 0.026, s, fontsize=9.3, va='center', transform=ax.transAxes)
    y -= 0.052
ax.text(0, y - 0.04, 'Pitch sets the tread OD; everything else is pass/fail. Out-of-range numbers are fixable in the scripts. Send them and the CAD gets regenerated.',
        fontsize=9, color=GREY, transform=ax.transAxes)
save(fig, 'p6-record-sheet', pdf)
pdf.close()
print('ok')
