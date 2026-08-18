# -*- coding: utf-8 -*-
import sys, urllib.request, re
sys.stdout.reconfigure(encoding='utf-8')
ids = {
 'ghostcite2026': '2602.06718',
 'papertrail2026': '2602.21045',
 'rlam2026': '2601.09749',
 'kaiju2026': '2604.02375',
}
for key, aid in ids.items():
    url = f'https://export.arxiv.org/api/query?id_list={aid}'
    try:
        data = urllib.request.urlopen(url, timeout=40).read().decode('utf-8','ignore')
        entry = re.search(r'<entry>(.*?)</entry>', data, re.DOTALL).group(1)
        title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL).group(1).strip()
        authors = re.findall(r'<name>(.*?)</name>', entry, re.DOTALL)
        year = re.search(r'<published>(.*?)</published>', entry, re.DOTALL).group(1)[:4]
        print(key, '|', title, '|', year, '|', authors)
    except Exception as e:
        print(key, 'ERR', e)
