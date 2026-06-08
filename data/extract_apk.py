"""Extract Brawl Stars CSVs out of an APK or APKMirror bundle into data/csv_logic/.

Handles either:
- a regular .apk (csv_logic lives at assets/csv_logic/)
- an APKMirror .apkm bundle (csv_logic lives inside split_install_time_asset_pack.apk)

Usage: python3 data/extract_apk.py <path-to-apk-or-apkm>
"""

import io
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "csv_logic"


def csv_entries(zf):
    return [n for n in zf.namelist() if n.startswith("assets/csv_logic/") and n.endswith(".csv")]


def find_csvs(apk_path: Path):
    """Return (zipfile-like-object, list of csv-entry names)."""
    outer = zipfile.ZipFile(apk_path)
    names = csv_entries(outer)
    if names:
        return outer, names

    # No CSVs at the outer level — must be an APKM bundle wrapping split APKs.
    for inner_name in outer.namelist():
        if not inner_name.endswith(".apk"):
            continue
        with outer.open(inner_name) as f:
            data = f.read()
        inner = zipfile.ZipFile(io.BytesIO(data))
        names = csv_entries(inner)
        if names:
            print(f"  csv_logic found inside {inner_name}")
            return inner, names

    raise SystemExit("could not find assets/csv_logic/*.csv in APK or any inner APK")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    apk = Path(sys.argv[1]).expanduser()
    if not apk.exists():
        sys.exit(f"not found: {apk}")

    print(f"reading {apk.name} ({apk.stat().st_size / 1024 / 1024:.0f} MB)")
    zf, names = find_csvs(apk)
    print(f"  {len(names)} CSV files")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for entry in names:
        out = OUT_DIR / Path(entry).name
        with zf.open(entry) as src, open(out, "wb") as dst:
            shutil.copyfileobj(src, dst)
        written += 1
    print(f"wrote {written} files to {OUT_DIR.relative_to(REPO)}")


if __name__ == "__main__":
    main()
