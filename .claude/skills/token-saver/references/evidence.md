# Evidence behind token-saver

Every source was read at the source: arXiv abstracts through the arXiv API, plus Anthropic's own documentation. Searched November 2026. Most papers are recent preprints that have not been peer reviewed, and many studies use one model family or one benchmark. Treat each number as "measured once, in that setup", not as a law.

## Contents

1. What drives cost
2. Caching
3. Preamble and tools
4. Context and output handling
5. Planning, verification and loops
6. Reasoning effort and output
7. Multi-agent and delegation
8. Restarting
9. Measured to backfire or not applicable
10. Anthropic documentation used

## 1. What drives cost

- **TurnCost** (arXiv 2610.15093, Oct 2026). Studied 600 public coding-agent trajectories, across two scaffolds and two models.
  - Turn count explains 84% of the variance in log trajectory cost; mean observation size explains 4%.
  - 98.6% of input tokens are served from the prefix cache.
  - The median observation is 118-286 tokens; huge build logs sit near the 99th percentile.
  - Flat input pricing overestimates loop cost by about 7×.
  - Delegating to a cheaper model raised cost in half the settings.
  - Caveat: the paper does not show that turns can be removed while keeping task success fixed.
  - https://arxiv.org/abs/2610.15093
- **Token Reduction Is Not Cost Reduction** (2607.12161, Jul 2026). Tested against an unmodified Claude Code baseline.
  - The strongest tool-output compression cut delivered tokens by 38.4% but raised billed cost by 6.8%.
  - Token reduction vs. cost reduction: Pearson r = 0.15.
  - Cache creation and cache reads dominate input-side cost.
  - Compression changed trajectories, adding retrieval, testing and turns, and it lowered patch success on a SWE-bench Go subset.
  - https://arxiv.org/abs/2607.12161
- **Tokenomics** (2601.14470, Jan 2026), using ChatDev with GPT-5. The iterative code-review stage consumed 59.4% of tokens, and input tokens were 53.9% of the total. https://arxiv.org/abs/2601.14470

## 2. Caching

- **Don't Break the Cache** (2601.06007, Jan 2026). Covers OpenAI, Anthropic and Google.
  - Prompt caching cut API cost by 41-80% on multi-turn agent tasks.
  - Keeping dynamic content at the end of the prompt, and dynamic tool results out of the cached block, beat naive full-context caching.
  - https://arxiv.org/abs/2601.06007
- **The Physical Cost of Context** (2610.34763, Oct 2026).
  - Preloading ten retrieved blocks ("Eager") cut model calls by 35.7% compared with on-demand grep.
  - Keeping only the last five observations ("Mask-5") cut prompt volume by 33.3% but threw away 135.9K reusable tokens per task. Uncached prefill rose by 608.5% and the runs missed the quality gate.
  - https://arxiv.org/abs/2610.34763
- **Silent and Costly** (2610.34817, Oct 2026). Prompt-caching mis-integrations in agent code usually fail silently. Measure cache hits rather than assuming them. https://arxiv.org/abs/2610.34817

## 3. Preamble and tools

- **What Does a Harness Buy? Tokens, Mostly** (2610.04433, Oct 2026). Compared Claude Code, mini-SWE-agent and OpenCode on SWE-bench Verified.
  - Pass rates were roughly equivalent across harnesses.
  - Cost per task differed by up to 3×. The gap was set by the per-step preamble (system prompt plus tool schemas) multiplied by the number of steps.
  - https://arxiv.org/abs/2610.04433
- **Empirical Cost Attribution of Context-Compression Gateways** (2609.22114, Aug 2026). Tested with Claude Code and Codex.
  - Tool-schema filtering removed 21K-57K tokens per turn and was the only reliably positive lever.
  - Single-shot compression benchmarks say nothing about multi-turn cost.
  - https://arxiv.org/abs/2609.22114
- **TokenEconomizer** (2610.22732, Oct 2026). Cut cost by 18.4-31% across Claude Code, Codex and Copilot CLI with comparable success. It did this by:
  - injecting environment-specific micro-skills
  - pruning tools that were never relevant
  - stepping into unproductive failure loops

  https://arxiv.org/abs/2610.22732

## 4. Context and output handling

- **Same Simulation, Different Evidence** (2610.26836, Oct 2026). Reading a large tool report through a file and section index, instead of inline, cost GPT-5.1/5.2 8-11 points. Claude Opus 4.6 and Sonnet 4.6 showed no detectable cost. Naming the authoritative output helped. https://arxiv.org/abs/2610.26836
- **What Does Context Compression Cost an Agent?** (2608.16370, Aug 2026). Compression can leave completion unchanged while multiplying retrieval calls; for GPT-5.5, calls went from 21 to 64. https://arxiv.org/abs/2608.16370
- **Towards Reliable Context Compression** (2608.06503, Aug 2026). Compaction weakens the influence of recent steps and causes repeated exploration and unstable runs. https://arxiv.org/abs/2608.06503
- **The Complexity Trap** (2508.21433, Aug 2025). On SWE-agent, simple observation masking halved cost compared with the raw agent and matched LLM summarization. This result is harness-level and conflicts with 2610.34763 once prefix caching is counted, so the skill does not tell the agent to mask history. https://arxiv.org/abs/2508.21433

