"""Write cad/07-Cradle-drive-layout.step from the archived fit-study assembly.

Keeps: spool, rear roller proxy, Smol feeder with LOAD, PREP position, inlet/outlet
filament paths, the V1.0 N20 (and its pinion for the v1pinion gear set) and an MR148.
The printed roller, treads, pinion and bracket are STLs in the same coordinates.  Re-poses everything
into measured box coordinates (rear factory axle = X 0, interior floor = Z 0).
"""
import sys, re, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))
from steplib import load, refs, closure, components, axis2, point
import cradle_drive as cd

SRC = cd.STEP01
DST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'cad' / '07-Cradle-drive-layout.step'
GEARSET = sys.argv[2] if len(sys.argv) > 2 else 'fast'
L = cd.Layout(GEARSET)
REMOVE = ['Wheel-0', 'Wheel-1', 'Bearing-1', 'Shaft-0', 'Trial_carrier', 'Driven-gear-0', 'Spacer-0'] + (['Pinion-0'] if GEARSET == 'fast' else [])

txt, ents = load(SRC)
comps = components(ents)

def find(pred):
    return [i for i, s in ents.items() if pred(s)]

pdshape = {refs(s)[0]: i for i, s in ents.items() if s.startswith("PRODUCT_DEFINITION_SHAPE('',")}
sdr = {refs(s)[0]: i for i, s in ents.items() if s.startswith('SHAPE_DEFINITION_REPRESENTATION')}
srr = {}
for i, s in ents.items():
    if s.startswith('SHAPE_REPRESENTATION_RELATIONSHIP') or ('SHAPE_REPRESENTATION_RELATIONSHIP()' in s and 'REPRESENTATION_RELATIONSHIP(' in s and 'TRANSFORMATION' not in s):
        pass
for i, s in ents.items():
    if s.startswith("SHAPE_REPRESENTATION_RELATIONSHIP('','',"):
        srr.setdefault(refs(s)[0], []).append(i)
cdsr_by_nauo = {}
for i, s in ents.items():
    if s.startswith('CONTEXT_DEPENDENT_SHAPE_REPRESENTATION'):
        rr, pds = refs(s)[:2]
        cdsr_by_nauo[refs(ents[pds])[0]] = (i, rr, pds)
prpc_by_product = {}
for i, s in ents.items():
    if s.startswith('PRODUCT_RELATED_PRODUCT_CATEGORY'):
        for r in refs(s): prpc_by_product[r] = i

removed_roots, removed_reps = set(), []
for n in REMOVE:
    c = comps[n]; cdsr, rr, pds = cdsr_by_nauo[c['nauo']]
    pd = c['child']; form = refs(ents[pd])[0]; prod = refs(ents[form])[0]
    removed_roots |= {c['nauo'], cdsr, pds, sdr[pdshape[pd]], prpc_by_product[prod]}
    removed_roots |= set(srr.get(c['rep'], []))
    removed_reps.append(c['rep'])
    removed_reps += [refs(ents[k])[1] for k in srr.get(c['rep'], [])]

referenced = set()
for s in ents.values(): referenced.update(refs(s))
top = set(ents) - referenced
kept_reps = [d['rep'] for n, d in comps.items() if n not in REMOVE and d['rep']]
kept_reps += [refs(ents[k])[1] for r in list(kept_reps) for k in srr.get(r, [])]
kept_geo = closure(ents, kept_reps)
removed_only = closure(ents, removed_reps) - kept_geo

# presentation: drop styled items on removed geometry, drop MDGPRs that become empty
new_text = {}
for i in list(top):
    s = ents[i]
    if s.startswith('MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION'):
        head, rest = s.split('(', 1)
        items_txt = rest[rest.index('(') + 1: rest.index(')')]
        items = refs(items_txt)
        keep = [k for k in items if refs(ents[k])[-1] not in removed_only]
        ctx = refs(rest[rest.index(')'):])
        if not keep or (ctx and ctx[0] in removed_only):
            removed_roots.add(i); continue
        new_text[i] = "MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(" + ','.join(f'#{k}' for k in keep) + ')' + rest[rest.index(')') + 1:]

