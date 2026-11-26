"""Sample the Smol (with LOAD) and PREP reference parts from cad/01 into clouds.pkl.

Vertices plus circles up to r 6 mm (larger arcs are skipped: sampling a partial
arc as a full circle would invent geometry).  Used by checks.py and render.py."""
import sys, pickle, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
from steplib import load, components, closure, rep_bodies, refs, point, axis2, NUM

def cloud(ents, comps, name, rmax=6.0):
    pts = []
    for i in closure(ents, rep_bodies(ents, comps[name]['rep'])):
        s = ents[i]
        if s.startswith('VERTEX_POINT'):
            pts.append(point(ents, refs(s)[0]))
        elif s.startswith('CIRCLE('):
            r = refs(s)
            if len(point(ents, refs(ents[r[0]])[0])) < 3: continue
            o, R = axis2(ents, r[0]); rad = float(NUM.findall(s.split(',')[-1])[0])
            if rad <= rmax:
                t = np.linspace(0, 2 * np.pi, 24, endpoint=False)
                pts.extend(o + rad * (np.outer(np.cos(t), R[:, 0]) + np.outer(np.sin(t), R[:, 1])))
    return np.array(pts)

if __name__ == '__main__':
    _, ents = load(ROOT / 'cad' / '01-Single-lane-fit-study.step'); comps = components(ents)
    d = dict(smol=cloud(ents, comps, 'Smol_feeder_with_LOAD'), prep=cloud(ents, comps, 'PREP_position'))
    pickle.dump(d, open(HERE / 'clouds.pkl', 'wb')); print({k: v.shape for k, v in d.items()})
