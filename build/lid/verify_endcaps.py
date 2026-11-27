"""End caps above Z 102: final canopy vs jojo's own lid, column by column (0.25 mm, Z step 0.2).
Mismatches within 2 samples of a jojo surface are mesh resolution; the rest must be the intended
changes (filled -X port, +X canopy wall over the bar at |x| <= 102.6)."""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'cradle-drive' / 'tools'))
import meshkit as mk, columns, printed_lid as P
from scipy import ndimage as ndi
t=mk.read_stl(HERE.parents[1] / 'cad/08-printed-lid/08-Printed-lid.stl'); V=t.reshape(-1,3); T=np.arange(len(V)).reshape(-1,3)
can=t[4316:]  # canopy shell triangles (base first)
Vj,Tj=P.endcap_tri(); jt=Vj[Tj]
zs=np.arange(102.2,111.5,0.2)
out={}
for side,xr in (('+X',np.arange(100.6,116.4,0.25)),('-X',np.arange(-116.3,-100.5,0.25))):
    ys=np.arange(-58,58.01,0.25)
    lo,hi=columns.intervals(jt,xr,ys); J=columns.zfield(lo,hi,zs)<0
    lo,hi=columns.intervals(can,xr,ys); C=columns.zfield(lo,hi,zs)<0
    mism=J!=C
    # tolerance: mismatch within 1 sample of a jojo boundary is resolution
    edge=ndi.binary_dilation(J,iterations=2)&~ndi.binary_erosion(J,iterations=2)
    real=mism&~edge
    X=xr[:,None,None]+0*ys[None,:,None]+0*zs; Y=ys[None,:,None]+0*X; Z=zs[None,None,:]+0*X
    port=(np.hypot(X+100,Y)<5)
    cliff=(np.abs(X)<=102.6)
    keep=real&~port&~cliff
    out[side]=dict(jojo=int(J.sum()),mismatch=int(mism.sum()),beyond_2_samples=int(real.sum()),excluding_port_and_cliff=int(keep.sum()))
    if keep.any():
        idx=np.argwhere(keep); print(side,'examples',[(round(xr[a],2),round(ys[b],2),round(zs[c],2),bool(J[a,b,c])) for a,b,c in idx[:: max(1,len(idx)//12)][:12]])
print(out)
