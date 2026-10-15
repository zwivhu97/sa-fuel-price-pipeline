from datetime import date
from pathlib import Path

import requests

RAW_ROOT = Path(__file__).resolve().parents[1] / "data" / "raw"


def download_raw(url, source, prefix, extension):
    """Download a URL and save the response untouched under data/raw/<source>/."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    folder = RAW_ROOT / source
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{prefix}_{date.today().isoformat()}.{extension}"
    path.write_bytes(response.content)
    return path