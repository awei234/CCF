# -*- coding: utf-8 -*-
import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
key = '5d964f20957244b984e467ba36f2f227.xBg66BKQWy3f6nXU'
url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
for model in ['glm-4-flash', 'glm-4-air', 'glm-4-flashx']:
    try:
        r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 10}, timeout=60)
        print(model, r.status_code, r.text[:300])
    except Exception as e:
        print(model, 'ERR', e)
