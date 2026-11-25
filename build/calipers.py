from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.lib.pagesizes import landscape,letter
from pypdf import PdfReader,PdfWriter
from pathlib import Path
import math,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from design import dtype
D=Path('pkg')
tri=np.fromfile(D/'04-Printable-box-PROXY.stl',offset=84,dtype=dtype)
v=tri['v'];n=tri['n'];order=v[:,:,2].mean(1).argsort();shade=np.clip(.38+.50*np.clip(n@np.array([-.35,-.4,.85]),0,1)+.07*(v[:,:,2].mean(1)+120)/200,0,1)
col=np.clip(shade[:,None]*np.array([.95,1,1.02]),0,1)
fig=plt.figure(figsize=(8,4));ax=fig.add_axes([0,0,1,1]);ax.add_collection(PolyCollection(v[order,:,:2],facecolor=col[order],edgecolor='face',linewidth=.16));ax.set(xlim=(-120,120),ylim=(-60,60),aspect='equal');ax.axis('off');fig.savefig('box-top.png',dpi=150,transparent=True);plt.close(fig)
c=canvas.Canvas('caliper-pages.pdf',pagesize=landscape(letter));ink='#172F39';grey='#596E76';blue='#12658A';orange='#A8431C';light='#EAF1F1';green='#007968'
def txt(x,y,s,size=11,b=False,color=ink):
 c.setFillColor(HexColor(color));c.setFont('Helvetica-Bold' if b else 'Helvetica',size);c.drawString(x,612-y,s)
def line(x,y,X,Y,color=ink,w=1,dash=None):
 c.setStrokeColor(HexColor(color));c.setLineWidth(w);c.setDash(dash or []);c.line(x,612-y,X,612-Y);c.setDash([])
def rect(x,y,w,h,fill=light,stroke=grey):
 c.setStrokeColor(HexColor(stroke));c.setFillColor(HexColor(fill));c.rect(x,612-y-h,w,h,fill=1,stroke=1)
def circle(x,y,r,fill=light,stroke=grey):
 c.setStrokeColor(HexColor(stroke));c.setFillColor(HexColor(fill));c.circle(x,612-y,r,fill=1,stroke=1)
def ar(x,y,X,Y,color=orange,both=True):
 line(x,y,X,Y,color,1.5)
 for x1,y1,x2,y2 in [(x,y,X,Y)]+([(X,Y,x,y)] if both else []):
  a=math.atan2(y2-y1,x2-x1)
  for da in [-.45,.45]:line(x1,y1,x1+6*math.cos(a+da),y1+6*math.sin(a+da),color,1.35)
def head(k,title,sub):
 txt(37,34,'POLYDRYER BOX    /    CALIPER GUIDE',9,True,green);txt(37,72,title,25,True);txt(37,95,sub,11,color=grey)
 line(37,108,755,108,'#B6C8CA');txt(704,34,k,10,True,grey)
def para(x,y,lines):
 for s in lines:txt(x,y,s,11);y+=16
def foot(s):
 line(37,558,755,558,'#B6C8CA');txt(37,580,s,10,color=grey);c.showPage()
head('3 / 6','Locate the wheel and gear tracks','Remove the lid, spool and loose accessories. Leave the passive rear roller seated. All readings are in millimeters.')
# map isotropic x-right y-up; longitudinal +X toward future drive
left,top,scale=77,150,2.57
c.drawImage('box-top.png',left,612-top-120*scale,240*scale,120*scale,mask='auto')
def mapxy(x,y):return left+(x+120)*scale,top+(60-y)*scale
def mline(x,y,X,Y,*a):line(*mapxy(x,y),*mapxy(X,Y),*a)
for y in [42,-42,13.5,-13.5]:mline(50,y,100,y,orange,1.3,[4,2])
for u in [117,129,136,145]:
 x=-54.5+u;txt(mapxy(x,0)[0]-6,149,str(u),8,True,blue);mline(x,-44,x,44,blue,.85,[2,2])
 for y in [42,13.5,-13.5,-42]:circle(*mapxy(x,y),2.7,'#FFE4B5',orange)
