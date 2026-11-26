import sys, numpy as np
sys.path.insert(0, 'tools'); from steplib import *
import cradle_drive as cd
path = sys.argv[1]
txt, ents = load(path)
bad = [(i, r) for i, s in ents.items() for r in refs(s) if r not in ents]
print('dangling refs', len(bad), bad[:5])
comps = components(ents); print('components', sorted(comps))
cdsr = {}
for i, s in ents.items():
    if s.startswith('CONTEXT_DEPENDENT_SHAPE_REPRESENTATION'):
        rr, pds = refs(s)[:2]; cdsr[refs(ents[pds])[0]] = rr
def xf(n):
    rr = cdsr[comps[n]['nauo']]
    idt = [r for r in refs(ents[rr]) if ents[r].startswith('ITEM_DEFINED_TRANSFORMATION')][0]
    a, b = refs(ents[idt])[0:2]
    oa, Ra = axis2(ents, a); ob, Rb = axis2(ents, b)
    return Rb @ Ra.T, ob - Rb @ Ra.T @ oa
pd_parent = {d['child']: n for n, d in comps.items()}
def world(n):
    R, t = xf(n); p = comps[n]['parent']
    while p in pd_parent:
        R2, t2 = xf(pd_parent[p]); R, t = R2 @ R, R2 @ t + t2; p = comps[pd_parent[p]]['parent']
    return R, t
for n in sorted(comps):
    if comps[n]['rep'] is None: continue
    ids = closure(ents, rep_bodies(ents, comps[n]['rep']))
    v = np.array([point(ents, refs(ents[i])[0]) for i in ids if ents[i].startswith('VERTEX_POINT')])
    if not len(v): continue
    R, t = world(n); w = v @ R.T + t
    print(f'{n:24s}', w.min(0).round(2), w.max(0).round(2))
    if n == 'Spool_205x78': print('   spool axis X,Z from flange top', np.array([w[:, 0].mean(), w[:, 2].max() - cd.FLANGE_R]).round(3), 'expected', cd.SPOOL_C.round(3))
    key = {'N20-0': 'n20', 'Pinion-0': 'v1_pinion'}.get(n)
    if key:
        ref = cd.Layout(sys.argv[2] if len(sys.argv) > 2 else 'fast').donor()[key]; print(f'   {n} max deviation vs design pose', np.abs(np.sort(w, 0) - np.sort(ref, 0)).max().round(4))
