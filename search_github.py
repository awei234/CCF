# -*- coding: utf-8 -*-
import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')
url = 'https://api.github.com/search/repositories'
params = {'q': 'dsh-anchored-standard'}
headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, params=params, headers=headers, timeout=30)
print(r.status_code)
d = r.json()
print('total', d.get('total_count'))
for x in d.get('items', [])[:10]:
    print(x['full_name'], x['html_url'], x.get('description'))
