"""Render a frozen, self-authored exam-style *synthetic* formula suite.

The manifest is committed and immutable for a particular evaluation. Generated
PNGs are *not* exam photos and are stored outside source control. Never report
their metrics as real-world exam photo performance.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "frozen_manifest.json"


def render_formula(latex: str) -> Image.Image:
    fig = plt.figure(figsize=(11, 1.65), dpi=175)
    fig.patch.set_facecolor("white")
    fig.text(.02, .5, "$" + latex + "$",
             fontsize=29, ha="left", va="center", color="#080808")
    image = io.BytesIO()
    try:
        fig.savefig(image, format="png", facecolor="white",
                    bbox_inches="tight", pad_inches=.16)
    finally:
        plt.close(fig)
    image.seek(0)
    with Image.open(image) as im:
        return im.convert("RGB").copy()


def apply_style(image: Image.Image, style: str) -> Image.Image:
    if style == "clean":
        return image
    if style == "lowcontrast":
        return Image.blend(image, Image.new("RGB", image.size, "white"), .5)
    if style == "blur":
        return image.filter(ImageFilter.GaussianBlur(.75))
    if style == "rotate":
        return image.rotate(2.0, resample=getattr(Image, "Resampling", Image).BICUBIC,
                            fillcolor="white", expand=True)
    raise ValueError(f"Unknown render style: {style}")


def generate(output_dir: Path):
    manifest_data = MANIFEST.read_bytes()
    data = json.loads(manifest_data)
    assert data["schema_version"] == "formula-frozen-v016-1"
    examples = data["cases"]
    ids = [e["id"] for e in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evaluation IDs")
    output_dir.mkdir(parents=True, exist_ok=True)
    index = {"manifest_sha256": hashlib.sha256(manifest_data).hexdigest(),
             "render_engine": f"matplotlib-{matplotlib.__version__}",
             "provenance": data["provenance"], "samples": []}
    for case in examples:
        path = output_dir / (case["id"] + ".png")
        png = apply_style(render_formula(case["latex"]), case["render"])
        png.save(path, "PNG")
        index["samples"].append({
            "id": case["id"], "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "width": png.width, "height": png.height,
        })
    index_path = output_dir / "image_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {len(examples)} synthetic test images at {output_dir}")
    print(f"manifest_sha256 = {index['manifest_sha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "generated")
    args = parser.parse_args()
    generate(args.out)
