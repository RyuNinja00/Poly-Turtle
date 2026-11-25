import cadquery as cq,numpy as np
from scipy.spatial.transform import Rotation as Rot
from pathlib import Path
from OCP.gp import gp_Trsf
D=Path('pkg');C=np.array([41.3666,194.9537,70.2236]);origin=np.array([34.735,115,6.253]);rear=-54.5;rz=-np.sqrt(106.5**2-rear**2);dx=-6.072124302839878;dz=rz+np.sqrt(106.5**2-(dx-rear)**2);sp=np.array([dx,0,dz]);angle=np.deg2rad(40.11723234778508)
Tr=np.array([124.382*np.sin(angle),0,-124.382*np.cos(angle)])+sp
Rr=Rot.from_euler('y',-171.4383691372638,degrees=True).as_matrix()@np.array([[0,-1,0],[1,0,0],[0,0,1]])
Rf=Rot.from_euler('y',114.83758478971156,degrees=True).as_matrix()@Rot.from_euler('z',92.02810427172394,degrees=True).as_matrix()@np.array([[0,0,1],[1,0,0],[0,1,0]])
Tf=np.array([50.82170486028815,-1.52379502811359,104.38142041181])
def loc(R,T):
 tr=gp_Trsf();tr.SetValues(*np.column_stack([R,T]).flatten());return cq.Location(tr)
def step(f):return cq.importers.importStep(str(f)).val()
def box(a,b,c,d,e,f):return cq.Solid.makeBox(b-a,d-c,f-e,(a,c,e))
def cyl(r,l,o,d):return cq.Solid.makeCylinder(r,l,cq.Vector(*o),cq.Vector(*d))
def part():
 bs=[]
 for x in [-19.825,15.82]:
  b=cyl(10,4,(x,0,0),(1,0,0)).fuse(box(x,x+4,-10,10,-19,0)).cut(cyl(7.05,5,(x-.5,0,0),(1,0,0)))
  if x>0:b=b.cut(box(x-1,x+5,-6.2,6.2,-28,-11.85))
  bs.append(b)
 b=bs[0].fuse(bs[1])
 for y in [-10,7.15]:b=b.fuse(box(-19.825,19.82,y,y+2.85,-21,-16))
 b=b.fuse(box(-5.25,19.82,-9,9,-24.3,-22.18))
 for y in [-8.8,6.18]:b=b.fuse(box(-5.25,19.82,y,y+2.62,-23,-16))
 for x in [-.5,10]:
  for y in [-7.8,7.8]:b=b.cut(box(x,x+2.6,y-.65,y+.65,-26,-18.5))
 for x in [-16,10]:b=b.fuse(box(x,x+8,7.15,15,-21,-17.6).cut(cyl(1.65,5,(x+4,12,-22),(0,0,1))))
 return b.clean()
dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
def register():
 data=Path('3689772.geom').read_bytes();v=np.frombuffer(data[84:],dtype=dtype).copy();v['v']+=[0,0,rz+158];(D/'04-Printable-box-PROXY.stl').write_bytes(data[:84]+v.tobytes())
 s=part();assert s.isValid() and len(s.Solids())==1;s.exportStl(str(D/'06-Roller-bench-carrier.stl'),.06,.15);cq.exporters.export(s,str(D/'06-Roller-bench-carrier.step'))
 cav=step('7280858.geom').rotate((0,0,0),(1,0,0),180).translate((67.3,0,110.01));cq.exporters.export(cav,str(D/'02-Stock-lid-free-volume.step'))
def shell():
 import sys;sys.path.insert(0,'deps');import manifold3d as m
 v=np.fromfile('6064460.geom',offset=84,dtype=dtype)['v'];verts,idx=np.unique(v.reshape(-1,3),axis=0,return_inverse=True);mesh=m.Mesh(vert_properties=verts,tri_verts=idx.reshape(-1,3).astype(np.uint32));mesh.merge()
 lid=m.Manifold(mesh).translate((0,0,59.21))
 def block(lo,hi):return m.Manifold.cube(np.array(hi)-lo).translate(lo)
 outer=block([2,-42,108.5],[102,34,147]);inner=block([4.5,-39.5,70],[99.5,31.5,144.5]);axis=Rf[:,1];hole=m.Manifold.cylinder(53,2.15,2.15,64).transform(np.column_stack([Rf[:,0],-Rf[:,2],axis,Tf+axis*33]))
 s=(lid+outer)-inner-hole;assert s.status()==m.Error.NoError and len(s.decompose())==1
 b=s.to_mesh();tri=b.vert_properties[b.tri_verts,:3];out=np.zeros(len(tri),dtype=dtype);out['v']=tri;n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);out['n']=n/np.maximum(1e-20,np.linalg.norm(n,axis=1))[:,None];(D/'05-Raised-lid-clearance-shell.stl').write_bytes(bytes(80)+len(tri).to_bytes(4,'little')+out.tobytes())
if __name__=='__main__':register();shell()
