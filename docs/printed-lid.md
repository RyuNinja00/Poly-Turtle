# 08 Printed lid (rev 3: one piece, no supports)

**The conversion needs a printed lid.** The Smol feeder (with LOAD) and the PREP switch sit above the top of the box, so the stock lid can't close over them. The base of this lid is jojo's two-port **Printed Lid for Polydryer Box** ([Printables 1441905](https://www.printables.com/model/1441905), CC BY-NC-SA, based on work by Extrutim and Cipism).

**Revisions:**
- **Rev 1** turned the cad/05 clearance shell into separate printable parts.
- **Rev 2** turned the feeder so filament travels uphill.
- **Rev 3** keeps that layout and makes the lid **one print with no supports**. It also gives the lid a single design language: 45° facets everywhere. Rev 2's flat plate and box hood could only be printed as two bonded parts, or as one part with a lot of support.

![08 printed lid overview](printed-lid.png)

## How it prints in one piece

Print it **rim down** on the bed. In that orientation every downward-facing surface is one of three things:
- a 45° facet;
- one of two short bridges: the 37 mm vault top and the 25 mm canopy top;
- one of jojo's own small bridges, for example the 6 mm gasket channel.

| Region | What it is |
|---|---|
| Below Z 102 | jojo's lid, **triangle for triangle**: rim, gasket channel, side latches. The old 4.3 mm outlet hole is closed. |
| End caps above Z 102 | Rebuilt from jojo's own geometry, exact in Z: the latch bars and finger slots. Jojo's −X port is filled. |
| Vault (between the end caps) | The flat plate is replaced by 45° chamfers rising from the walls at Z 105.5 to a 37 mm wide flat at Z 128 (inside). There is 1.75 mm of headroom over a full Ø205 spool (jojo's plate gave 1.36). |
| Feeder canopy | A 45° frustum over the feeder, inner top Z 157. The feeder is re-posed to **45°**, so its top face and outlet face are parallel to the canopy faces. |
| Shadow line | A small V-groove runs around the canopy just above Z 102. It turns the base/canopy join into a deliberate detail. |

The lid is 100.3 mm tall overall. Print it in ASA with a brim. The bed contact is jojo's rim and gasket-channel walls. A few jojo ledges sit 0.2–1.5 mm above the bed; they are under 1.1 mm wide and print as short overhangs.

## Files

[`cad/08-Printed-lid.zip`](../cad/08-Printed-lid.zip) contains these files. All are in the cad/01 / cad/05 model frame (Z up, mm).

| File | Part |
|---|---|
| `08-Printed-lid.stl` | The lid. It is two touching shells in one file: jojo's exact base and the canopy. Every slicer merges them into one solid. |
| `08c-feeder-carrier.stl` | Sits under the Smol and replaces the BoxTurtle trayframe interface. It carries the two V1 heat-set inserts for the Smol's downward bolts, the PREP block (2 × M2 pilots, Ø1.7), the curved inlet guide (R20, 40°, Ø2.4 bore, flared mouth), and two wall inserts (−Y). Print it on its flat −Y face, no supports. |
| `checks.json`, `mesh-report.json` | Check and mesh results. |

## Lid features

- **Outlet:** a PC4-M10 fitting screws into a Ø9 boss on the canopy's −X face. The fitting cuts its own thread over 8.7 mm. The face is square to the filament axis, so the PTFE leaves the Smol in a straight line.
- **Wiring:** one M12 / PG7 gland, vertical, through the vault top at X −20. LOAD, PREP and the N20 leads all leave here. Fit plugs inside so the lid can come off.
- **Feeder mounting:** 2 × M3 through the −Y wall at (X 47.4, Z 111.3) and (X 29.1, Z 129.7). Each passes through a printed standoff and threads into an insert in the carrier rail. Use a washer and a dab of sealant under each head.

## Assembly

1. **Inserts.** Press V1 M3 heat-set inserts into the carrier: two in the rail top (A, B) and two in its −Y face.
2. **Bench-build the module.**
   - Thread the Smol's two downward M3 bolts (the old trayframe bolts) into the rail inserts. A Ø3.2 relief under each insert takes the existing bolt tails.
   - Screw the D2F PREP switch to its block with 2 × M2 self-tapping screws from below.
   - Push filament through the guide, under the lever and into the Smol. It should run without catching.
3. **Install.** Turn the lid upside down and lower the module straight in through the rim. The checks confirm the whole move is clear (minimum 0.25 mm). Screw the two −Y wall screws in.
4. **Outlet and wiring.** Fit the PC4-M10 and the PTFE to the hub. Route the leads to the gland.
5. **Spool.** Load it so filament pays out **up the +X side**, toward the guide. The cradle drive is unchanged and rewinds in the opposite direction.

**Service:** remove the two wall screws and the whole feeder module, PREP included, lifts out through the rim.

## Checks (`build/lid/checks.py`, values from `checks.json`)

Clearances are sampled from vertices and small circles of the cad/01 reference parts, moved into the rev 3 pose. They are not exact solids.

| Check | Result |
|---|---|
| Meshes | Base, canopy and carrier are each closed; every edge is shared by exactly 2 faces |
| Lid to Smol | 1.47 mm |
| Lid to carrier | 0.25 mm (the carrier face against the wall standoffs) |
| Carrier to Smol, excluding the replaced trayframe interface | 0.46 mm, at the rail top where the Smol's base sits |
| Carrier to PREP | 0.20 mm (the switch face sits on the block) |
| Lid to spool (Ø205 × 78) | 1.75 mm |
| Feeder module to spool | 3.67 mm |
| Drop-in: module lowered straight down past the rim in 2 mm steps | 0 points inside the lid; minimum 0.25 mm |
| Outlet axis vs. its face normal | 0.0° |

**Downward-facing area, rim down** (canopy / jojo base):

| Overhang | Canopy | Jojo base |
|---|---|---|
| 45–50° | 16,753 mm² | 1,885 mm² |
| 50–80° | 225 mm² | 163 mm² |
| Horizontal | 4,367 mm² | 7,388 mm² |

The horizontal canopy ceilings are the 37 mm vault flat, the 25 mm canopy top, and jojo's 10 mm end-slot ceilings.

**Inlet routing.** Free filament runs from the +X side of the spool into the guide mouth:

| Spool radius | Turn at the guide mouth |
|---|---|
| 102.5 (full) | 1.5° |
| 80 | 20.0° |
| 60 | 32.7° |
| 45 (near empty) | 41.2° |

After the mouth, the guide adds a smooth 40° turn at R20. The path stays at least 1.6 mm from the carrier at every spool size.

## Verify on the box

- **Guide mouth.** The guide hangs to Z 59 (model frame), 1.2 mm below the lid's rim plane and just inside the box's +X end wall, at X 92. With the lid closed, check that the box's +X end wall and its seating lip leave at least 2 mm at that point.
- **Payout strip.** A full spool pays out close to the +X wall (X 96 at the spool's equator). Keep that strip free of desiccant or plugs.
- **Bench test.** Bench-feed the module before the first full run, and watch for drag on a near-empty spool.

## Parameters and rebuild

- **Pose:** `build/lid/pose.py`, with `ALPHA = 45` and `INLET` set in `printed_lid.py`. `search.py` reproduces the pose search.
- **Shape:** `ZC`, `Z_WALL`, `VAULT_IN` and `FRUSTUM` set the shape. `FRUSTUM` is the smallest 45° frustum that clears the module by 1.5 mm.
- **Features:** carrier and outlet features are defined in the feeder's own frame, so they follow the pose.

```
cd build/lid
python3 clouds.py        # Smol / PREP reference clouds (needs cad/01: python transport/restore.py)
python3 printed_lid.py   # lid (jojo base + canopy, marching cubes 0.4 mm) and carrier
python3 occ.py           # base occupancy grid for the checks
python3 checks.py        # checks.json and cad/08-Printed-lid.zip
python3 render.py        # docs/printed-lid.png
```

Each derivative file keeps jojo's CC BY-NC-SA license and attribution.
