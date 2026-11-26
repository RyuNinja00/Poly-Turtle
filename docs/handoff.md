# Picking up the project

The target is the single-spool box supplied with the Polymaker PolyDryer. The older two-spool PolyBox and the separate stacked BoxTurtle enclosure project have different geometry.

## Design decisions

1. The baseline reuses both original driven wheels and tires. A smaller printed wheel and TPU tire are under consideration after measuring the molded box. The current carrier targets the V1.0 matched 8 × 80 mm shaft and 15/30-tooth gears. V1.1 uses a 5 × 60 mm shaft with a flat and 12/22-tooth gears. The two tire STLs are byte-identical. Confirm the donor before changing the carrier.
2. Keep the factory rear passive roller. Its position and working diameter determine the spool center. The measured working diameter is 8 mm. The 95 mm length in the model came from the printable-body reference.
3. Preserve the stock lid if possible. The particular stock-lid pose tested with a 205 × 78 mm spool does not clear. The raised option is 35.4 mm taller than the two-port printed lid and gives about 2.09 mm of sampled clearance to the assembled Smol feeder and PREP switch position. The build uses the V1.0 roller and a Smol feeder reference extracted from V1.1 CAD.
4. Fit with the lid shut, spool turning and box on the dock matters. Sealing, thermal performance, spool loading, idler access, and actual feeding and rewinding are open tests.

## Revision 2c (2026-11-25)

The drive moved into the factory front cradles. Details are in [cradle-drive.md](cradle-drive.md). One printed roller with an integrated 15T gear runs on the factory rod. The treads are TPU, the printed 17T pinion goes on the V1.0 N20, and the bracket keys into the left cradle slot and holds the motor with zip ties. The spool pose, lid, feeder, LOAD, PREP and paths are unchanged, and the lane LED is removed. The `--gearset v1pinion` option keeps the V1.0 pinion at 41 % rewind speed. Next: take the five measurements listed in cradle-drive.md, adjust `PITCH` if needed, print, then bench-test payout, mesh and rewind. The section below records the revision 1 plan.

## Printed lid rev 2 (2026-11-26)

Does this need a new lid? Yes. [printed-lid.md](printed-lid.md) covers the details. Jojo's two-port lid (Printables 1441905) is kept exactly up to the plate top, and the old outlet hole is closed. A hood is bonded on. One feeder carrier takes the trayframe's place: the Smol's two downward bolts go into V1 heat-set inserts, and the carrier also holds the PREP block, a curved inlet guide and two towers. Two roof screws drop the whole module out for service.

Rev 1 kept the archived feeder pose. That pose had the inlet at the high end of a downward-tilted axis, so filament would have needed about a 110° turn. Rev 2 turns the Smol and PREP end for end and tilts them to 40° uphill toward −X. The inlet is now low at +X, fed up the +X side of the spool: the turn is 8° at the guide mouth on a full spool and 46° on a near-empty spool, followed by a smooth R20 bend. The outlet leaves through a PC4-M10 boss in the hood's −X wall. The hood grows from 35.4 to 45.9 mm above the lid. The spool pose and the cradle drive are unchanged. Load the spool so it pays out up its +X side. Next: check the guide-mouth clearance at the box's +X wall, then bench-feed the module before bonding the hood.

## Next work (revision 1, superseded)

Start with the [molded-box data, probe diagram and six outstanding readings](measurements/README.md). The retained rear axle is 22 mm above the floor reference. The measured 129 mm wheel stations rule out the stock wheel lips in the current pose. The Ø30 lip / Ø28 TPU tread is a candidate. Check the wheel and gear tracks before committing to a new drive position. The existing CAD and printable bench carrier represent the original trial.

Bring the measurements into the assembly using the rear axle as the reference. The trial driven axle is 128.57 mm forward and 0.27 mm below the reference rear axle. Check the wheel lips, driven gear, carrier tabs, opposite wall and both dock openings first. Nominal proxy penetrations are about 1.25–1.33 mm at the two wheels, 1.24 mm at the driven gear and 1.04 mm at the carrier. A different floor profile or roller diameter changes the result.

After resolving those interferences, design the base adapter, feeder attachment, PREP guide and actuator, and sealed disconnect for the lid harness. Bench-check shaft retention, wheel tracking, gear mesh, free payout, and loaded rewind before testing AFC switching or running the dryer.

## Geometry sources

The stock lid reference and curved desiccant insert are especially useful because they share a coordinate system. The compatible two-port printed lid provides an alternative sealing perimeter. The GrabCAD item originally considered for this project did not establish the molded box's internal floor geometry. The printable body is useful for comparison, and the original box is the authority for final mounting dimensions.

See [fit study](fit-study.md#sources-and-attribution) for upstream CAD and licenses.
