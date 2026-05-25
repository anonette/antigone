#!/usr/bin/env python3
"""Build share/stimuli_reference.json for Lovable Stimulus reference page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from antigone.stimuli_catalog import write_reference_json  # noqa: E402


def main() -> None:
    out = ROOT / "share" / "stimuli_reference.json"
    write_reference_json(out)
    n = len(__import__("json").loads(out.read_text(encoding="utf-8"))["cells"])
    print(f"Wrote {out} ({n} cells)")


if __name__ == "__main__":
    main()
