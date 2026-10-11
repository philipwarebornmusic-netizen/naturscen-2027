#!/usr/bin/env python3
"""Copy the verified Naturscen deliverables into the static share site."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

FILES = {
    ROOT / "3d" / "naturscenen_3d_sikt_v4.3.html": DOCS / "3d" / "index.html",
    ROOT / "Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.pdf": DOCS / "Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.pdf",
    ROOT / "Platskarta_Naturscen_2027_ALTERNATIV_HORNFIX_5GRADER_v1.4.pdf": DOCS / "Platskarta_Naturscen_2027_ALTERNATIV_HORNFIX_5GRADER_v1.4.pdf",
    ROOT / "Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf": DOCS / "Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf",
    ROOT / "Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.png": DOCS / "assets" / "platskarta-c-v1.5.png",
    ROOT / "Platskarta_Naturscen_2027_KAPACITET_FORSKJUTNA_RADER_28CM_v1.5.csv": DOCS / "Platskarta_Naturscen_2027_KAPACITET_FORSKJUTNA_RADER_28CM_v1.5.csv",
}


def main() -> None:
    missing = [str(source.relative_to(ROOT)) for source in FILES if not source.is_file()]
    if missing:
        raise FileNotFoundError("Missing generated deliverables: " + ", ".join(missing))

    for source, destination in FILES.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    model = (DOCS / "3d" / "index.html").read_text(encoding="utf-8")
    expected_links = [destination.name for source, destination in FILES.items() if source.suffix == ".pdf"]
    absent_links = [name for name in expected_links if name not in model]
    if absent_links:
        raise ValueError("3D model is missing PDF links: " + ", ".join(absent_links))

    print("Synced share site:")
    for destination in FILES.values():
        print(f"  {destination.relative_to(ROOT)} ({destination.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