roots = [i for i in top if i not in removed_roots]
for i, t in new_text.items(): ents[i] = t
K = closure(ents, roots)
assert not (K & removed_only), 'removed geometry still referenced'

# ---------------------------------------------------------------- placements
from collections import Counter
REFCOUNT = Counter(r for s in ents.values() for r in refs(s))
def set_axis(aid, origin, R):
    p, zdir, xdir = refs(ents[aid])[:3]
    assert REFCOUNT[p] == 1 and REFCOUNT[zdir] == 1 and REFCOUNT[xdir] == 1, ('shared placement entity', aid)
    ents[p] = "CARTESIAN_POINT('',(%.9g,%.9g,%.9g))" % tuple(origin)
    ents[zdir] = "DIRECTION('',(%.12g,%.12g,%.12g))" % tuple(R[:, 2])
    ents[xdir] = "DIRECTION('',(%.12g,%.12g,%.12g))" % tuple(R[:, 0])

top_children = {n: d for n, d in comps.items() if d['parent'] == 5}
for n, d in top_children.items():
    cdsr, rr, pds = cdsr_by_nauo[d['nauo']]
    idt = [r for r in refs(ents[rr]) if ents[r].startswith('ITEM_DEFINED_TRANSFORMATION')][0]
    set_axis(refs(ents[idt])[1], cd.MODEL_TO_BOX, np.eye(3))
poses = [('N20-0', cd.R_N20, L.T_N20 - cd.MODEL_TO_BOX), ('Bearing-0', np.eye(3), cd.T_BEARING - cd.MODEL_TO_BOX)]
if GEARSET != 'fast': poses.append(('Pinion-0', cd.R_N20, L.T_N20 - cd.MODEL_TO_BOX))
# feeder parts follow the printed lid (rev 3: re-posed 45 deg uphill, build/lid/printed_lid.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lid'))
from pose import Pose
import json as _json
_rep = _json.load(open(Path(__file__).resolve().parents[2] / 'cad/08-printed-lid/mesh-report.json'))['pose']
FEED = Pose(_rep['alpha_deg'], _rep['inlet'])
for n in ('Smol_feeder_with_LOAD', 'PREP_position', 'Inlet_path', 'Outlet_path'):
    poses.append((n, FEED.R.as_matrix(), FEED.t + (cd.MODEL_TO_BOX if comps[n]['parent'] == 5 else 0)))
for n, R, T in poses:
    cdsr, rr, pds = cdsr_by_nauo[comps[n]['nauo']]
    idt = [r for r in refs(ents[rr]) if ents[r].startswith('ITEM_DEFINED_TRANSFORMATION')][0]
    set_axis(refs(ents[idt])[1], T, R)
ents[53] = "PRODUCT('Cradle_drive_donor_parts','Cradle_drive_donor_parts','',(#54))"
ents[7] = "PRODUCT('Poly_Turtle_cradle_drive_layout','Poly_Turtle_cradle_drive_layout','',(#8))"

# placements of shared points must be unique to their axis: verify
for n, d in top_children.items():
    pass
header = txt.split('DATA;', 1)[0]
header = re.sub(r"'2026-11-24T16:17:13'", "'2026-11-25T16:00:00'", header)
header = re.sub(r"FILE_DESCRIPTION\(\(.*?\)", "FILE_DESCRIPTION(('Poly-Turtle cradle drive layout, box coordinates: X fwd from rear factory axle, Z up from floor, mm')", header, flags=re.S)
with open(DST, 'w', encoding='latin-1') as f:
    f.write(header + 'DATA;\n')
    for i in sorted(K):
        f.write(f'#{i} = {ents[i]};\n')
    f.write('ENDSEC;\nEND-ISO-10303-21;\n')
print('wrote', DST, len(K), 'entities of', len(ents))
