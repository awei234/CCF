# -*- coding: utf-8 -*-
import json, sys, time, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

candidates = [
    'GhostCite: Citation verification in large language models',
    'CITEVERIFIER: Verifying citations in scientific literature',
    'PaperTrail: Provenance grounded scientific writing',
    'R-LAM: Reinforcement learning for agentic workflows',
    'KAIJU: Execution constrained agent framework',
]

def openalex(title):
    q = urllib.parse.quote(f'"{title}"')
    url = f'https://api.openalex.org/works?filter=title.search:{q}&per-page=3&select=title,publication_year,doi,authorships'
    req = urllib.request.Request(url, headers={'User-Agent': 'CCF-ResearchBot/1.0 (mailto:vergil@local)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))

for c in candidates:
    print('='*60)
    print('CANDIDATE:', c)
    try:
        d = openalex(c)
        hits = d.get('results') or []
        if not hits:
            print('  no hits')
        for h in hits:
            print('  -', h.get('publication_year'), h.get('title'), h.get('doi'))
    except Exception as e:
        print('  ERROR', e)
    time.sleep(1)
