"""Generate lightweight WebP previews for every reservation PDF page."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDFTOPPM = Path(
    os.environ.get(
        "PDFTOPPM",
        r"C:\Users\李浩康\.cache\codex-runtimes\codex-primary-runtime"
        r"\dependencies\native\poppler\Library\bin\pdftoppm.exe",
    )
)
SOURCE_FOLDERS = ("docs", "docs2")
RESOLUTION_DPI = 144
WEBP_QUALITY = 82


def generate_folder(folder_name: str) -> dict[str, int]:
    source_dir = ROOT / folder_name
    output_dir = ROOT / f"{folder_name}-images"
    output_dir.mkdir(exist_ok=True)
    page_counts: dict[str, int] = {}

    for pdf_path in sorted(source_dir.glob("*.pdf")):
        document_id = pdf_path.stem
        page_count = len(PdfReader(pdf_path).pages)
        page_counts[document_id] = page_count

        with tempfile.TemporaryDirectory(prefix="reservation-pdf-") as temp_dir:
            prefix = Path(temp_dir) / document_id
            subprocess.run(
                [
                    str(PDFTOPPM),
                    "-r",
                    str(RESOLUTION_DPI),
                    "-png",
                    str(pdf_path),
                    str(prefix),
                ],
                check=True,
            )

            for page_number in range(1, page_count + 1):
                png_path = Path(f"{prefix}-{page_number}.png")
                webp_path = output_dir / f"{document_id}-{page_number}.webp"
                with Image.open(png_path) as image:
                    image.convert("RGB").save(
                        webp_path,
                        "WEBP",
                        quality=WEBP_QUALITY,
                        method=6,
                    )

        print(f"generated {folder_name}/{pdf_path.name}: {page_count} page(s)")

    return page_counts


def main() -> None:
    if not PDFTOPPM.exists():
        raise FileNotFoundError(f"pdftoppm was not found: {PDFTOPPM}")

    manifest = {folder: generate_folder(folder) for folder in SOURCE_FOLDERS}
    manifest_json = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "document-pages.js").write_text(
        f"window.DOCUMENT_PAGE_COUNTS={manifest_json};\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
