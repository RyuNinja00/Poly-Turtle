# Poly-Turtle

One BoxTurtle filament lane in a removable, single-spool Polymaker PolyDryer Box. The priorities are to reuse the donor rubber tires, shaft, gears, motor, extruder components and PREP/LOAD switches, keep the spool chamber sealed, and preserve the dryer's docking and airflow.

**Current stage: revision 2c, the cradle drive (CAD + printable parts, not yet bench-tested).** The respool drive sits in the factory front-roller cradles: one printed roller with an integrated gear runs on the factory rod, and the V1.0 N20 drops into a zip-tie bracket. That's 5 printed parts with no fasteners on the roller, and rewind runs at 93 % of V1.0. A TPU tread sized to keep the archived spool pose means the raised lid, Smol extruder with LOAD, PREP switch and filament paths are unchanged. The lane LED is dropped. See [cradle drive](docs/cradle-drive.md). **Printed lid rev 1** (jojo's two-port lid + feeder hood + feeder carrier) is in [printed lid](docs/printed-lid.md). One open item, the spool-to-PREP filament entry, needs a decision before printing. A working conversion has yet to be built or tested.

![Cradle drive overview](docs/cradle-drive-overview.png)

## Start here

- [Cradle drive: parts, assembly, clearance results and the measurements that confirm it](docs/cradle-drive.md). Printable STLs in [cad/07-cradle-drive](cad/07-cradle-drive/); assembly STEP in `cad/07-Cradle-drive-layout.step.zip`.
- [Printed lid (rev 1): parts, assembly, checks and the open inlet item](docs/printed-lid.md). STLs in `cad/08-Printed-lid.zip`.
- [Final measurements picture guide](docs/measurements/finalize-guide.md) ([printable PDF with record sheet](docs/PolyDryer-Finalize-Guide.pdf)).
- [Molded-box measurements and original photos](docs/measurements/README.md).
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
