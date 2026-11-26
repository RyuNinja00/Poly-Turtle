# Regenerate the cradle drive

Requires Python 3 with numpy, scipy and matplotlib. No CAD kernel is needed.

1. From the repository root, run `python transport/restore.py` to restore `cad/01-Single-lane-fit-study.step`, which supplies the donor N20, Smol, PREP and spool.
2. In this folder:

```
python cradle_drive.py                      # STLs + layout.json -> cad/07-cradle-drive/
python checks.py                            # checks.json (clearances, gear mesh, assembly sequence)
python cradle_drive.py --gearset v1pinion   # V1.0-pinion option -> cad/07-cradle-drive/v1-pinion-variant/
python checks.py --gearset v1pinion
python render.py                            # docs/cradle-drive-overview.png
python finalize_guide.py                    # measurement picture guide (docs/measurements/finalize/, PDF)
python make_step.py out.step && python verify_step.py out.step
```

All geometry follows from the parameters at the top of `cradle_drive.py`. Set `PITCH` to the measured roller pitch and re-run. Gear sets live in `GEARSETS`. `checks.json` lists any negative clearance under `negative clearances`.
