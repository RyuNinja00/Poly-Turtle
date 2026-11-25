import sys
from pathlib import Path
import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool as X
from OCP.TDF import TDF_LabelSequence,TDF_Label
from OCP.TDataStd import TDataStd_Name
rev=sys.argv[1];r=STEPCAFControl_Reader();r.SetNameMode(True);r.ReadFile(rev+'.step');d=TDocStd_Document(TCollection_ExtendedString('doc'));r.Transfer(d);t=X.ShapeTool_s(d.Main());seq=TDF_LabelSequence();t.GetShapes(seq)
def name(l):
 a=TDataStd_Name();return a.Get().ToExtString() if l.FindAttribute(a.GetID_s(),a) else ''
def save(sh,tag):
 idx=sum(1 for _ in Path('.').glob(tag+'-*.step'));p=tag+'-'+str(idx)+'.step';cq.exporters.export(sh,p);print(p,flush=True)
def walk(l,loc,mode):
 n=name(l);tag=''
 if mode=='drive':
  tag={'Wheel v3':'Wheel','MR148ZZ':'Bearing','8x80mm shaft':'Shaft','gear_30_spacer_x4':'Spacer','helical_gear_30_teeth_x4':'Driven-gear','helical_gear_15_teeth_x4':'Pinion'}.get(n,'')
 elif mode=='feed':
  tag={'BMG Gear Kit':'BMG','Omron D2HW-C201H v2 (3)':'LOAD'}.get(n,'')
  if n.startswith('LDO-36STH'):tag='Stepper'
  if n.startswith('Omron D2HW'):tag='LOAD'
 elif mode=='elec':
  if n.startswith('N20 DC MOTOR'):tag='N20'
  if n.startswith('D2F-L_Straight v1'):tag='PREP'
 if tag:save(cq.Shape.cast(t.GetShape_s(l)).located(loc),tag);return
 q=TDF_LabelSequence();t.GetComponents_s(l,q)
 for j in range(1,q.Length()+1):
  ll=q.Value(j);ref=TDF_Label();t.GetReferredShape_s(ll,ref);walk(ref,loc*cq.Location(t.GetLocation_s(ll)),mode)
seen=set()
for i in range(1,seq.Length()+1):
 l=seq.Value(i);n=name(l)
 if n in seen:continue
 seen.add(n)
 if rev=='v10' and n=='E-Spooler v5':walk(l,cq.Location(),'drive')
 if rev=='v10' and n=='Smol-D2HW v2':walk(l,cq.Location(),'feed')
 if rev=='v11' and n=='E-Spooler_1.1':walk(l,cq.Location(),'elec')
 if rev=='v11' and n=='Smol-D2HW':save(cq.Shape.cast(t.GetShape_s(l)),'Smol')
