# -*- coding: utf-8 -*-
import json, os, sys, glob
sys.stdout.reconfigure(encoding='utf-8')
base = os.path.expanduser('~/.jiuwenswarm/agent/workspace/workspace/v5-adversarial-T3/experiments/exp1')
for arm in ['no-rail', 'f03Only', 'f04Only', 'full-rail', 'promptOnly']:
    for seed in ['42','43','44']:
        p = os.path.join(base, arm, 'seed'+seed, 'numbers_audit.json')
        if not os.path.exists(p):
            print(arm, seed, 'NO FILE')
            continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print(arm, seed, 'ERR', e)
            continue
        # d may be a list or dict; count items with source/manual fields
        if isinstance(d, dict):
            items = d.get('items') or d.get('claims') or d.get('numbers') or []
        else:
            items = d
        n_manual = sum(1 for x in items if isinstance(x, dict) and x.get('classification') == 'manual')
        n_total = len(items)
        print(arm, seed, 'total', n_total, 'manual', n_manual)
