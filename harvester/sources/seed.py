"""The spine loader — reads the curated games table (not an enricher).

`seed.json` is written by `harvester/build_seed.py`. If it is missing we build it
on the fly so a fresh checkout can harvest without a separate step.
"""

import json
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent / "data" / "seed.json"


def load():
    if not SEED.exists():
        from .. import build_seed
        return build_seed.finalize()
    return json.loads(SEED.read_text(encoding="utf-8"))
