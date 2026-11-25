"""Restore the exact original download and large CAD files from the GitHub import."""
import hashlib
from pathlib import Path
from zipfile import ZipFile

root = Path(__file__).resolve().parent.parent
parts = sorted((root / "transport").glob("piece-[0-9][0-9][0-9]"))
if len(parts) != 58:
    raise ValueError(f"Expected 58 archive parts, found {len(parts)}")
data = b"".join(p.read_bytes() for p in parts)
expected = "e2e22fc372c959e3d5ec638c8fadac89f0a613a6"
actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
if actual != expected:
    raise ValueError("Archive checksum mismatch")
dest = root / "downloads" / "PolyDryer-BoxTurtle-Fit-Study.zip"
dest.parent.mkdir(exist_ok=True)
dest.write_bytes(data)
with ZipFile(dest) as archive:
    if archive.testzip() is not None:
        raise ValueError("ZIP validation failed")
    for f in ["01-Single-lane-fit-study.step", "03-Stock-lid-interference-trial.step"]:
        (root / "cad").mkdir(exist_ok=True)
        (root / "cad" / f).write_bytes(archive.read(f))
