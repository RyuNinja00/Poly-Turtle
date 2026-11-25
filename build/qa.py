from design import *
import vtk
from vtk.util.numpy_support import vtk_to_numpy,numpy_to_vtk
def distance(f,a):
 r=vtk.vtkSTLReader();r.SetFileName(str(f));r.Update()
 imp=vtk.vtkImplicitPolyDataDistance();imp.SetInput(r.GetOutput());pp=vtk.vtkPoints();pp.SetData(numpy_to_vtk(np.ascontiguousarray(a)));pd=vtk.vtkPolyData();pd.SetPoints(pp);sf=vtk.vtkSampleImplicitFunctionFilter();sf.SetInputData(pd);sf.SetImplicitFunction(imp);sf.Update();return vtk_to_numpy(sf.GetOutput().GetPointData().GetScalars())
def pts(f):return np.array([v.toTuple() for v in step(f).tessellate(.2,.25)[0]])
a=pts('Smol-0.step');b=pts('PREP-0.step');b=b-(b.max(0)+b.min(0))/2+[7,-43,0];u=np.concatenate([(a-origin),b])@Rf.T+Tf
print('raised feeder-shell sampled clearance',distance(D/'05-Raised-lid-clearance-shell.stl',np.unique(u.round(2),axis=0)).min(),flush=True)
for f in ['Wheel-0.step','Wheel-1.step','Driven-gear-0.step']:
 u=(pts(f)-C)@Rr.T+Tr;print(f,distance(D/'04-Printable-box-PROXY.stl',np.unique(u.round(2),axis=0)).min(),flush=True)
