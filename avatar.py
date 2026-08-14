"""Download avatars for the highest-ranked VUPs in dist/vup-full-array.json."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from PIL import Image

DATA_FILE = Path("dist/vup-full-array.json")
AVATAR_HOST = "https://i0.hdslb.com"
REQUEST_TIMEOUT = 30.0

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_dirname(name: str) -> str:
    """Reduce a VUP name to something usable as a single path component."""
    return _UNSAFE.sub("_", name).strip().rstrip(".") or "_"


def to_jpeg(path: Path) -> Path:
    """Re-encode a .webp download as .jpg, dropping the original."""
    if path.suffix.lower() != ".webp":
        return path
    target = path.with_suffix(".jpg")
    with Image.open(path) as image:
        image.convert("RGB").save(target, "jpeg")
    path.unlink()
    return target


def fetch_avatar(client: httpx.Client, face: str, folder: Path) -> str:
    url = f"{AVATAR_HOST}{face}"
    destination = folder / url.rsplit("/", 1)[-1]

    # A .webp is stored as .jpg once converted, so check both before re-fetching.
    if destination.exists() or destination.with_suffix(".jpg").exists():
        return "skipped"

    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as error:
        print(f"failed {url}: {error!r}")
        return "failed"

    folder.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    to_jpeg(destination)
    return "downloaded"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download avatars from VUP data")
    parser.add_argument("--dir", type=Path, default=Path("tmp"), help="Output directory")
    parser.add_argument("--sort", default="followers", help="Sort by this key, descending")
    parser.add_argument("--limit", type=int, default=300, help="Number of avatars to download")
    parser.add_argument("--jobs", type=int, default=8, help="Concurrent downloads")
    args = parser.parse_args()

    if not DATA_FILE.exists():
        raise SystemExit(f"{DATA_FILE} not found; run main.py first")

    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not items:
        raise SystemExit(f"{DATA_FILE} is empty")
    if args.sort not in items[0]:
        raise SystemExit(f"unknown sort key {args.sort!r}; try one of {', '.join(items[0])}")

    ranked = sorted(items, key=lambda item: item[args.sort], reverse=True)[: args.limit]
    tally: Counter[str] = Counter()

    with (
        httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client,
        ThreadPoolExecutor(max_workers=args.jobs) as pool,
    ):
        futures = [
            pool.submit(fetch_avatar, client, item["face"], args.dir / safe_dirname(item["name"]))
            for item in ranked
        ]
        for position, (item, future) in enumerate(zip(ranked, futures, strict=True), start=1):
            status = future.result()
            tally[status] += 1
            value = item[args.sort]
            shown = f"{value:,}" if isinstance(value, int) else value
            print(f"[{position}/{len(ranked)}] {status:<10} {item['name']} ({args.sort}: {shown})")

    print(
        f"\nSummary: {tally['downloaded']} downloaded, "
        f"{tally['skipped']} skipped, {tally['failed']} failed"
    )


if __name__ == "__main__":
    main()
