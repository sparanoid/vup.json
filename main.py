import json
import httpx
from urllib.parse import urlparse

r = httpx.get(
    'https://api.tokyo.vtbs.moe/v1/info',
    timeout=10,
)
vtbs = r.json()

r_vdb = httpx.get(
    'https://vdb.vtbs.moe/json/list.json',
    timeout=10,
)
vtbs_vdb = r_vdb.json()['vtbs']

vdb_dict = {}
vup = {}
vup_desc = {}
vup_room = {}

# Prepare JSON
for user in vtbs_vdb:
    pending_removal = True
    uid = None
    for account in user['accounts']:
        if account.get('platform') == 'bilibili':
            pending_removal = False
            uid = account['id']
    if not pending_removal:
        default_name_lang = user['name']['default']
        vdb_dict[uid] = dict(
            name = user['name'][default_name_lang],
            type = user['type'],
        )

for user in vtbs:
    if 'mid' in user:
        uid = user['mid']
        face_hash = urlparse(user['face']).path

        if str(uid) in vdb_dict.keys():
            type = vdb_dict[str(uid)]['type']
        else:
            type = 'unknown'

        vup[uid] = dict(
            name = user['uname'],
            type = type,
            face = face_hash,
        )
        vup_desc[uid] = dict(
            name = user['uname'],
            type = type,
            face = face_hash,
            sign = user['sign'],
        )
        vup_room[uid] = dict(
            name = user['uname'],
            type = type,
            face = face_hash,
            room_id = user['roomid'],
        )

with open('dist/vup.json', 'w') as file:
    file.write(json.dumps(vup, indent=2, ensure_ascii=False))

with open('dist/vup-desc.json', 'w') as file:
    file.write(json.dumps(vup_desc, indent=2, ensure_ascii=False))

with open('dist/vup-room.json', 'w') as file:
    file.write(json.dumps(vup_room, indent=2, ensure_ascii=False))
