# Picking up the project

The target is the single-spool box supplied with the Polymaker PolyDryer. The older two-spool PolyBox and the separate stacked BoxTurtle enclosure project have different geometry.

## Design decisions

1. Reuse the two original powered BoxTurtle wheels and tires. The current carrier targets the V1.0 matched 8 × 80 mm shaft and 15/30-tooth gears. V1.1 uses a 5 × 60 mm shaft with a flat and 12/22-tooth gears. The two tire STLs are byte-identical. Confirm the donor before changing the carrier.
2. Keep the factory rear passive roller. Its position and working diameter determine the spool center. The model assumes an 8 × 95 mm roller from the printable-body reference.
3. Preserve the stock lid if possible. The particular stock-lid pose tested with a 205 × 78 mm spool does not clear. The raised option is 35.4 mm taller than the two-port printed lid and gives about 2.09 mm of sampled clearance to the assembled Smol feeder and PREP switch position. The build uses the V1.0 roller and a Smol feeder reference extracted from V1.1 CAD.
4. Fit with the lid shut, spool turning and box on the dock matters. Sealing, thermal performance, spool loading, idler access, and actual feeding and rewinding are open tests.

## Next work

The repository currently contains no caliper readings from the actual box. Record the diameter of the surface the spool rolls on, its crown depth, and the floor or rib depths at the four longitudinal stations and four lateral tracks shown in the guide. Also measure the opposite wall, the intended spool, and its clearance under the closed lid. Keep the bridge datum and left/right orientation with the readings.

Bring the measurements into the assembly using the rear axle as the reference. The trial driven axle is 128.57 mm forward and 0.27 mm below the reference rear axle. Check the wheel lips, driven gear, carrier tabs, opposite wall and both dock openings first. Nominal proxy penetrations are about 1.25–1.33 mm at the two wheels, 1.24 mm at the driven gear and 1.04 mm at the carrier. A different floor profile or roller diameter changes the result.

After resolving those interferences, design the base adapter, feeder attachment, PREP guide and actuator, and sealed disconnect for the lid harness. Bench-check shaft retention, wheel tracking, gear mesh, free payout, and loaded rewind before testing AFC switching or running the dryer.

## Geometry sources

The stock lid reference and curved desiccant insert are especially useful because they share a coordinate system. The compatible two-port printed lid provides an alternative sealing perimeter. The GrabCAD item originally considered for this project did not establish the molded box's internal floor geometry. The printable body is useful for comparison, and the original box is the authority for final mounting dimensions.

See [fit study](fit-study.md#sources-and-attribution) for upstream CAD and licenses.