mline(-54.5,-46,-54.5,46,blue,5);mline(-54.5,0,100,0,green,1.1,[5,3])
txt(66,135,'Rear end',11,True,blue);txt(540,135,'End receiving driven wheels',11,True,orange)
for y,s in [(42,'L 42'),(13.5,'L 13.5'),(-13.5,'R 13.5'),(-42,'R 42')]:txt(651,mapxy(0,y)[1]+4,s,10,True,orange)
txt(75,477,'Blue roller = distance zero',11,True,blue);txt(258,477,'Green line = midplane',11,True,green);txt(444,477,'Dots = depth-probe stations',11,True,orange)
para(38,504,['Sight straight down and mark the rear roller centerline on tape on both side rims. Mark the midpoint across the box.',
'On a paper strip along the rim, mark 117, 129, 136 and 145 mm from the rear centerline toward the drive. At each',
'station, place a straightedge across both rims. Mark its four probe tracks at 13.5 and 42 mm either side of its midpoint.'])
foot('Top view uses the printable reference body. Use the surfaces of your molded box for the readings.')
head('4 / 6','Measure the roller and floor','Use the same rigid straightedge across the same hard rim ledges for every depth reading.')
txt(37,139,'A   Roller diameter',16,True);txt(393,139,'B   Depth to roller and floor',16,True)
circle(155,235,35,'#C9D7DA');rect(95,165,139,9,'#A4BBC2');rect(109,174,11,65,'#ACC2C8');rect(190,174,11,65,'#ACC2C8');rect(177,159,45,20,'#83A5B3');ar(120,235,190,235);txt(142,224,'D',12,True,orange)
para(38,317,['Close the outside jaws across the round surface','that actually carries the spool flange. Keep the','jaws square to the axle. Rotate and repeat.','If a sleeve or bearing supports the spool, measure','its outside diameter. Record left and right if different.'])
# depth caliper on edge of bridge relative to shifted caliper heel
rect(405,202,303,10,'#B4D4CC',green);rect(411,212,10,84);rect(692,212,10,84);rect(411,292,291,9)
circle(475,270,13,'#C9D7DA');rect(601,280,39,12,'#B8C7C9')
for xx,yy in [(475,257),(622,280)]:
 rect(xx-13,157,13,45,'#A0BAC3',blue);rect(xx-18,145,22,17,'#D7E2E5',blue);line(xx,202,xx,yy,blue,1.7);circle(xx,yy,2,orange,orange)
