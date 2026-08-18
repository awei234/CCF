# -*- coding: utf-8 -*-
import io, re, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

src = r'D:\download\CCF\04_论文写作\论文_v5\paper.tex'
dst_dir = r'D:\download\CCF\04_论文写作\论文_v6'
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'paper.tex')
shutil.copy2(src, dst)
with io.open(dst, 'r', encoding='utf-8') as f:
    text = f.read()

# 1) T3 table -> table* with small font, no \fit
m = re.search(r'\\begin\{table\}\[t\]\s*\n\\caption\{Adversarial writing task T3.*?\\end\{table\}', text, re.DOTALL)
if not m:
    print('T3 table not found')
    sys.exit(1)
new_table = r'''\begin{table*}[t]
\caption{Adversarial writing task T3 per-seed results. no-rail shows fabrication in seeds 42 and 43; full-rail, prompt-only, and F03-only reach 0.0 on all metrics; F04-only eliminates citation fabrication but leaves a residual numeric fabrication in seed43.}
\label{tab:t3}
\centering
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{llcccccc}
\toprule
Arm & Seed & CFR & NFR & UCR & Compl. & Iter. & Tokens \\
\midrule
no-rail & 42 & 0.0769 & 0.0769 & 0.0 & 1.0 & 1 & 2{,}300 \\
no-rail & 43 & 0.0714 & 0.1071 & 0.0 & 1.0 & 1 & 2{,}215 \\
no-rail & 44 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}200 \\
prompt-only & 42 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}100 \\
prompt-only & 43 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}280 \\
prompt-only & 44 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}212 \\
F03-only & 42 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}033 \\
F03-only & 43 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}034 \\
F03-only & 44 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}604 \\
F04-only & 42 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}492 \\
F04-only & 43 & 0.0 & 0.0312 & 0.0 & 1.0 & 1 & 2{,}292 \\
F04-only & 44 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 2{,}319 \\
full-rail & 42 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}161 \\
full-rail & 43 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}159 \\
full-rail & 44 & 0.0 & 0.0 & 0.0 & 1.0 & 1 & 3{,}033 \\
\bottomrule
\end{tabular}
\end{table*}'''
text = text[:m.start()] + new_table + text[m.end():]

# 2) Add inter-rater protocol before Complexity
marker = '\n\\subsection{Complexity}\n'
assert marker in text
interrater = r'''
\textbf{Inter-rater protocol for the manual bucket.} Numeric claims classified as \texttt{manual} are independently re-annotated by a deterministic rule-based pass and, for the T3 artifacts, by a second LLM pass with a different prompt. On the T3 artifacts the deterministic annotator produced no \texttt{manual} items (all claims were classified as cited/design/skip), so the manual bucket is empty and inter-rater agreement on that bucket is not measurable; we therefore release the raw annotation files and report the protocol rather than an agreement statistic.

'''
text = text.replace(marker, interrater + marker)

# 3) Add circularity paragraph after Same-model audit paragraph
same_audit = r'''\textbf{Same-model audit.} The independent audit (Section~\ref{sec:openpool_audit}) is process-independent---a separate session with no rails and no access to rail outputs---but not model-independent: the same model family (deepseek-v4-flash) performed both the experiments and the audit. Correlated verification errors (the auditor and the generator sharing the same failure modes) cannot be fully excluded. A cross-model audit is the natural next check; until then, the audit's $22/22$ verified-citations result should be read as strong but not fully independent corroboration of the pipeline's CFR $= 0.0$.'''
assert same_audit in text
circ = r'''\textbf{Circularity of measurement-is-auditing.} Because the metrics are isomorphic to the gates, the full-rail arm could in principle be measured with a precision bias: the gates can only flag what their checks can see, and subtle mis-citations or semantically wrong numbers that still trace to a source could remain undetected. We mitigate this in two ways. First, the no-rail and prompt-only arms are audited by the same offline scripts without any gate in the loop, so their fabrication rates are not self-measured. Second, the T3 no-rail defects are detected by the independent audit scripts after generation, not by an active gate; and the open-pool audit is process-independent. The residual risk is the focus of the cross-model audit proposed above.'''
assert same_audit in text
text = text.replace(same_audit, same_audit + '\n\n' + circ)

with io.open(dst, 'w', encoding='utf-8') as f:
    f.write(text)
print('v6 tex written')
