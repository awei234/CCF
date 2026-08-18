# -*- coding: utf-8 -*-
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')
key = 'sk-ws-H.EPHLYXH.jxql.MEUCIGhJJmeXdmdCH0SFVOJ3f9IkU7aFNBui32ULdkMPf8ANAiEApJXsXwd6SVR-wpgd6KlCKg--k2-zfB6HvUmYt3-OnVE'
url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
models = [
    'qwen-turbo', 'qwen-turbo-latest', 'qwen-plus', 'qwen-plus-latest',
    'qwen-max', 'qwen-max-latest', 'qwen-flash', 'qwen-long',
    'qwen3-turbo', 'qwen3-8b', 'qwen2.5-7b-instruct', 'qwen2.5-14b-instruct',
]
for model in models:
    try:
        r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}, timeout=40)
        if r.status_code == 200:
            print(model, 'OK')
        else:
            print(model, r.status_code, r.text[:120].replace('\n',' '))
    except Exception as e:
        print(model, 'ERR', e)
