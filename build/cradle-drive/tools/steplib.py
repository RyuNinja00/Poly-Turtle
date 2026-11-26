"""Minimal STEP (AP214, OCC-style) reader: entity table, assembly tree, per-part point clouds."""
import re, numpy as np
from collections import defaultdict

ENT = re.compile(r"#(\d+)\s*=\s*(.*?);\s*$", re.S)

def load(path):
    txt = open(path, encoding='latin-1').read()
    data = txt.split('DATA;', 1)[1].rsplit('ENDSEC;', 1)[0]
    ents = {}
    for stmt in data.split(';\n'):
        stmt = stmt.strip()
        if not stmt.startswith('#'):
            continue
        k, v = stmt.split('=', 1)
        ents[int(k[1:])] = ' '.join(v.split())
    return txt, ents

REF = re.compile(r"#(\d+)")
NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:E[-+]?\d+)?", re.I)

def refs(s):
    return [int(x) for x in REF.findall(s)]

def closure(ents, roots):
    seen, st = set(), list(roots)
    while st:
        i = st.pop()
        if i in seen: continue
        seen.add(i)
        st.extend(refs(ents[i]))
    return seen

def nums(s):
    inner = s[s.index('(', s.index('(') + 1):]
    return [float(x) for x in NUM.findall(inner.split(')')[0])]

def point(ents, i):
    s = ents[i]; return np.array([float(x) for x in NUM.findall(s.split("',")[1])][:3])

def direction(ents, i):
    return point(ents, i)

def axis2(ents, i):
    r = refs(ents[i]); o = point(ents, r[0]); z = direction(ents, r[1]); x = direction(ents, r[2]) if len(r) > 2 else np.array([1., 0, 0])
    z = z / np.linalg.norm(z); x = x - z * (x @ z); x /= np.linalg.norm(x); y = np.cross(z, x)
    return o, np.column_stack([x, y, z])

def part_points(ents, ids, circle_n=24):
    pts = []
    for i in ids:
        s = ents[i]
        if s.startswith('VERTEX_POINT'):
            pts.append(point(ents, refs(s)[0]))
        elif s.startswith('CIRCLE('):
            r = refs(s); rad = float(NUM.findall(s.split(',')[-1])[0])
            if len(point(ents, refs(ents[r[0]])[0])) < 3: continue
            o, R = axis2(ents, r[0])
            t = np.linspace(0, 2 * np.pi, circle_n, endpoint=False)
            pts.extend(o + rad * (np.outer(np.cos(t), R[:, 0]) + np.outer(np.sin(t), R[:, 1])))
    return np.array(pts)

def components(ents):
    """name -> (shape_rep_id, parent pd id) for every NAUO"""
    out = {}
    pds = {}
    for i, s in ents.items():
        if s.startswith('NEXT_ASSEMBLY_USAGE_OCCURRENCE'):
            name = s.split("'")[3]; r = refs(s); out[name] = dict(nauo=i, parent=r[0], child=r[1])
    # shape rep for each product definition
    pdshape = {}
    for i, s in ents.items():
        if s.startswith("PRODUCT_DEFINITION_SHAPE('',"):
            pdshape[refs(s)[0]] = i
    sdr = {}
    for i, s in ents.items():
        if s.startswith('SHAPE_DEFINITION_REPRESENTATION'):
            a, b = refs(s)[:2]; sdr[a] = b
    for n, d in out.items():
        d['rep'] = sdr.get(pdshape.get(d['child']))
    return out

def rep_bodies(ents, rep):
    """shape reps hold MANIFOLD_SOLID_BREP via SHAPE_REPRESENTATION_RELATIONSHIP or directly"""
    roots = [rep]
    for i, s in ents.items():
        if s.startswith('SHAPE_REPRESENTATION_RELATIONSHIP') and refs(s)[0] == rep:
            roots.append(refs(s)[1])
    return roots
