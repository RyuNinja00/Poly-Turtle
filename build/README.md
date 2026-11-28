# Reproduce the fit study

The published geometry and guide are ready to open. These Python sources preserve the generation and measurement methods. Run commands from a clean copy of this directory. The scripts use relative paths. Re-running extraction in a populated directory can suffix duplicate donor part names.

1. Install the Python packages in requirements.txt (Python 3.12 was used) and create a directory named pkg.
2. Download CAD/Cad.zip from ArmoredTurtle/BoxTurtle at commit 101a580c238fc8c52d3bc1f0ea8c3f779cb2d065. Extract Cad/BoxTurtle.step as v10.step. At commit ad3cd010009d54c8c969a0dc94fbdcfc25320ded, extract BT_V1.1_release.step from CAD/Cad.zip as v11.step.
3. Run python download.py for the three Printables geometry inputs. For manual download, use lid interior STEP from model 1747851 (save as 7280858.geom), Box.stl from model 872878 (3689772.geom), and the two-port lid STL from model 1441905 (6064460.geom).
4. Run python extract.py v10 and python extract.py v11. Run python design.py, then python assemble.py.
5. Run python sheet.py for the overview and scale drawing, then python calipers.py to append the measurement pages. Run python qa.py for sampled checks of the raised feeder and the lower components against the reference meshes.

The saved model poses are defined in design.py and assemble.py. Surface sampling is an approximation. The archived CAD results, findings and worksheet are the reference snapshot for the current revision.

## Printed lid (cad/08)

`build/lid/` builds the one-piece rev 3 lid without a CAD kernel:

- `cliplid.py` and `earcut.py` clip jojo's lid exactly at Z 102 and cap the cut; the old outlet hole is closed.
- `pose.py` and `search.py` choose the uphill feeder pose.
- `printed_lid.py` builds the canopy from heightmaps:
  - a 45° vault plus a 45° feeder frustum;
  - jojo's end caps from exact z-intervals (`columns.py`);
  - features and the feeder carrier as signed-distance fields;
  - meshes everything with marching cubes at 0.4 mm.
- `extras.py` builds exact small parts: the threaded outlet bushing, the TPU rim gaskets (from jojo's channel), the Micro-Fit plate and gaskets.
- `decimate.py` collapses flat regions within 0.01 mm.
- `occ.py` builds the base occupancy grid.
- `checks.py` checks clearances, drop-in, inlet routing and rim-down overhangs, then packs `cad/08-Printed-lid.zip`.
- `verify.py` and `verify_endcaps.py` re-measure the final STLs.
- `render.py` draws `docs/printed-lid.png`.

Run `clouds.py` first; it needs the restored cad/01. See [docs/printed-lid.md](../docs/printed-lid.md).

## Cradle-drive STEP (cad/07)

`python3 build/cradle-drive/make_step.py [out.step]` writes the assembly STEP (default `cad/07-Cradle-drive-layout.step`; zip it to publish). It poses the Smol, LOAD, PREP and the filament paths from `cad/08-printed-lid/mesh-report.json`, so rebuild the lid first. `verify_step.py <file.step>` checks it.

## Whole-assembly audit

`build/audit/` re-checks the published STLs together, in the model frame:
- `assembly.py`: interference and gaps between every pair (lid, carrier, drive parts, gaskets, Micro-Fit plate and housing, PC4-M10 envelope, spool) → `assembly.json`;
- `thin.py`: walls thinner than about two nozzle widths → `thin.json`;
- `pogo_check.py`: the N20 pogo disconnect (lid pocket, print-in-place box part, bumpers, connectors) against the lid, carrier, spool, box proxy and filament paths → `pogo.json`;
- `supports.py STL up-axis [voxel]`: regions that start in mid-air or overhang past 45° in a print orientation, e.g. `supports.py ../../cad/08-printed-lid/08c-feeder-carrier.stl +y`.
