#!/usr/bin/env python3
"""Push share/stimuli_reference.json to Antigone Lab (Lovable catalog endpoint).

Requires Lovable to implement POST /api/public/catalog with header
X-Antigone-Secret == ANTIGONE_INGEST_SECRET.

If the endpoint returns 404, upload share/stimuli_reference.json manually in Lovable.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from antigone.lovable_ingest import push_catalog


def main() -> None:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(description="POST stimulus catalog to Lovable")
    ap.add_argument(
        "catalog",
        nargs="?",
        type=Path,
        default=ROOT / "share" / "stimuli_reference.json",
        help="Catalog JSON (default: share/stimuli_reference.json)",
    )
    ap.add_argument("--url", help="Override Lovable base URL (will append /api/public/catalog)")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    catalog_path = args.catalog.resolve()
    try:
        result = push_catalog(catalog_path, catalog_url=args.url, timeout_s=args.timeout)
    except RuntimeError as exc:
        print(f"[fail] {exc}")
        print()
        print("Fallback: open Lovable chat and paste:")
        print()
        print("  Replace src/data/stimuli_reference.json with the attached file from the repo.")
        print("  Then attach: " + str(catalog_path))
        sys.exit(1)

    print(f"[ok] catalog pushed: cells={result['cells']}")
    print(f"  url: {result['catalog_url']}")


if __name__ == "__main__":
    main()
