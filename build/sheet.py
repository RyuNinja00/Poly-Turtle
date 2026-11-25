from design import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from scipy.spatial import ConvexHull
def lines(file,y):
 v=np.fromfile(file,offset=84,dtype=dtype)['v'];out=[]
 for t in v[(v[:,:,1].min(1)<y)&(v[:,:,1].max(1)>y)]:
  ends=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   u,w=t[i],t[j]
   if (u[1]<y)!=(w[1]<y):ends.append((u+(w-u)*(y-u[1])/(w[1]-u[1]))[[0,2]])
  if len(ends)==2:out.append(ends)
 return out
def hull(sh,R,T):
 v=np.array([v.toTuple() for v in sh.tessellate(.2,.25)[0]])@R.T+T;v=v[:,[0,2]];return v[ConvexHull(v).vertices]
c=hull(part(),Rr,Tr);feed=hull(step('Smol-0.step'),Rf,Tf-Rf@origin)
def draw(ax,full):
 ax.set_aspect('equal');ax.axis('off')
 ax.add_patch(Circle((dx,dz),102.5,facecolor='#f1e9d8',edgecolor='#977e53',lw=1))
 for yy in [13.5,42.1]:ax.add_collection(LineCollection(lines(D/'04-Printable-box-PROXY.stl',yy),colors='#68757a',linewidths=.65))
 ax.add_patch(Circle((rear,rz),4,color='#26749a'));ax.add_patch(Circle(Tr[[0,2]],23.8,facecolor='#49545a'));ax.add_patch(Circle(Tr[[0,2]],21.88,fill=False,edgecolor='#dadcda',lw=.6))
 ax.fill(*c.T,color='#d58b48',alpha=.8)
 if full:
  ax.add_collection(LineCollection(lines(D/'05-Raised-lid-clearance-shell.stl',.17),colors='#254352',linewidths=1))
  ax.fill(*feed.T,color='#2b827c',alpha=.85)
with PdfPages(D/'Start-here-Fit-check.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.055,.92,'One BoxTurtle lane in a PolyDryer Box',fontsize=21,weight='bold');f.text(.055,.87,'V1.0 driven roller   /   205 × 78 mm design spool   /   side view',fontsize=11,color='#397174')
 ax=f.add_axes([.04,.07,.53,.75]);draw(ax,True);ax.set(xlim=(-124,124),ylim=(-122,154))
 for i,(title,msg) in enumerate([('Feeder and lid','The assembled Smol feeder is shown in teal.\nThe raised pocket adds 35.4 mm to the\ntwo-port replacement lid.'),('Driven roller','The dark wheel outline includes the hub lip.\nThe orange carrier holds both shaft bearings\nand the N20 motor.'),('Rear support','The blue circle marks the assumed center of\nthe factory roller. Its diameter and position\ncome from the printable box reference.'),('Floor clearance','The wheel ends, driven gear and carrier enter\nthe printable reference near its floor. Check\nthe molded box with the template on page 2.')]):
  y=.76-.16*i;f.text(.58,y,title,fontsize=13,weight='bold');f.text(.58,y-.027,msg,fontsize=10,va='top',linespacing=1.4)
 pdf.savefig(f);plt.close(f)
 f=plt.figure(figsize=(11,8.5));f.text(.06,.93,'Roller position template',fontsize=21,weight='bold');f.text(.06,.88,'Print on US Letter landscape at 100%. Check the 50 mm scale bar.',fontsize=12)
 ax=f.add_axes([.075,.23,219/279.4,119/215.9]);draw(ax,False);ax.set(xlim=(-100,119),ylim=(-126,-7))
 for x,z in [(rear,rz),(Tr[0],Tr[2])]:
  ax.plot([x-3,x+3],[z,z],color='black',lw=.8);ax.plot([x,x],[z-3,z+3],color='black',lw=.8)
 ax.annotate('Factory rear roller',(rear,rz),(-93,-62),arrowprops={'arrowstyle':'-'},fontsize=9);ax.annotate('BoxTurtle axle',Tr[[0,2]],(67,-58),arrowprops={'arrowstyle':'-'},fontsize=9)
 ax.plot([-90,-40],[-116,-116],color='black',lw=1.8);ax.plot([-90,-90],[-118,-114],color='black');ax.plot([-40,-40],[-118,-114],color='black');ax.text(-65,-122,'50 mm',ha='center',fontsize=9)
 f.text(.075,.15,'Trial axle center is 128.57 mm forward and 0.27 mm below the rear roller center.',fontsize=11,weight='bold')
 f.text(.075,.08,'Check the floor at both wheel lips, about 42 mm either side of the spool midplane, and at the driven gear, about\n13.5 mm off center. The two grey sections are from the printable box. Compare them with your molded box.',fontsize=10)
 pdf.savefig(f);plt.close(f)
