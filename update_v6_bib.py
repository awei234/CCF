# -*- coding: utf-8 -*-
import io
p = r'D:\download\CCF\04_论文写作\论文_v6\references.bib'
s = io.open(p, encoding='utf-8').read()
add = '''
@article{ghostcite2026,
  title={GhostCite: A Large-Scale Analysis of Citation Validity in the Age of Large Language Models},
  author={Xu, Zuyao and Qiu, Yuqi and Sun, Lu and Miao, Fasheng and Wu, Fubin and Li, Xiang and Wang, Xinyi and Lu, Haozhe and Zhang, Zhengze and Hu, Yuxin and others},
  journal={arXiv preprint arXiv:2602.06718},
  year={2026}
}
@article{papertrail2026,
  title={PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based Scholarly Q\&A},
  author={Martin-Boyle, Anna and Leckey, Cara A. C. and Brown, Martha C. and Kaur, Harmanpreet},
  journal={arXiv preprint arXiv:2602.21045},
  year={2026}
}
@article{rlam2026,
  title={R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation},
  author={Sureshkumar, Suriya},
  journal={arXiv preprint arXiv:2601.09749},
  year={2026}
}
@article{kaiju2026,
  title={KAIJU: An Executive Kernel for Intent-Gated Execution of LLM Agents},
  author={Guerin, Cormac and Guerin, Frank},
  journal={arXiv preprint arXiv:2604.02375},
  year={2026}
}
'''
io.open(p, 'w', encoding='utf-8').write(s + add)
print('bib updated')
