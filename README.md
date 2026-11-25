# Poly-Turtle

One BoxTurtle filament lane in a removable, single-spool Polymaker PolyDryer Box. The priorities are to reuse the donor rubber tires, shaft, gears, motor, extruder components and PREP/LOAD switches, keep the spool chamber sealed, and preserve the dryer's docking and airflow.

**Current stage: CAD fit study and bench carrier.** The driven parts fit the V1.0 carrier in CAD. The modeled wheel ends and gear interfere with the floor of a third-party printable body. Measurements of the molded box show about 7.1 mm interference at both wheel lips in the original drive position. A proposed smaller wheel clears those two points by about 1.7 mm. A raised replacement lid clears the assembled feeder in the modeled pose. A working conversion has yet to be built or tested.

![Side view of the prototype and fit findings](docs/fit-overview.png)

## Start here

- [Molded-box measurements, original photos and next six probe locations](docs/measurements/README.md).
- [Illustrated caliper guide and full-size roller template](docs/PolyDryer-Caliper-Guide.pdf). Page 2 prints at 100% on US Letter landscape. Pages 3–6 show where to measure and record readings.
- [Download the entire repository](https://github.com/RyuNinja00/Poly-Turtle/archive/refs/heads/main.zip). Extract it, then run the command below to open the two full-size assemblies or recreate the original fit-study download.
- [CAD file directory](cad/) and [fit findings, assembly instructions and attributions](docs/fit-study.md).
- [Project handoff](docs/handoff.md) for design decisions, unverified assumptions and what to do after measuring the stock box.
- [Build sources and reproduction instructions](build/README.md).

Dimensions are in millimeters. The file marked PROXY represents a third-party printable body. The stock-lid free-volume STEP is a solid representation of empty space.

## Opening the large STEP assemblies

The original 35.5 MB fit-study ZIP is stored byte-for-byte in ordered pieces in [transport](transport/). A clone or the GitHub Download ZIP contains everything required. From the extracted repository run:

```
python transport/restore.py
```

On Windows with the Python launcher, use `py transport/restore.py`. This offline script uses the Python standard library, verifies the original archive checksum, and writes:

- `downloads/PolyDryer-BoxTurtle-Fit-Study.zip`
- `cad/01-Single-lane-fit-study.step`
- `cad/03-Stock-lid-interference-trial.step`

The other STEP/STL files and the illustrated PDF are available individually in the repository. Rebuilding CAD from upstream is optional.
