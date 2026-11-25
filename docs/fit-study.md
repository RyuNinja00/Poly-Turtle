# Single-lane PolyDryer Box fit study
Open Start-here-Fit-check.pdf for the layout and full-size template. The project targets the removable single-spool PolyDryer Box. Dimensions are millimeters. This is a fit study with a printable bench carrier. A working or dryer-qualified conversion still requires mechanical and electrical tests.

## Open in CAD
Import 01 as a STEP assembly. Add 04 and 05 at their saved coordinates in millimeters to see the printable reference body and raised-lid alternative. File 02 is solid geometry representing the empty space inside the stock lid. Hide it for a normal assembly view. For the original-lid trial, hide the raised feeder and lid, then import 03 at the origin alongside 02 and the spool. File 06 has its own axle-centered coordinate system for editing or bench printing.

## What was modeled
- The V1.0 wheel assemblies, both flexible tires, Ø8 × 80 shaft, MR148 bearings, 15/30-tooth gears and spacer are donor geometry. The N20 shape came from the V1.1 model and was aligned to the V1.0 pinion. The V1.0 and V1.1 flexible tire STL files have identical Git contents. The V1.1 Ø5 × 60 shaft with flat needs a different carrier/drive arrangement.
- The single-piece trial carrier has 14.10 mm through-seats for the bearings, an open N20 saddle, tie slots and two fixture tabs. Check retention, axial play, motor alignment, gear mesh, payout drag and loaded rewind on the bench. The fixture tabs require a base adapter after the cast-in floor geometry is established.
- The existing rear roller is represented by a Ø8 × 95 cylinder using the printable box as a reference. Its actual outside diameter and axle position in the molded product remain measurements. The design spool has Ø205 flanges, 78 mm overall width, 2 mm flange thickness and a Ø195 winding envelope.
- The raised-lid trial uses an assembled Smol feeder with its LOAD switch. PREP is a proposed switch position. The two short colored cylinders mark filament centerlines. A PREP guide and actuator, feeder mounting, wiring disconnect, sealed pass-through, idler access, dock airflow and hot operation still require design or verification. The raised shell is a clearance prototype.

## CAD checks
The stock-lid interior reference measures 201.41 × 86.81 × 49.80 mm overall. The desiccant insert's curved groove supplied a nominal spool-axis datum. Aligning the rear reference roller and driven tires in the selected pose shifted the trial spool center 6.07 mm rearward and 3.35 mm upward from that datum. The desiccant container itself is omitted from the operating assembly.

| Check | Result for the modeled pose |
|---|---|
| Carrier against shaft, both wheel assemblies, two bearings, N20, two gears and spacer | No positive-volume solid intersection in the nominal pose |
| Stock-lid candidate in file 03 | Sampled hardware extends 4.67 mm outside the reference free volume and enters the conservative spool envelope by 2.12 mm |
| Raised shell against Smol and proposed PREP | Closest sampled clearance 2.09 mm |
| Raised shell against design spool | Closest sampled clearance 1.36 mm |
| Feeder and PREP against conservative Ø205 × 78 spool envelope | At least 4.42 mm in the sampled pose |
| Driven wheel assemblies against printable base | About 1.25 and 1.33 mm sampled penetration |
| Driven gear and trial carrier against printable base | About 1.24 and 1.04 mm sampled penetration |
| Spool against printable base | About 1.24 mm sampled penetration near the opposite end wall |

The distances involving meshes are signed surface samples. They describe the chosen poses and are not guaranteed manufacturing clearances or a global proof of infeasibility. The two-port lid's perimeter and gasket geometry were retained. A local capped pocket and a 4.3 mm outlet were added. The pocket increases the modeled lid height by 35.4 mm. Retention, sealing, routing and assembly sequence remain untested.

## Physical fit check
1. Print page 2 of the PDF at actual size and measure its 50 mm bar. Register the crosshair on the rear factory roller. The trial driven axle is 128.57 mm forward and 0.27 mm below that roller.
2. Measure the actual rear roller diameter and compare the floor with the template near each outer wheel lip (roughly 42 mm from the spool midplane), then near the driven gear (roughly 13.5 mm off center). The projected wheel lip is Ø47.6 mm and the flexible tread is Ø43.76 mm. Check both lips through a full rotation.
3. Compare the largest intended spool with the opposite end wall. The modeled Ø205 spool is more restrictive than a nominal Ø200 spool. Check clearance to both dock air openings at the proposed carrier location.
4. Use the resulting measurements to locate the base adapter. A dimensioned cross-section or straight-on photo with a ruler through the roller axes is sufficient for a first revision.

## Sources and attribution
- BoxTurtle, Armored Turtle. V1.0 tagged source and V1.1 assembly source. Donor geometry was extracted and repositioned. GPL-3.0 license is enclosed. https://github.com/ArmoredTurtle/BoxTurtle/tree/BT-1.0 and https://github.com/ArmoredTurtle/BoxTurtle/tree/ad3cd010009d54c8c969a0dc94fbdcfc25320ded
- PolyDryer Lid Interior Reference Dimensions, EmeraldFlame. Public Domain per Printables. The reference was transformed into assembly coordinates. https://www.printables.com/model/1747851
- PolyDryer In-Lid Desiccant Container, EmeraldFlame. GPL v3. Measurements of the curved groove were used to locate the spool-axis reference. https://www.printables.com/model/1757829
- Drybox To Fit Polydryer, Extrutim. File 04 is a translated copy of the printable body used as a proxy. CC Attribution–NonCommercial–ShareAlike. https://www.printables.com/model/872878
- Printed Lid for Polydryer Box, jojo, based on work by Extrutim and Cipism. File 05 adapts the two-port model and retains its CC Attribution–NonCommercial–ShareAlike license. https://www.printables.com/model/1441905
