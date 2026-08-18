# -*- coding: utf-8 -*-
import sys, urllib.parse, urllib.request, re
sys.stdout.reconfigure(encoding='utf-8')
candidates = ['GhostCite', 'CITEVERIFIER', 'PaperTrail', 'R-LAM', 'KAIJU']
for c in candidates:
    print('='*50)
    print('CANDIDATE:', c)
    q = urllib.parse.quote(f'ti:"{c}"')
    url = f'https://export.arxiv.org/api/query?search_query={q}&start=0&max_results=5'
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            data = r.read().decode('utf-8', 'ignore')
        entries = re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)
        if not entries:
            print('  no entries')
        for e in entries:
            t = re.search(r'<title>(.*?)</title>', e, re.DOTALL)
            i = re.search(r'<id>(.*?)</id>', e, re.DOTALL)
            d = re.search(r'<published>(.*?)</published>', e, re.DOTALL)
            print('  -', t.group(1).strip() if t else '?', '|', i.group(1).strip() if i else '?', '|', d.group(1).strip() if d else '?')
    except Exception as ex:
        print('  ERROR', ex)
