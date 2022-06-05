import json
import httpx

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
        data[uid] = dict(
            name = user['uname'],
            face = user['face'],
            sign = user['sign'],
        )

with open('vup.json', 'w') as file:
    file.write(json.dumps(data, indent=2, ensure_ascii=False))
