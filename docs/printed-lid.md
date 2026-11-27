# 08 Printed lid (rev 3.2: one piece, no supports)

**The conversion needs a printed lid.** The Smol feeder (with LOAD) and the PREP switch sit above the top of the box, so the stock lid can't close over them. The base of this lid is jojo's two-port **Printed Lid for Polydryer Box** ([Printables 1441905](https://www.printables.com/model/1441905), CC BY-NC-SA, based on work by Extrutim and Cipism).

**Revisions:**
- **Rev 1** turned the cad/05 clearance shell into separate printable parts.
- **Rev 2** turned the feeder so filament travels uphill.
- **Rev 3** keeps that layout and makes the lid **one print with no supports**. It also gives the lid a single design language: 45° facets everywhere. Rev 2's flat plate and box hood could only be printed as two bonded parts, or as one part with a lot of support.
- **Rev 3.1** adds:
  - a printed M10×1 outlet thread with an O-ring / TPU-washer seat;
  - a PTFE-lined inlet guide;
  - a Micro-Fit 3.0 2×6 bulkhead in place of the cable gland;
  - a printable TPU lid-to-box gasket.

  It also cuts the lid STL from 56 MB to under 8 MB.
- **Rev 3.2** is the whole-assembly audit (see *Whole-assembly audit* below): a thicker +X end wall, an outlet counterbore that leaves the thread whole, a collar and a print fin on the inlet guide, and a 45° underside on the +X canopy strip.

![08 printed lid overview](printed-lid.png)

## How it prints in one piece

Print it **rim down** on the bed. In that orientation every downward-facing surface is one of three things:
- a 45° facet;
- one of two short bridges: the 36 mm vault top and the 25 mm canopy top;
- one of jojo's own small bridges, for example the 6 mm gasket channel.

| Region | What it is |
|---|---|
| Below Z 102 | jojo's lid, **triangle for triangle**: rim, gasket channel, side latches. The old 4.3 mm outlet hole is closed. |
| End caps above Z 102 | Rebuilt from jojo's own geometry, exact in Z: the latch bars and finger slots. Jojo's −X port is filled. |
| Vault (between the end caps) | The flat plate is replaced by 45° chamfers rising from the walls at Z 106.5 to a 36 mm wide flat at Z 129 (inside). There is 1.6 mm of headroom over a full Ø205 spool, measured on the final mesh (jojo's plate gave 1.36). |
| Feeder canopy | A 45° frustum over the feeder, inner top Z 158.5, at least 2.1 mm from the Smol. The feeder is re-posed to **45°**, so its top face and outlet face are parallel to the canopy faces. |
| Shadow line | A small V-groove runs around the canopy just above Z 102. It turns the base/canopy join into a deliberate detail. |

The lid is 101.8 mm tall overall. Print it in ASA with a brim. The bed contact is jojo's rim and gasket-channel walls. A few jojo ledges sit 0.2–1.5 mm above the bed; they are under 1.1 mm wide and print as short overhangs.

## Files

[`cad/08-Printed-lid.zip`](../cad/08-Printed-lid.zip) contains these files. All are in the cad/01 / cad/05 model frame (Z up, mm).

| File | Part |
|---|---|
| `08-Printed-lid.stl` | The lid. It is three touching shells in one file: jojo's exact base, the canopy, and the threaded outlet bushing. Every slicer merges them into one solid. Size: 7.7 MB, 154k triangles. Flat areas were decimated within 0.01 mm. |
| `08c-feeder-carrier.stl` | Sits under the Smol and replaces the BoxTurtle trayframe interface. It carries the two V1 heat-set inserts for the Smol's downward bolts, the PREP block (2 × M2 pilots, Ø1.7), the curved inlet guide (R20, 40°, Ø4.3 bore for a 4 × 2 mm PTFE liner, flared mouth with a Ø9.2 collar), and two wall inserts (−Y). Print it on its flat −Y face, no supports: a fin under the guide holds it up while printing. |
| `08g-TPU-lid-gasket-2.5mm.stl` / `-3.5mm` / `-4.5mm` | Lid-to-box seal. A hollow TPU ring (0.8 mm walls) that snaps into jojo's rim channel. Choose the height as described under *Lid-to-box seal*. Print flat, in TPU 85A–95A. |
| `08h-TPU-outlet-washer.stl` | Optional printed seal under the PC4-M10 hex, in place of a 10 × 1 mm O-ring. Print in TPU. |
| `08m-microfit-2x6-plate.stl` | 2 mm bulkhead plate for a Micro-Fit 3.0 2 × 6 housing with panel-mount ears (Molex 43020-1200, or the seller's "5557-3.0-2*R"). Cutout after Wireheadarts' Micro-Fit library (Printables 1300761). Print in ASA. |
| `08n-TPU-microfit-plate-gasket.stl` | 1 mm TPU gasket under the plate. |
| `checks.json`, `verify.json`, `verify-endcaps.txt`, `mesh-report.json` | Check, final-mesh verification and mesh results. |

## Lid features

- **Outlet:** a printed **M10 × 1** internal thread (PC4-M10 is M10 × 1) in a bushing on the canopy's −X face.
  - It has 7.5 mm of thread, sized major Ø10.3 / minor Ø9.1 for printing.
  - The face has a Ø12.6 × 0.8 mm counterbore round the thread for a **10 × 1 mm O-ring** (about 0.2 mm squeeze) or the printed TPU washer (ID 10.3, OD 12.3, 1.2 thick, so it stands 0.4 proud). A 0.9 mm lip is left round the counterbore, backed by the boss.
  - The thread axis is the filament axis, square to the 45° face.
  - Printed at 45° the thread comes out a little rough. Screw the fitting in by hand, or chase it once with an M10 × 1 tap.
- **Wiring:** a Molex **Micro-Fit 3.0 2 × 6** bulkhead on the vault top at X −20, which replaces the gland.
  - **Which half goes where.** Sellers' names for the two halves are reversed from what you might expect:
    - The **lid** takes the 2 × 6 housing with the barbed ears and **male pins**: the seller's "5557-3.0-2*R (母壳, female shell)", the same as Molex 43020-1200 (pins 43031).
    - The **cable** gets the 2 × 6 housing with the **female 43030 terminals**: the seller's "5557-3.0-2*P (公壳, male shell)", the same as Molex 43025-1200.
  - The plate sits on a 1 mm TPU gasket over a 25 × 13.5 opening and is held by 2 × M3 × 10 with nuts inside.
  - With 12 circuits there is room for the N20 (2), LOAD (2–3), PREP (2) and spares.
  - The N20 lives in the box, not on the lid. Put a small 2-pin inline connector (Micro-Fit 2-pin, JST-PH or similar) in its leads inside the box, so the lid can be lifted off without a cable tying it to the box.
  - **The cutout shape** follows Wireheadarts' *OpenSCAD library for mounting Molex MicroFit 3.0 panel-mount plugs* (Printables 1300761). It has three parts:
    - a body opening;
    - a full-length slot so the snap ears can pass and spring back;
    - a 3.18 mm notch for the latch.

| Size | Seller's drawing, 2 × 6 R housing | Plate cutout |
|---|---|---|
| Body length B | 19.00 ± 0.25 | 19.45 (0.1 per side over the 19.25 maximum) |
| Body across both rows | 7.00 | 7.31 |
| Across rows, latch included | 8.50 | 8.61 |
| Ear span | not given; Molex is 22.89 | slot 22.99 × 3.15 |

  - The library's single-row figures (4.21 / 5.51) plus one 3.00 mm row pitch give 7.21 / 8.51. The seller's 2 × 6 drawing (7.00 / 8.50) confirms that extrapolation.
  - The plate is 2.0 mm thick, inside the 1.57–2.30 mm panel range the library is designed for.
  - The seller doesn't give the ear span, so print the plate first (a few minutes) and press a housing in. Both ears should click and it shouldn't wobble. If it's off, change `MF` in `extras.py`; only the plate needs reprinting.
- **Feeder mounting:** 2 × **M3 × 12** through the −Y wall at (X 47.4, Z 111.3) and (X 29.1, Z 129.7). Each passes through a printed standoff and threads into an insert in the carrier rail, with 4.5 mm of thread engaged. The standoffs stop 0.6 mm short of the carrier so it slides in freely; tightening the screws closes that gap. Use a washer and a dab of sealant under each head. The screw tips stay at least 2.8 mm from the Smol.

## Assembly

1. **Inserts.** Press V1 M3 heat-set inserts into the carrier: two in the rail top (A, B) and two in its −Y face.
2. **Bench-build the module.**
   - Push a 4 × 2 mm PTFE tube into the guide from the mouth until it stops at the shoulder (about 15 mm). Trim it flush with the mouth.
   - Thread the Smol's two downward M3 bolts (the old trayframe bolts) into the rail inserts. A Ø3.2 relief under each insert takes the existing bolt tails.
   - Screw the D2F PREP switch to its block with 2 × M2 self-tapping screws from below.
   - Push filament through the guide, under the lever and into the Smol. It should run without catching.
3. **Install.** Turn the lid upside down and lower the module straight in through the rim. The whole move is clear by at least 0.63 mm. Screw the two −Y wall screws in.
4. **Outlet and wiring.**
   - Drop a 10 × 1 O-ring (or the TPU washer) into the outlet counterbore and screw in the PC4-M10. Run the PTFE to the hub.
   - Crimp the lane leads into the 43020-1200 housing and snap it into the plate. Join the N20 leads through their inline 2-pin connector.
   - Fit the plate with its gasket: 2 × M3 × 10 with nuts inside.
5. **Seal.** Press the chosen TPU gasket into the rim channel (see below).
6. **Spool.** Load it so filament pays out **up the +X side**, toward the guide. The cradle drive is unchanged and rewinds in the opposite direction.

**Service:** unplug the N20's inline connector, remove the two wall screws and the whole feeder module, PREP included, lifts out through the rim.

## Lid-to-box seal

Jojo's lid seals on the box rim through a channel round the rim. The channel is about 5.6 mm wide at the mouth, 6.0 mm wide under its ceiling at Z 65.2, and 5 mm deep. The `08g` gaskets are a **hollow TPU box section** shaped to that channel:
- 5.76 mm wide. The channel walls have about 4° of draft, so the gasket clears them by 0.1 mm at the ceiling and is a 0.1 mm-per-side press fit at the mouth, which holds it in;
- 0.8 mm walls;
- an enclosed void, so it compresses without needing very soft TPU.

The box proxy is not reliable enough to give how far the real box rim reaches into the channel, so pick the height from a quick test:

1. Put three pea-sized balls of modelling clay or Blu-Tack on the box rim: one in the middle of each long side and one at an end.
2. Close the lid (no gasket) and latch it, then open it again.
3. Measure the squashed thickness **G**. This is the gap between the rim top and the channel ceiling.
4. Choose the gasket closest to **G + 1 mm**: 2.5, 3.5 or 4.5. That gives about 1 mm of squeeze.

If G is outside 1.5–3.5 mm, change `GASKET_HEIGHTS` in `extras.py` and rebuild. Print the gasket flat in TPU 85A–95A, then press it in from the rim side, working round from a corner. If your box came with its stock silicone gasket and that fits jojo's channel, it works just as well.

## Checks

Two independent passes:
- `checks.py` checks against the design fields during the build.
- `verify.py` and `verify_endcaps.py` re-measure the **final STLs** (column resolution 0.25 mm). They use exact Z-intervals along 0.25 mm columns and nearest-vertex distances, and also test against the printable box proxy (cad/04) with the lid closed.

The table gives the final-mesh values (`verify.json`). Smol and PREP are sampled from the cad/01 reference parts, so treat ~0.5 mm as the reading error.

| Check | Final mesh |
|---|---|
| Shells | Base, canopy, outlet bushing and carrier are each closed. Welded exactly as float32 (as a slicer reads the STL), every edge is shared by exactly 2 faces with no collapsed triangles. |
| Lid to Smol | 2.13 mm |
| Lid to carrier | 0.66 mm (wall standoffs, 0.6 mm by design) |
| Carrier to Smol, excluding the replaced trayframe interface | 0.51 mm, at the rail top where the Smol's base sits |
| Carrier to PREP | 0.20 mm (the switch face sits on its block) |
| Lid to Ø205 × 78 spool | 1.62 mm (jojo's own side wall beside the flange is about the same) |
| Feeder module to spool | 3.67 mm |
| Module, PREP, guide to box proxy (lid closed) | ≥ 8.0 mm (the guide's print fin, at the −Y side); nothing inside the box walls |
| Drop-in: module lowered straight down past the rim in 1 mm steps | 0 points inside the lid; minimum 0.63 mm |
| Filament path: guide bore, PREP lever zone, Smol, outlet bore | Clear of the carrier and the lid. The guide bore measures Ø4.24 at its narrowest on the final mesh, so a Ø4.0 liner fits with 0.12 mm all round. |
| Smol bolt tails A, B | Pass the carrier inserts and reliefs (Ø3.2 relief measures Ø3.14 on the mesh, Ø4.2 insert holes Ø4.16) |
| Outlet | Bore clear past Ø8.8. The M10 × 1 thread is present over 7.5 mm (15 crest/root crossings on a probe line). The Smol's outlet end is 6.4 mm short of the fitting tip. |
| Micro-Fit plate | 25 × 13.5 opening and both screw holes clear. The seat is flat (Z 132.54 under the whole plate) on a 3.5 mm roof. There are 24 mm from the underside of the roof to the spool for the housing and wires, and the module is more than 20 mm away. |
| Wall screws | Holes clear; standoffs and insert walls solid all round; M3 × 12 tips ≥ 2.8 mm from the Smol |
| End caps vs jojo (Z 102–111.6) | Every difference is within 2 samples (0.5 mm) of jojo's surface, except the two intended changes: the filled −X port and the canopy wall over the +X bar. Both finger slots stay as jojo made them. |
| Base/canopy seam | All 174 sampled wall columns continue through Z 102. At the two +X corner columns the shadow line cuts in to 0.6 mm from the column, as drawn. |

**Fixes made during this double-check:**
- **STL welding:** the lid STL had 32,586 triangles that collapsed when welded as float32. Marching cubes put vertices on grid nodes; the build now keeps the field off the nodes and welds in float32.
- **Canopy clearance:** the canopy was raised 1.5 mm. It was 1.05 mm from the Smol on the final mesh.
- **Vault clearance:** the vault chamfers start 1 mm higher. The spool headroom was 1.41 mm.
- **Drop-in gap:** the standoff gap was opened from 0.25 to 0.6 mm, so the module doesn't scrape as it goes in.

Six zero-area slivers remain: one is in jojo's original mesh, four come from the cap triangulation and one is in the canopy. They are valid topology, and slicers drop them.

**Downward-facing area, rim down** (canopy / jojo base):

| Overhang | Canopy | Jojo base |
|---|---|---|
| 45–50° | 16,528 mm² | 1,942 mm² |
| 50–80° | 315 mm² (includes the thread flanks) | 163 mm² |
| Horizontal | 4,102 mm² | 7,388 mm² |

The horizontal canopy ceilings are the 36 mm vault flat, the 25 mm canopy top, and jojo's 10 mm end-slot ceilings.

**Inlet routing.** Free filament runs from the +X side of the spool into the guide mouth:

| Spool radius | Turn at the guide mouth |
|---|---|
| 102.5 (full) | 1.5° |
| 80 | 20.0° |
| 60 | 32.7° |
| 45 (near empty) | 41.2° |

After the mouth, the guide adds a smooth 40° turn at R20. The straight-line path stays at least 1.0 mm from the carrier at every spool size (0.97 mm at 45 mm radius, where it enters past the collar's flared lip).

## Whole-assembly audit (rev 3.2)

A last pass checked every part against every other: `build/audit/assembly.py` (interference between all lid, carrier, drive, gasket, plate, connector and fitting parts in one frame), `build/audit/thin.py` (walls thinner than the nozzle can print), `build/audit/supports.py` (anything that starts in mid-air or overhangs past 45° in the print orientation) and a mesh scan of every STL. Results are in `build/audit/assembly.json` and `thin.json`.

**Found and fixed:**
- **+X canopy end wall** came out 0.7–0.9 mm thick over the latch bar. The canopy now stops at X 97.4 inside and drops as a full wall over the bar.
- **Outlet face groove** cut into the thread crests (groove ID Ø10.2 under the Ø10.3 thread major). It is now a Ø12.6 × 0.8 counterbore outside the thread, and the washer was resized to match.
- **Guide mouth lip** was 0.8 mm thick at the flare. A Ø9.2 collar now surrounds the mouth.
- **Carrier print supports.** On its −Y print face the guide and the web started in mid-air, 26–36 mm above the bed (about 90 mm² unsupported). A 4 mm fin now runs under the guide from the print face to the tube, ending 1 mm outside the mouth, and the web is carried down to the print face. What is left is hole ceilings and a 3 mm overhang under the mouth collar.
- **+X canopy strip.** The new wall between the vault and the +X bar started flat at Z 101.4 over open space (3 mm wide, 112 mm²). Its underside is now a 45° chamfer up from the bar.
- **Motor bracket orientation.** Printed upside down as the guide said, its motor floor is a 12 mm one-sided overhang. The cradle-drive guide now says to print it on its flat +X end face, with one small support under the key tab.
- **Collapsed triangles** in the roller and pinion STLs (float32 rounding). `meshkit.write_stl` now welds as float32 and drops them, keeping the mesh closed.
- **Assembly STEP** still had the Smol, PREP and filament paths in the old pose. They now come from the rev 3 lid pose, so the STEP matches the lid.

**Checked, no change needed:**

| Pair | Result |
|---|---|
| Drive parts (roller, treads, pinion, bracket) vs lid and carrier | ≥ 133 mm apart |
| Treads vs spool flange | Touching (they drive it). Roller body 0.48 mm, pinion 1.65 mm from the flange circle |
| Bracket key tab vs box proxy | Overlaps the proxy's cradle post by up to 1.5 mm. The proxy is a different (printable) box; the tab was sized to the molded box's slot (S = 13.9–14.4) and the cradle-drive checks against that slot are all positive. Measure S before printing, as the cradle-drive guide says. |
| Lid rim vs box proxy | Overlaps at the rim only (the proxy rim is taller than the real one); this is why the gasket height is picked by the clay test |
| Installed gasket vs channel | Press fit of 0.1 mm per side at the drafted channel mouth, 0.1 mm clear at the ceiling |
| Micro-Fit plate, plate gasket | Seat flat on the Z 132.54 vault top |
| 2 × 6 housing (with ears) through the opening | 2.5 mm clear of the opening edges; 4.8 mm above a full spool with 10 mm of wire bend |
| PC4-M10 hex (14 AF) and body | Seat on the bushing face; nothing else within reach |
| Lid, rim down: overhangs left | Only the intended bridges (6 mm gasket channel, 36 mm vault flat, 25 mm canopy top, jojo's end-slot ceilings), jojo's own small ledges, the 9.2 mm plug over jojo's old −X port, and the tops of the horizontal screw holes |
| Thin features left | Thread crests, the 0.9 mm lip round the outlet counterbore (backed by the boss), the carrier's 2 mm webs, the 0.8 mm gasket walls and the 0.6 mm tread end lips, all by design |
| Meshes | Every STL is closed and manifold. The 07d bracket is 194k triangles (not decimated), which slicers handle fine |

## Verify on the box

- **Guide mouth.** The guide's mouth collar hangs to Z 57.2 (model frame), 3.0 mm below the lid's rim plane, and reaches X 97.2. The box wall enters jojo's channel at X 102.9, so there are about 5.7 mm in the model. With the lid closed, check that the box's +X end wall and any seating lip leave at least 2 mm at that point.
- **Payout strip.** A full spool pays out close to the +X wall (X 96 at the spool's equator). Keep that strip free of desiccant or plugs.
- **Bench test.** Bench-feed the module before the first full run, and watch for drag on a near-empty spool.

## Parameters and rebuild

- **Pose:** `build/lid/pose.py`, with `ALPHA = 45` and `INLET` set in `printed_lid.py`. `search.py` reproduces the pose search.
- **Shape:** `ZC`, `Z_WALL`, `VAULT_IN` and `FRUSTUM` set the shape. `FRUSTUM` is the smallest 45° frustum that clears the module by 1.5 mm.
- **Features:** carrier and outlet features are defined in the feeder's own frame, so they follow the pose.

```
cd build/lid
python3 clouds.py        # Smol / PREP reference clouds (needs cad/01: python transport/restore.py)
python3 printed_lid.py   # lid (jojo base + canopy + threaded bushing), carrier, gaskets, plate (~5 min)
python3 occ.py           # base occupancy grid for the checks
python3 checks.py        # design-field checks, checks.json and cad/08-Printed-lid.zip
python3 verify.py        # final-mesh re-measure -> verify.json (about 15 min)
python3 verify_endcaps.py
python3 render.py        # docs/printed-lid.png
```

Each derivative file keeps jojo's CC BY-NC-SA license and attribution.
