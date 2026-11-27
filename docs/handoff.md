# Picking up the project

The target is the single-spool box supplied with the Polymaker PolyDryer. The older two-spool PolyBox and the separate stacked BoxTurtle enclosure project have different geometry.

## Design decisions

1. The baseline reuses both original driven wheels and tires. A smaller printed wheel and TPU tire are under consideration after measuring the molded box. The current carrier targets the V1.0 matched 8 × 80 mm shaft and 15/30-tooth gears. V1.1 uses a 5 × 60 mm shaft with a flat and 12/22-tooth gears. The two tire STLs are byte-identical. Confirm the donor before changing the carrier.
2. Keep the factory rear passive roller. Its position and working diameter determine the spool center. The measured working diameter is 8 mm. The 95 mm length in the model came from the printable-body reference.
3. Preserve the stock lid if possible. The particular stock-lid pose tested with a 205 × 78 mm spool does not clear. The raised option is 35.4 mm taller than the two-port printed lid and gives about 2.09 mm of sampled clearance to the assembled Smol feeder and PREP switch position. The build uses the V1.0 roller and a Smol feeder reference extracted from V1.1 CAD.
4. Fit with the lid shut, spool turning and box on the dock matters. Sealing, thermal performance, spool loading, idler access, and actual feeding and rewinding are open tests.

## Revision 2c (2026-11-25)

The drive moved into the factory front cradles. Details are in [cradle-drive.md](cradle-drive.md). One printed roller with an integrated 15T gear runs on the factory rod. The treads are TPU, the printed 17T pinion goes on the V1.0 N20, and the bracket keys into the left cradle slot and holds the motor with zip ties. The spool pose, lid, feeder, LOAD, PREP and paths are unchanged, and the lane LED is removed. The `--gearset v1pinion` option keeps the V1.0 pinion at 41 % rewind speed. Next: take the five measurements listed in cradle-drive.md, adjust `PITCH` if needed, print, then bench-test payout, mesh and rewind. The section below records the revision 1 plan.

## Whole-assembly audit, printed lid rev 3.2 (2026-11-27)

Every part was checked against every other in one frame, plus thin walls and print overhangs (`build/audit/`, results in [printed-lid.md](printed-lid.md#whole-assembly-audit-rev-32)). Fixed: the thin +X canopy end wall, the outlet groove that cut the thread crests (now a counterbore), the thin guide mouth lip (collar), the carrier guide and web that started in mid-air (print fin, web foot), the +X canopy strip that started flat over open space (45° underside), collapsed triangles in the roller and pinion STLs, and the stale feeder pose in the 07 STEP. The motor bracket's print orientation changed to its +X end face. The N20 needs a 2-pin inline connector inside the box so the lid lifts off freely. No real collisions were found; the only overlaps are with the box proxy, which is a different box.

## Printed lid rev 3.1 (2026-11-27)

Rev 3.1 adds the following. `verify.py` re-checks all of it on the final STLs.
- **Outlet:** a printed M10×1 thread for the PC4-M10, with an O-ring / TPU-washer seat (a counterbore since rev 3.2).
- **Inlet guide:** a Ø4.3 bore for a PTFE liner.
- **Wiring:** a Micro-Fit 3.0 2×6 bulkhead plate (43020-1200) instead of the gland.
- **Seal:** TPU rim gaskets in three heights, chosen with a clay test.
- **Files:** the lid STL is decimated to 7.9 MB.

Open points:
- Confirm the Micro-Fit cutout against a real housing. The cutout now follows the Printables 1300761 library shape; its dual-row height is extrapolated.
- Do the clay gap test.

## Printed lid rev 3 (2026-11-26)

[printed-lid.md](printed-lid.md) has the details.

**One-piece lid.** It prints rim down with no supports:
- Jojo's two-port lid (Printables 1441905) is kept triangle for triangle below Z 102. Its end caps (latch bars, finger slots) are rebuilt from jojo's own geometry above Z 102.
- The flat plate is replaced by a 45° chamfered vault with a 36 mm bridge.
- The feeder sits under a 45° frustum with a 25 mm top bridge.

**Feeder.** It is re-posed to 45° uphill toward −X. The inlet and PREP are low at +X and fed up the spool's +X side through an R20 guide. The outlet is a PC4-M10 square to the canopy's −X face.

**Carrier.** One carrier holds the Smol (V1 heat-set inserts for its two downward bolts), the PREP block and the guide. It is held by 2 × M3 through the −Y wall. Service: remove those two screws and the module lifts out through the rim.

**History.**
- Rev 1 kept the archived pose, which needed about a 110° inlet turn.
- Rev 2 (40°, bonded hood) fixed the routing but could not print as one part without supports.

**Next.**
- Check the guide mouth against the box's +X end wall.
- Bench-feed the module.
- Print a test.

## Next work (revision 1, superseded)

Start with the [molded-box data, probe diagram and six outstanding readings](measurements/README.md). The retained rear axle is 22 mm above the floor reference. The measured 129 mm wheel stations rule out the stock wheel lips in the current pose. The Ø30 lip / Ø28 TPU tread is a candidate. Check the wheel and gear tracks before committing to a new drive position. The existing CAD and printable bench carrier represent the original trial.

Bring the measurements into the assembly using the rear axle as the reference. The trial driven axle is 128.57 mm forward and 0.27 mm below the reference rear axle. Check the wheel lips, driven gear, carrier tabs, opposite wall and both dock openings first. Nominal proxy penetrations are about 1.25–1.33 mm at the two wheels, 1.24 mm at the driven gear and 1.04 mm at the carrier. A different floor profile or roller diameter changes the result.

After resolving those interferences, design the base adapter, feeder attachment, PREP guide and actuator, and sealed disconnect for the lid harness. Bench-check shaft retention, wheel tracking, gear mesh, free payout, and loaded rewind before testing AFC switching or running the dryer.

## Geometry sources

The stock lid reference and curved desiccant insert are especially useful because they share a coordinate system. The compatible two-port printed lid provides an alternative sealing perimeter. The GrabCAD item originally considered for this project did not establish the molded box's internal floor geometry. The printable body is useful for comparison, and the original box is the authority for final mounting dimensions.

See [fit study](fit-study.md#sources-and-attribution) for upstream CAD and licenses.
