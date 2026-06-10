"""Decompress every .sc file in a Brawl Stars APK / APKM, decode embedded KTX
(ASTC) textures, and write a PNG atlas per file under data/sc_textures/.

Usage:
  python3 data/extract_apk_graphics.py <apk-or-apkm-path>

For .sc files that don't contain texture data the file is skipped silently.
Atlas PNGs are written as data/sc_textures/<sc-name>_<index>_<WxH>.png so each
.sc file's outputs cluster together.
"""

import io
import struct
import sys
import zipfile
from pathlib import Path

from PIL import Image
import texture2ddecoder
from sc_compression import decompress as sc_decompress

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "sc_textures"

# OpenGL internalFormat → (decoder, block_w, block_h)
ASTC_BLOCKS = {
    0x93B0: (4, 4), 0x93B1: (5, 4), 0x93B2: (5, 5), 0x93B3: (6, 5),
    0x93B4: (6, 6), 0x93B5: (8, 5), 0x93B6: (8, 6), 0x93B7: (8, 8),
    0x93B8: (10, 5), 0x93B9: (10, 6), 0x93BA: (10, 8), 0x93BB: (10, 10),
    0x93BC: (12, 10), 0x93BD: (12, 12),
}


def decode_ktx(raw, pos):
    ident = raw[pos:pos + 12]
    if ident != b"\xabKTX 11\xbb\r\n\x1a\n":
        return None
    hdr = struct.unpack("<13I", raw[pos + 12:pos + 12 + 52])
    _, _, _, _, gif, _, w, h, _, _, _, _, kvd = hdr
    payload_start = pos + 12 + 52 + kvd
    img_size = struct.unpack("<I", raw[payload_start:payload_start + 4])[0]
    payload = raw[payload_start + 4:payload_start + 4 + img_size]

    if gif in ASTC_BLOCKS:
        bw, bh = ASTC_BLOCKS[gif]
        rgba = texture2ddecoder.decode_astc(payload, w, h, bw, bh)
        return Image.frombytes("RGBA", (w, h), rgba, "raw", "BGRA")
    if gif == 0x9278:  # ETC2_RGBA8
        rgba = texture2ddecoder.decode_etc2a8(payload, w, h)
        return Image.frombytes("RGBA", (w, h), rgba, "raw", "BGRA")
    if gif == 0x9274:  # ETC2_RGB
        rgb = texture2ddecoder.decode_etc2(payload, w, h)
        return Image.frombytes("RGBA", (w, h), rgb, "raw", "BGRA")
    return None  # unknown format


def extract_sc(name, data):
    try:
        raw, _, _ = sc_decompress(data)
    except Exception:
        return []
    images = []
    i = 0
    while True:
        i = raw.find(b"\xabKTX", i)
        if i < 0:
            break
        img = decode_ktx(raw, i)
        if img is not None:
            images.append(img)
        i += 1
    return images


def iter_sc_files(apk_path):
    """Yield (name, bytes) for every .sc file in the APK or APKM bundle."""
    outer = zipfile.ZipFile(apk_path)
    found = False
    for n in outer.namelist():
        if n.startswith("assets/sc/") and n.endswith(".sc"):
            found = True
            yield Path(n).name, outer.read(n)
    if found:
        return
    # APKM bundle — peek inside inner APKs
    for n in outer.namelist():
        if not n.endswith(".apk"):
            continue
        inner = zipfile.ZipFile(io.BytesIO(outer.read(n)))
        for m in inner.namelist():
            if m.startswith("assets/sc/") and m.endswith(".sc"):
                yield Path(m).name, inner.read(m)


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    apk = Path(sys.argv[1]).expanduser()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_pngs = 0
    total_bytes = 0
    for name, data in iter_sc_files(apk):
        total_files += 1
        stem = name[:-3]
        images = extract_sc(name, data)
        if not images:
            continue
        for idx, img in enumerate(images):
            out = OUT_DIR / f"{stem}_{idx}_{img.width}x{img.height}.png"
            img.save(out, optimize=True)
            total_pngs += 1
            total_bytes += out.stat().st_size
        print(f"  {name}: {len(images)} texture(s)")

    print(f"\n{total_files} .sc files scanned · {total_pngs} PNGs written · {total_bytes/1024/1024:.1f} MB total")
    print(f"output: {OUT_DIR.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