## 5. Planning, verification and loops

- **FlowPlan** (2611.13241, Nov 2026). Localizing, planning the edit explicitly and then verifying against the plan cost no significant solve rate.
  - Haiku 4.5 used 0.32-0.74× the baseline tokens.
  - Sonnet 5 used 0.72-0.94× the baseline tokens.
  - The savings came from less re-reading and re-testing after edits.
  - https://arxiv.org/abs/2611.13241
- **W&D: Scaling Parallel Tool Calling** (2602.07359, Feb 2026). Parallel tool calls within one step cut the turns needed and raised accuracy on deep-research benchmarks. https://arxiv.org/abs/2602.07359
- **Why Pay for Long Reasoning When Rewrite Do Trick?** (2611.03852, Nov 2026). Compact state records shortened later reasoning and cut repeated verification. Tested on open-weight models only. https://arxiv.org/abs/2611.03852

## 6. Reasoning effort and output

- **Low Reasoning Effort Is Enough for Routine Office Work** (2608.03169, Aug 2026). With GPT-5.6, low effort used about 43% fewer output tokens and 20% less time, with identical rule-following over 840 runs. https://arxiv.org/abs/2608.03169
- **Chain of Draft** (2502.18600, Feb 2025). Terse intermediate reasoning matched CoT using as little as 7.6% of the tokens, on older non-thinking models. On models that always think, effort is the real control. https://arxiv.org/abs/2502.18600
- Most 2026 efficient-reasoning papers (for example ThinkPrune-style pruning, length-penalty RL and early-exit decoding) need training or decoder access. A session cannot use them.

## 7. Multi-agent and delegation

- **The Illusion of Agentic Complexity** (2606.30524, Jun 2026). A single-agent pipeline matched multi-agent quality with 86% fewer tokens at twice the speed. https://arxiv.org/abs/2606.30524
- **Think More or Read More?** (2610.23246, Oct 2026). Self-consistency matched or beat debate in 93% of 980 settings. Communication pays only when its accuracy gain exceeds the reasoning room it uses up. https://arxiv.org/abs/2610.23246
- **Beyond the Model: Harness Effects** (2609.32459, Sep 2026). Task-specific subagents gave stable gains. General subagents and context compression could hurt. https://arxiv.org/abs/2609.32459
- **When Independent Sampling Outperforms Agentic Reasoning** (2605.08478, May 2026). For self-contained algorithmic problems, k independent attempts beat agent loops on cost. https://arxiv.org/abs/2605.08478

## 8. Restarting

- **Continue or Restart?** (2610.35971, Oct 2026). Across 147,002 traces, early failure prediction within a task was at chance level (AUC about 0.50). Plain continuation reached higher solve rates at lower mean cost than restart policies in 216 of 224 configurations. https://arxiv.org/abs/2610.35971

## 9. Measured to backfire or not applicable

- **Minification** (2606.01326, May 2026): 42% fewer input tokens but -12 points of resolution on SWE-bench Verified. https://arxiv.org/abs/2606.01326
- **Notation Matters: TOON/TRON** (2605.29676, May 2026): up to 18-27% fewer tokens, but 9-14 points lower accuracy, and TOON collapsed parallel tool-call output. https://arxiv.org/abs/2605.29676
- **Local-Splitter** (2604.12301, Apr 2026): 45-79% cloud-token savings from local routing plus prompt compression. It needs a local model and a proxy, so it is not applicable inside a session. https://arxiv.org/abs/2604.12301

## 10. Anthropic documentation used

- Claude Code, "Manage costs effectively": https://code.claude.com/docs/en/costs
  - thinking is billed as output
  - agent teams use about 7× tokens
  - keep CLAUDE.md under 200 lines
  - `/clear` costs nothing
  - MCP tool definitions are deferred by default
- Claude Code, "Prompt caching": https://code.claude.com/docs/en/prompt-caching
  - a model switch means no cache hits on the next request
  - effort changes keep the cache on Fable 5.1+ and the 5.5 models
  - MCP connect/remove and deny rules invalidate the cache
  - compaction rebuilds the conversation layer; `/rewind` reuses an earlier entry
  - the TTL is 1 hour within plan usage and 5 minutes on usage credits
- API pricing, with output at 5× input on current models: https://platform.claude.com/docs/en/about-claude/pricing
