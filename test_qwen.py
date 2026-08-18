# -*- coding: utf-8 -*-
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')
key = 'bb31fou8iyg9aR9lKEq9UCOSCzZwSX'
url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
for model in ['qwen-turbo', 'qwen-turbo-latest', 'qwen-plus', 'qwen-max']:
    try:
        r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 10}, timeout=60)
        print(model, r.status_code, r.text[:300])
    except Exception as e:
        print(model, 'ERR', e)