# draw break at probe on bridge edge for sightline
txt(445,241,'C',12,True,orange);txt(631,258,'F',12,True,orange);txt(495,195,'Bridge top',10,True,green)
para(393,317,['Rest the flat depth-measuring end on the bridge','with the thin rod extending just beside its edge.','Probe the crown of the seated rear roller for C.','Across the crown, the shallowest reading is the top.','At each orange dot, touch the highest solid rib or','floor surface for F. Sweep between dots for higher','features. Record their positions too.'])
rect(38,449,715,83,'#F1F5F5','#C1D2D2');txt(51,471,'If the rod cannot reach',12,True)
para(51,491,['Place a narrow, square-ended block on that exact surface. Measure its height H with the outside jaws,',
'then probe the block top. Full depth = reading to block top + H. Use this only where the block sits flat and stable.'])
foot('Use light contact. Over an air opening, record OPEN and measure the nearest solid lip. Keep the probe out of the dock.')
head('5 / 6','Check the opposite wall, spool and lid','These readings locate the spool relative to the stationary shell and check the room above a loaded spool.')
txt(38,141,'C   Rear wall at spool-center height',15,True)
# rear wall at left; roller and tangent straightedge kept vertical
rect(57,161,7,153,'#A8B9BE');line(64,313,308,313,grey,2);circle(211,285,15,'#CCD8DA');rect(192,163,4,138,'#A9CDC3',green)
ar(64,191,192,191);txt(86,183,'inside jaws',10,True,orange);line(65,191,65,209,blue,2);line(191,191,191,209,blue,2);line(65,205,191,205,blue,2);txt(214,173,'Straightedge',10,True,green);line(211,177,196,182,green)
txt(215,292,'rear roller',10,True);txt(74,237,'Rear wall',10,True)
para(38,340,['Hold a thin straightedge vertical against the rear-facing','tangent of the roller. At about 95 mm above its axle,','measure gap W from the rear wall to that tangent face.','If your jaw touches the opposite face of the straightedge,','subtract its thickness. Wall-to-axis distance = W + D/2.',
'Repeat near each flange if the wall is curved or ribbed.'])
txt(407,141,'D   Spool rise and lid depth',15,True)
# section showing side rim, spool and bridge hovering above using blocks
for x in [418,690]:rect(x,232,20,42,'#C1CDCF');rect(x,193,20,39,'#DFE6E6')
rect(418,184,292,9,'#ACD1C7',green)
p=c.beginPath();p.moveTo(451,612-276);p.curveTo(484,612-197,642,612-197,680,612-276);c.setStrokeColor(HexColor('#91663D'));c.setLineWidth(2);c.drawPath(p)
line(435,232,692,232,grey,1,[3,3]);ar(552,184,552,217);txt(561,208,'P',11,True,orange);ar(680,184,680,232);txt(655,221,'B',11,True,orange);txt(456,298,'Hard rim reference',10,True);line(492,286,476,232,grey,.8)
para(407,340,['Seat your largest spool on the factory rollers. Raise','the bridge on two equal blocks and measure B from','its top to the hard rim. Probe the highest flange for P.','Spool rise above that rim = B − P. Rotate and repeat.',
'Invert the lid. Bridge the matching hard seating plane','and probe the inside roof above each flange. Subtract','bridge thickness for lid depth L. Record any gasket','offset or uncertainty at the seam.'])
# Inverted lid cross-section and the actual depth-rod contact.
line(55,453,73,453,ink,2);line(73,453,84,479,ink,2);line(84,479,167,479,ink,2);line(167,479,179,453,ink,2);line(179,453,192,453,ink,2)
rect(55,447,138,6,'#ACD1C7',green);rect(121,434,9,13,'#A0BAC3',blue);line(130,447,130,479,blue,1.5);circle(130,479,2,orange,orange)
txt(205,456,'Lid upside down',10,True);txt(205,472,'Probe beside bridge to inner roof.',9)
txt(38,503,'Spool dimensions',12,True);para(38,523,['Measure outside flange-to-flange width with the large jaws. For a spool wider in diameter than the jaw capacity,',
'wrap a paper strip once around a round flange, mark the overlap, and divide the measured strip length by 3.142.'])
foot('With matching seating planes, nominal top gap = L − (B − P). The factory roller result provides a baseline for the new pose.')
head('6 / 6','Record your readings','Use the station labels from page 3. Keep the same left/right orientation and bridge for the whole grid.')
txt(39,140,'Roller and reference',15,True);txt(39,169,'Roller diameter D    left ________    right ________        Bridge top to roller crown C ________ mm',12)
txt(39,192,'Rear-axis depth from bridge top = C + D/2.     Bridge thickness ________ mm',11,color=grey)
txt(39,226,'Bridge top to highest floor or rib, F (mm)',14,True)
xs=[39,238,360,482,604,752];ys=[241,272,303,334,365,396]
for i,(a,b) in enumerate(zip(ys,ys[1:])):
 rect(39,a,713,b-a,'#E6F1F0' if i==0 else '#FFFFFF','#C4D1D3')
 for x in xs[1:-1]:line(x,a,x,b,'#BCCED0',.6)
 if i==0:
  for x,s in zip(xs,['Forward of rear axle','L 42','L 13.5','R 13.5','R 42']):txt(x+8,a+20,s,11,True)
 else:txt(49,a+20,['117 mm','129 mm','136 mm','145 mm'][i-1],12)
txt(39,419,'Highest extra feature    station ________    lateral offset ________    F ________    type __________________',11)
txt(39,446,'Rear-wall gap W    left ________    right ________        Spool diameter ________    width ________ mm',11)
txt(39,473,'Raised bridge B ________    crown depth P ________    lid depth L    left ________    right ________ mm',11)
txt(39,507,'Return the raw readings',13,True,green);para(39,528,['A photo looking down at the marked stations and a side photo of the rib that gave the shallowest F will help identify it.'])
foot('For a common bridge datum, floor distance below the rear axle = F − (C + D/2). A smaller value means less wheel clearance.')
c.save()
base=D/'Start-here-Fit-check.pdf'
orig=Path('guide-original.pdf')
if not orig.exists():orig.write_bytes(base.read_bytes())
w=PdfWriter()
for fname in [orig,'caliper-pages.pdf']:w.append(str(fname))
with base.open('wb') as f:w.write(f)
