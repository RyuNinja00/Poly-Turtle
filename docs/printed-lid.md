# 08 Printed lid (rev 1)

**Yes, the conversion needs a printed lid.** The Smol feeder (with LOAD) and the PREP switch stand 35.4 mm above the top of the box, and the stock-lid trial (`cad/03`) has hardware outside the stock lid's free volume. The printed lid is jojo's two-port **Printed Lid for Polydryer Box** ([Printables 1441905](https://www.printables.com/model/1441905), CC BY-NC-SA, based on work by Extrutim and Cipism). The old `cad/05` clearance shell was already this lid with a capped box glued on top. Rev 1 turns that shell into a lid you can print and assemble.

![08 printed lid overview](printed-lid.png)

Files: [`cad/08-Printed-lid.zip`](../cad/08-Printed-lid.zip) contains the STLs, `checks.json` and `mesh-report.json`. Everything is in the cad/01 and cad/05 model frame (Z up, mm).

| File | Part | Print |
|---|---|---|
| `08a-lid-body.stl` | jojo lid. The cad/05 pocket is clipped flush with the flat top of the plate, which leaves a 95 × 71 mm opening. The rim, gasket channel, latches, ports and the 4.3 mm outlet hole are jojo's original triangles; nothing was re-meshed. | Top face down, as jojo intended |
| `08b-hood.stl` | Feeder hood. Same outside envelope as cad/05, so all the earlier clearance results still apply. Holds the PREP block, the gland hole, the two roof screw holes and four locating tabs. | Roof down |
| `08c-feeder-carrier.stl` | Takes the place of the BoxTurtle trayframe interface under the Smol. Rail with two heat-set inserts and two towers that hang it from the hood roof. | On its flat +Y face |
| `08-Printed-lid-one-piece.stl` | 08a + 08b as two touching shells that the slicer merges. Use this instead of 08a + 08b if you would rather print one part with supports under the lid plate than bond two parts. | Roof down, tree supports under the plate |

All three parts print without supports. ASA is recommended for dryer temperatures.

## Assembly

1. **Bond 08b to 08a.** The hood's 2.5 mm wall sits on the matching ring around the opening, and four tabs drop 3 mm into the opening to locate it. Use an ASA acetone weld, or epoxy for other materials. This joint is permanent and is part of the seal.
2. **Inserts.** Press two V1 M3 heat-set inserts (Ø4.2 × 5.5 holes) into the carrier rail at A and B, and two more into the tower tops.
3. **Smol to carrier.** The Smol's two M3 bolts that originally went down into the trayframe thread into the rail inserts. Below each insert, a Ø3.4 relief lets the existing 13.6 mm tails pass, so the original bolts can be reused.
4. **PREP.** Mount the D2F-type switch to the hood block with 2 × M2 self-tapping screws from below (Ø1.7 pilots, lever toward the filament). Do this before the feeder goes in.
5. **Feeder in.** With the lid upside down, lower the carrier and Smol straight through the opening. Fasten it with 2 × M3 × 10 screws through the roof into the tower inserts. Use a washer and a dab of sealant under each head.
6. **Wiring.** LOAD, PREP and the N20 leads leave through one M12 / PG7 cable gland in the −X end wall (Ø12.4 hole). Fit a 2-pin plug inside for the N20 so the lid can come off.
7. **Outlet.** PTFE (4 mm OD) runs through the 4.3 mm hole in jojo's +X end wall, as before.

**Service:** removing the two roof screws drops the carrier and Smol out as one unit.

## Checks (`build/lid/checks.py`)

All clearances are sampled from vertices and small circles of the cad/01 reference parts, not from exact solids.

| Check | Result |
|---|---|
| Meshes 08a / 08b / 08c | closed, every edge shared by exactly 2 faces |
| Hood to Smol | 2.39 mm |
| Hood block to PREP | 0.20 mm (switch face; the switch is screwed to it) |
| Carrier to Smol, excluding the replaced trayframe interface | 0.46 mm (rail top at the Smol base, the bearing face) |
| Carrier to hood | 0.30 mm (tower tops under the roof) |
| Hood / carrier to Ø205 spool envelope | 3.47 / 4.27 mm |
| Hood tabs and carrier inside jojo's solid | 0 vertices |
| Carrier + Smol footprint vs opening | x 16.6–99.0, y −35.8–31.0 inside 4.5–99.5 × −39.5–31.5: drops in vertically |

## Open item: getting filament from the spool into PREP

The archived pose (cad/01, unchanged since the fit study) puts the PREP switch and the Smol inlet at the **high −X end** of a feeder axis tilted 25° downward toward +X. The inlet point is about 1 mm inside the hood's −X wall. Filament coming up from the spool has to enter the hood through the opening (x ≥ 4.5 below the plate), so it arrives almost vertically. It then has to turn about **110°** onto the feeder axis within a few millimetres. That turn is too tight for 1.75 mm filament (PLA especially), so rev 1 does not include an inlet guide, and the fit study only ever claimed straight centreline stubs. Options, in order of preference:

1. **Re-pose the feeder so filament travels uphill through it.** The inlet becomes the low end and filament comes up from the spool with a gentle bend. The hood probably has to get taller to clear the spool. All the parts above are parameterised on the Smol frame (`TF`, `A`, `V_` in `printed_lid.py`), so the carrier, the PREP block and the clearance checks follow a new pose.
2. Keep the pose. Take the filament out of the box through jojo's −X port, then bring it back in through a sealed PC4-M10 fitting in the hood's −X end wall, with a PTFE elbow of radius ≥ 25 mm outside the lid. This adds an external tube loop and two more places that need sealing.

Please decide this before printing anything except a test carrier.

## Rebuild

```
cd build/lid
python3 clouds.py        # needs cad/01 (python transport/restore.py)
python3 printed_lid.py   # 08a/08b/08c + one-piece STL
python3 checks.py        # checks.json and cad/08-Printed-lid.zip
python3 render.py        # docs/printed-lid.png
```

Each derivative file keeps jojo's CC BY-NC-SA license and attribution.
