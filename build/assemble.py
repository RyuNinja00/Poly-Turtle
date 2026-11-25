from design import *
def add(asm,s,n,c):asm.add(s,name=n,color=cq.Color(*c))
dark=(.17,.22,.25);grey=(.64,.68,.71);teal=(.05,.55,.52);orange=(.94,.46,.1);purple=(.54,.34,.67)
a=cq.Assembly(name='Single_lane_fit_study');drive=cq.Assembly(name='V10_roller')
for prefix,count in [('Wheel',2),('Bearing',2),('Shaft',1),('Spacer',1),('Driven-gear',1),('Pinion',1),('N20',1)]:
 for i in range(count):
  k=f'{prefix}-{i}';s=step(k+'.step')
  if prefix=='N20':s=s.translate((0,-.02,-.07))
  add(drive,s.moved(loc(Rr,Tr-Rr@C)),k,dark if prefix=='Wheel' else grey)
add(drive,part().moved(loc(Rr,Tr)),'Trial_carrier',orange);a.add(drive)
add(a,cyl(4,95,(rear,-47.5,rz),(0,1,0)),'Rear_roller_proxy',(.15,.42,.66))
spool=cyl(97.5,74,(dx,-37,dz),(0,1,0)).fuse(cyl(102.5,2,(dx,-39,dz),(0,1,0)),cyl(102.5,2,(dx,37,dz),(0,1,0))).cut(cyl(27.5,80,(dx,-40,dz),(0,1,0)))
add(a,spool,'Spool_205x78',(.78,.74,.63));s=step('Smol-0.step');add(a,s.moved(loc(Rf,Tf-Rf@origin)),'Smol_feeder_with_LOAD',teal)
prep=step('PREP-0.step');vv=np.array([v.toTuple() for v in prep.tessellate(.18,.25)[0]]);mid=(vv.min(0)+vv.max(0))/2
add(a,prep.moved(loc(Rf,Tf+Rf@(np.array([7,-43,0])-mid))),'PREP_position',purple)
for label,lo,hi in [('Inlet_path',-58,-30),('Outlet_path',38,49)]:add(a,cyl(.875,hi-lo,(0,lo,0),(0,1,0)).moved(loc(Rf,Tf)),label,(.9,.18,.12))
a.export(str(D/'01-Single-lane-fit-study.step'))
a=cq.Assembly(name='Stock_lid_trial');R=Rot.from_euler('zyx',[64.67418798,117.17517567,-154.20359024],degrees=True).as_matrix()@np.array([[0,0,1],[1,0,0],[0,1,0]]);T=np.array([59.9404488,-8.20312103,106.59029408])
for n,c in [('LOAD',purple),('Stepper',teal),('BMG',grey)]:add(a,step(n+'-0.step').moved(loc(R,T-R@origin)),n,c)
a.export(str(D/'03-Stock-lid-interference-trial.step'))
