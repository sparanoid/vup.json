import json
import httpx
from urllib.parse import urlparse

r = httpx.get(
    'https://api.tokyo.vtbs.moe/v1/info',
    timeout=10,
)
vtbs = r.json()
vup = {}
vup_desc = {}

# Prepare JSON
for user in vtbs:
    if 'mid' in user:
        uid = user['mid']
        face_hash = urlparse(user['face']).path
        vup[uid] = dict(
            name = user['uname'],
            face = face_hash,
        )
        vup_desc[uid] = dict(
            name = user['uname'],
            face = face_hash,
            sign = user['sign'],
        )

with open('vup.json', 'w') as file:
    file.write(json.dumps(vup, indent=2, ensure_ascii=False))

with open('vup-desc.json', 'w') as file:
    file.write(json.dumps(vup_desc, indent=2, ensure_ascii=False))
