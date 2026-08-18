# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\download\CCF\04_论文写作\论文_v6\paper.tex'
s = io.open(p, encoding='utf-8').read()

# Insert after the detector paragraph (line ~60) before 'All three share...'
marker = 'All three share the detector-centered assumption that fabrication is found after the fact.'
assert marker in s, 'marker not found'
insert = r'''Large-scale citation-verification systems such as GhostCite \citep{ghostcite2026} quantify hallucinated citations across millions of references, and provenance-grounding interfaces such as PaperTrail \citep{papertrail2026} attach claim-level evidence to generated text. Execution-constrained agent frameworks such as KAIJU \citep{kaiju2026} and R-LAM \citep{rlam2026} similarly operationalize contracts at execution time. These systems remain detector- or interface-level; none manipulates the contract as a controlled experimental variable with paired seeds as we do here. '''
s = s.replace(marker, insert + marker)

io.open(p, 'w', encoding='utf-8').write(s)
print('patched related work')
