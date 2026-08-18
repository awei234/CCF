# Abstract

Compares Semantic Search (vector index over the repository) and Deep Agentic Search (planning agent delegates exploration to a subagent in an isolated context window to protect against context pollution/rot) on SWE-QA repository-level code QA. Semantic search answered 65.2% of questions correctly vs 46.2% for deep agentic search at less than half the cost. A failure taxonomy shows deep agentic search introduced a new failure class: 41.8% of its failures occurred at the planner-subagent hand-off, usually silent, ending in a fluent, confident but wrong answer.
