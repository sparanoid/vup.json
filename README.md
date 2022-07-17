# vup.json

Extract bilibili vup info from vtbs.moe with user avatars

## Why?

- Extract and merge live [vtbs.moe](https://vtbs.moe/) database and [vdb](https://vdb.vtbs.moe/) with only valid vup info
- Make the final output much smaller. Better suited for FaaS platforms and low-end machines.
- Make output static and can be deployed to any web server.

## Schema

`vup.json`:

```json
{
  "375504219": {
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg"
  }
}
```

`vup-desc.json`:

```json
{
  "375504219": {
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg",
    "sign": "holoIive二期生、虚拟女仆、湊(みなと)あくあ！❖担当画师：がおう协力：湊阿库娅字幕组。商务合作与问题反馈请私信"
  }
}
```

`vup-room.json`:

```json
{
  "375504219": {
    "name": "湊-阿库娅Official",
    "type": "vtuber",
    "face": "/bfs/face/a7195c09c6ba4722966d745d6f692035d3fe4d95.jpg",
    "room_id": 14917277
  }
}
```

## Types

Only the folloing types are included from upstream APIs:

- `vtuber`
- `group`
- `fan`
- `unknown`

## License

MIT
