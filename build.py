from __future__ import annotations

import argparse
import io
import json
import math
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts" / "upstream"
DIST = ROOT / "dist"
WEIGHTS = ("Light", "Regular", "Retina", "Medium", "SemiBold", "Bold")
PACK_FORMATS = {
    "1.18.2": 8,
    "1.19.2": 9,
    "1.19.3": 12,
    "1.19.4": 13,
    "1.20": 15,
    "1.20.1": 15,
    "1.20.2": 18,
    "1.20.3": 22,
    "1.20.4": 22,
    "1.20.5": 32,
    "1.20.6": 32,
    "1.21": 34,
    "1.21.1": 34,
    "1.21.2": 42,
    "1.21.3": 42,
    "1.21.4": 46,
    "1.21.5": 55,
    "1.21.6": 63,
    "1.21.7": 64,
    "1.21.8": 64,
    "1.21.9": 69,
    "1.21.10": 69,
    "1.21.11": 75,
    "26.1": 84,
    "26.1.2": 84,
    "26.2": 88,
    "26.3": (97, 1),
}


def oblique_font(source: bytes, weight: str) -> bytes:
    font = TTFont(io.BytesIO(source))
    glyph_set = font.getGlyphSet()
    glyphs = font["glyf"]
    shear = math.tan(math.radians(12))
    for name in font.getGlyphOrder():
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(TransformPen(pen, (1, 0, shear, 1, 0, 0)))
        glyphs[name] = pen.glyph()

    for table in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX"):
        if table in font:
            del font[table]
    for name_id, value in {
        1: "Fira Code Minecraft Oblique",
        2: weight,
        4: f"Fira Code Minecraft {weight} Oblique",
        6: f"FiraCodeMinecraft-{weight}Oblique",
        16: "Fira Code Minecraft Oblique",
        17: weight,
    }.items():
        font["name"].setName(value, name_id, 3, 1, 0x409)
    font["post"].italicAngle = -12
    font["head"].macStyle |= 0b10
    font["OS/2"].fsSelection |= 0b1
    font["OS/2"].fsSelection &= ~0b1000000
    font.recalcBBoxes = True
    result = io.BytesIO()
    font.save(result)
    font.close()
    return result.getvalue()


def metadata(version: str) -> dict:
    fmt = PACK_FORMATS[version]
    pack = {"description": "Fira Code - configure weight and slant with Respackopts"}
    if isinstance(fmt, tuple):
        pack["min_format"] = list(fmt)
        pack["max_format"] = list(fmt)
    elif fmt >= 65:
        pack["min_format"] = [fmt, 0]
        pack["max_format"] = fmt
    else:
        pack["pack_format"] = fmt
    return {"pack": pack}


def font_definition(version: str) -> dict:
    faces = {
        "regular": "firacode:firacode-${weight}-${style}.ttf",
        "bold": "firacode:firacode-${boldWeight}-${style}.ttf",
        "italic": "firacode:firacode-${weight}-oblique.ttf",
        "bold_italic": "firacode:firacode-${boldWeight}-oblique.ttf",
    }
    provider = {"type": "caxton"}
    for face, file in faces.items():
        provider[face] = {"file": file, "shadow_offset": 0.5}
    providers = [provider]
    if version in ("1.18.2", "1.19.2", "1.19.3", "1.19.4"):
        providers.append(
            {
                "type": "legacy_unicode",
                "template": "minecraft:font/unicode_page_%s.png",
                "sizes": "minecraft:font/glyph_sizes.bin",
            }
        )
    else:
        providers.extend(
            {"type": "reference", "id": f"minecraft:include/{name}"}
            for name in ("space", "default", "unifont")
        )
    return {"providers": providers}


def respackopts_config() -> dict:
    fields = {
        "weight": ("regular", [weight.lower() for weight in WEIGHTS]),
        "boldWeight": ("bold", [weight.lower() for weight in WEIGHTS]),
        "style": ("upright", ["upright", "oblique"]),
    }
    return {
        "id": "firaCodeMinecraft",
        "version": 9,
        "capabilities": ["FileFilter", "DirFilter"],
        "conf": {
            name: {
                "type": "enum",
                "default": default,
                "values": values,
                "reloadType": "Resource",
            }
            for name, (default, values) in fields.items()
        },
    }


def respackopts_translations() -> dict:
    result = {
        "rpo.firaCodeMinecraft": "Fira Code for Minecraft",
        "rpo.firaCodeMinecraft.weight": "Normal weight",
        "rpo.firaCodeMinecraft.boldWeight": "Bold text weight",
        "rpo.firaCodeMinecraft.style": "Normal text style",
        "rpo.firaCodeMinecraft.style.upright": "Upright",
        "rpo.firaCodeMinecraft.style.oblique": "Oblique",
        "rpo.firaCodeMinecraft.style.tooltip": "Italic formatting always uses the oblique face.",
    }
    for weight in WEIGHTS:
        for field in ("weight", "boldWeight"):
            result[f"rpo.firaCodeMinecraft.{field}.{weight.lower()}"] = weight
    return result


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def build(version: str, sources: dict[str, bytes], obliques: dict[str, bytes]) -> None:
    outdir = DIST / version
    outdir.mkdir(parents=True, exist_ok=True)
    destination = outdir / f"FiraCode-configurable-Caxton-MC{version}.zip"
    files = {
        "pack.mcmeta": metadata(version),
        "assets/minecraft/font/default.json": font_definition(version),
        "assets/minecraft/font/default.json.rpo": {
            "expansions": {
                "weight": "firaCodeMinecraft.weight",
                "boldWeight": "firaCodeMinecraft.boldWeight",
                "style": "firaCodeMinecraft.style",
            }
        },
        "respackopts.json5": respackopts_config(),
        "assets/minecraft/lang/en_us.json": respackopts_translations(),
    }
    with ZipFile(destination, "w", ZIP_DEFLATED, compresslevel=9) as pack:
        for path, content in files.items():
            pack.writestr(path, json_bytes(content))
        for weight, source in sources.items():
            for style, data in (("upright", source), ("oblique", obliques[weight])):
                path = f"assets/firacode/textures/font/firacode-{weight.lower()}-{style}.ttf"
                pack.writestr(path, data)
        pack.writestr("OFL.txt", (ROOT / "OFL.txt").read_bytes())
    print(destination.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Fira Code resource packs")
    parser.add_argument("--version", choices=PACK_FORMATS, default="26.2")
    parser.add_argument("--all", action="store_true", help="build every stable Caxton version")
    parser.add_argument("--list", action="store_true", help="show supported versions")
    args = parser.parse_args()
    if args.list:
        print(" ".join(PACK_FORMATS))
        return
    sources = {weight: (FONTS / f"FiraCode-{weight}.ttf").read_bytes() for weight in WEIGHTS}
    obliques = {weight: oblique_font(data, weight) for weight, data in sources.items()}
    for version in PACK_FORMATS if args.all else (args.version,):
        build(version, sources, obliques)


if __name__ == "__main__":
    main()
