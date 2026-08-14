"""Build the vup.json dataset from the vtbs.moe live API and the vdb database.

Fetches both upstream sources, merges them into one record per bilibili VUP, and
writes every projection under dist/ that downstream consumers read.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

VDB_URL = "https://vdb.vtbs.moe/json/list.json"
VTBS_URL = "https://api.vtbs.moe/v1/info"

DIST = Path("dist")

REQUEST_TIMEOUT = 30.0
REQUEST_ATTEMPTS = 4

# Upstream occasionally serves a truncated list. Refuse to publish a dataset that
# lost more than this fraction of the records already committed to dist/.
MAX_SHRINK = 0.10


@dataclass(frozen=True, slots=True)
class Vup:
    uid: int
    name: str
    type: str
    room: int
    face: str
    sign: str
    group_name: str
    followers: int
    videos: int
    guards: int

    @property
    def room_id(self) -> int:
        """Alias kept for the deprecated vup-room.json schema."""
        return self.room


# Output stem -> field order. Every file is a projection of Vup, so adding a
# variant is a matter of listing its fields here.
LAYOUTS: dict[str, tuple[str, ...]] = {
    "vup": ("name", "type", "room", "face", "group_name"),
    "vup-desc": ("name", "type", "room", "face", "sign", "group_name"),
    "vup-full": (
        "name",
        "type",
        "room",
        "face",
        "sign",
        "group_name",
        "followers",
        "videos",
        "guards",
    ),
    "vup-slim": ("name", "type", "room", "group_name"),
    "vup-room": ("name", "type", "room_id", "face", "group_name"),
}

# Layouts that also ship a flat array form, with uid folded in as the first key.
# vup-room is excluded: it is deprecated and nothing consumes it that way.
ARRAY_LAYOUTS = ("vup", "vup-desc", "vup-full", "vup-slim")


def fetch_json(url: str) -> Any:
    """GET and decode `url`, retrying transient failures with a backoff."""
    last_error: Exception | None = None
    for attempt in range(1, REQUEST_ATTEMPTS + 1):
        try:
            response = httpx.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as error:  # ValueError covers JSONDecodeError
            last_error = error
            if attempt == REQUEST_ATTEMPTS:
                break
            delay = 2**attempt
            print(f"{url} failed ({error!r}); retrying in {delay}s", file=sys.stderr)
            time.sleep(delay)
    raise SystemExit(f"giving up on {url} after {REQUEST_ATTEMPTS} attempts: {last_error!r}")


def load_vdb() -> dict[str, tuple[str, str]]:
    """Map bilibili uid -> (type, group_name) for everyone tracked by vdb."""
    payload = fetch_json(VDB_URL)
    entries = payload.get("vtbs") if isinstance(payload, dict) else None
    if not entries:
        raise SystemExit("vdb returned no entries")

    index: dict[str, tuple[str, str]] = {}
    for user in entries:
        # A few vdb entries list more than one bilibili account. Only the last is
        # registered, matching how this dataset has always been built.
        uid = None
        for account in user.get("accounts", ()):
            if account.get("platform") == "bilibili":
                uid = account["id"]
        if uid is not None:
            index[uid] = (user["type"], user.get("group_name", ""))

    print(f"vdb: {len(index)} bilibili accounts")
    return index


def load_vups(vdb: dict[str, tuple[str, str]]) -> list[Vup]:
    """Merge the vtbs live info with vdb metadata into one record per VUP."""
    payload = fetch_json(VTBS_URL)
    if not isinstance(payload, list) or not payload:
        raise SystemExit("vtbs returned no entries")

    # Deregistered accounts (账号已注销) come back without face/sign/topPhoto.
    live = [user for user in payload if "mid" in user and "face" in user]

    records = []
    for user in sorted(live, key=lambda item: item["mid"]):
        uid = user["mid"]
        vup_type, group_name = vdb.get(str(uid), ("unknown", ""))
        records.append(
            Vup(
                uid=uid,
                name=user["uname"],
                type=vup_type,
                room=user["roomid"],
                face=urlparse(user["face"]).path,
                sign=user.get("sign", ""),
                group_name=group_name,
                followers=user["follower"],
                videos=user["video"],
                guards=user["guardNum"],
            )
        )

    print(f"vtbs: {len(records)} live records out of {len(payload)} returned")
    return records


def check_not_shrunk(records: list[Vup]) -> None:
    """Abort before writing if upstream lost a large share of the known records."""
    previous = DIST / "vup.json"
    if not previous.exists():
        return
    try:
        known = len(json.loads(previous.read_text(encoding="utf-8")))
    except ValueError:
        return  # committed file is unreadable; nothing to compare against

    floor = int(known * (1 - MAX_SHRINK))
    if len(records) < floor:
        raise SystemExit(
            f"refusing to publish: {len(records)} records, down from {known} "
            f"(floor {floor}). Upstream is probably serving a partial list."
        )


def project(record: Vup, fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: getattr(record, field) for field in fields}


def write_json(stem: str, payload: Any) -> None:
    path = DIST / f"{stem}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")


def main() -> None:
    DIST.mkdir(exist_ok=True)

    records = load_vups(load_vdb())
    check_not_shrunk(records)

    for stem, fields in LAYOUTS.items():
        write_json(stem, {record.uid: project(record, fields) for record in records})

    for stem in ARRAY_LAYOUTS:
        fields = LAYOUTS[stem]
        write_json(f"{stem}-array", [{"uid": r.uid, **project(r, fields)} for r in records])


if __name__ == "__main__":
    main()
