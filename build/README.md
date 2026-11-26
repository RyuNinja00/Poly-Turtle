# Reproduce the fit study

The published geometry and guide are ready to open. These Python sources preserve the generation and measurement methods. Run commands from a clean copy of this directory. The scripts use relative paths. Re-running extraction in a populated directory can suffix duplicate donor part names.

1. Install the Python packages in requirements.txt (Python 3.12 was used) and create a directory named pkg.
2. Download CAD/Cad.zip from ArmoredTurtle/BoxTurtle at commit 101a580c238fc8c52d3bc1f0ea8c3f779cb2d065. Extract Cad/BoxTurtle.step as v10.step. At commit ad3cd010009d54c8c969a0dc94fbdcfc25320ded, extract BT_V1.1_release.step from CAD/Cad.zip as v11.step.
3. Run python download.py for the three Printables geometry inputs. For manual download, use lid interior STEP from model 1747851 (save as 7280858.geom), Box.stl from model 872878 (3689772.geom), and the two-port lid STL from model 1441905 (6064460.geom).
4. Run python extract.py v10 and python extract.py v11. Run python design.py, then python assemble.py.
5. Run python sheet.py for the overview and scale drawing, then python calipers.py to append the measurement pages. Run python qa.py for sampled checks of the raised feeder and the lower components against the reference meshes.

The saved model poses are defined in design.py and assemble.py. Surface sampling is an approximation. The archived CAD results, findings and worksheet are the reference snapshot for the current revision.

## Printed lid (cad/08)

`build/lid/` turns `cad/05` into the printable rev 2 lid without a CAD kernel. It runs in this order:
- `cliplid.py` clips jojo's lid exactly at the plate top, caps it, and closes the old outlet hole.
- `pose.py` and `search.py` choose the uphill feeder pose.
- `printed_lid.py` builds the hood and the feeder carrier as signed-distance solids, meshed with marching cubes at 0.4 mm.
- `occ.py` builds the lid occupancy grid.
- `checks.py` checks clearances, inlet routing and drop-in, then packs `cad/08-Printed-lid.zip`.
- `render.py` draws `docs/printed-lid.png`.

Run `clouds.py` first; it needs the restored cad/01. See [docs/printed-lid.md](../docs/printed-lid.md).
