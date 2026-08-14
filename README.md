# vup.json

Extract bilibili vup info from vtbs.moe with user avatars

## Why?

- Extract and merge live [vtbs.moe](https://vtbs.moe/) database and [vdb](https://vdb.vtbs.moe/) with only valid vup info
- Make the final output much smaller. Better suited for FaaS platforms and low-end machines.
- Make output static and can be deployed to any web server.

## Outputs

Every file under `dist/` is a projection of the same record set, rebuilt hourly.
Object variants are keyed by bilibili uid; `*-array.json` variants are flat lists
with the uid folded in as the first field.

| File | Fields |
| --- | --- |
| `vup.json` | `name`, `type`, `room`, `face`, `group_name` |
| `vup-desc.json` | the above plus `sign` |
| `vup-full.json` | the above plus `followers`, `videos`, `guards` |
| `vup-slim.json` | `name`, `type`, `room`, `group_name` |
| `vup-room.json` | as `vup.json`, but `room` is named `room_id` (deprecated) |
| `vup-array.json`, `vup-desc-array.json`, `vup-full-array.json`, `vup-slim-array.json` | array forms of the matching object variant, prefixed with `uid` |

`vup.json`:

```json
{
  "375504219": {
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "room": 14917277,
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg",
    "group_name": "Hololive"
  }
}
```

`vup-full.json`:

```json
{
  "375504219": {
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "room": 14917277,
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg",
    "sign": "holoIive二期生、虚拟女仆、湊(みなと)あくあ！❖担当画师：がおう",
    "group_name": "Hololive",
    "followers": 744538,
    "videos": 492,
    "guards": 1
  }
}
```

`vup-full-array.json`:

```json
[
  {
    "uid": 375504219,
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "room": 14917277,
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg",
    "sign": "holoIive二期生、虚拟女仆、湊(みなと)あくあ！❖担当画师：がおう",
    "group_name": "Hololive",
    "followers": 744538,
    "videos": 492,
    "guards": 1
  }
]
```

`face` is a path only; prefix it with a bilibili image host such as
`https://i0.hdslb.com` to resolve it.

## Types

Only the following types are included from upstream APIs:

- `vtuber`
- `group`
- `fan`
- `unknown`

## Development

Requires [uv](https://docs.astral.sh/uv/). Rebuild everything under `dist/`:

```sh
uv run main.py
```

The build refuses to write if an upstream fetch keeps failing, or if the record
count drops more than 10% below what is already committed — so a partial
upstream response cannot overwrite a good dataset.

Lint and format:

```sh
uv run ruff check .
uv run ruff format .
```

Download avatars for the top VUPs into `tmp/` (needs the `avatars` group for Pillow):

```sh
uv run --group avatars avatar.py --limit 300 --sort followers
```

## License

MIT
