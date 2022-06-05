import json
import httpx
from urllib.parse import urlparse

r = httpx.get(
    'https://api.tokyo.vtbs.moe/v1/info',
    timeout=10,
)
vtbs = r.json()
data = {}

# Prepare JSON
for user in vtbs:
    if 'mid' in user:
        uid = user['mid']
        face_hash = urlparse(user['face']).path
        data[uid] = dict(
            name = user['uname'],
            face = face_hash,
            sign = user['sign'],
        )

with open('vup.json', 'w') as file:
    file.write(json.dumps(data, indent=2, ensure_ascii=False))
