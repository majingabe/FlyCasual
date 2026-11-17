---
name: token-saver
description: Work in a token- and compute-efficient way in Claude Code sessions, based on 2025-2026 measurements of what actually drives coding-agent cost - fewer model turns, cache-friendly behavior, a lean per-turn preamble, short output, and no needless subagents or restarts. Use this whenever the user mentions tokens, usage limits, usage credits, cost, spend, budget, running low on usage, "be efficient", "keep it cheap", or asks why a session used so much - and for long or large multi-step work (big refactors, many-file changes, long debugging sessions) even if they never say "tokens". Also use it before deciding to spawn subagents, switch models, compact, or start over.
---

# Token Saver

The target is the lowest cost per **successful** task. A run that saves tokens and then fails has wasted all of them, so never drop the verification that correctness needs. Cut the waste around it.

## How cost actually accrues

Every model call resends the whole context. With prompt caching (automatic in Claude Code), the unchanged prefix is re-read at a small fraction of the normal input price and only new content is processed in full:

    cost ≈ turns × cached prefix  +  new content  +  output (thinking included, 5× the input price)

In 600 real coding-agent trajectories, turn count explained 84% of cost variance and tool-output size only 4%. 98.6% of input tokens were cache hits, and the median tool output was 118-286 tokens. Two things follow. Removing turns matters far more than shrinking outputs. And anything that rewrites the cached prefix is expensive.

The levers, in priority order:

1. Fewer turns
2. Keep the cache intact
3. Keep the per-turn preamble small
4. Keep output short

## 1. Fewer turns (the biggest lever)

- **Batch independent calls in one message**: reads of several files, a few greps, `git status` plus `git diff`. Parallel calls cut turns, and in a deep-research study they also raised accuracy.
- **Read what you already know you'll need, together and up front**, not one file per turn. Preloading the needed context cut model calls by about 36% compared with searching on demand.
- **Chain shell steps whose result won't change your next move**, for example `npm ci && npm test` or `git status && git diff --stat`. Keep steps separate only when you must inspect output in between.
- **Locate, then plan, then edit, then verify the plan.** Say what you intend to change before editing. Afterwards, check it with the narrowest test that proves it, and run the full suite once at the end. A plan-then-verify method used 6-68% fewer tokens at the same solve rate. The savings came from less re-reading and re-testing after edits.
- **Don't re-read a file to confirm an edit.** The edit tool reports a failure if there is one.
- **Fix a done-criterion before you start and stop when it's met.** Open-ended review-and-polish loops are where agent tokens go: 59% of tokens in one study.
- **Break failure loops.** If the same error survives two different fixes, stop nudging. Re-diagnose from the actual error and code, or ask the user.
- **Don't re-derive facts already established** in the conversation, such as paths, versions or test commands.

## 2. Keep the cache intact

A cache hit needs an exact prefix match. Each of these actions forces the next call to re-read everything at full price:

- **Switching models mid-task.** Each model has its own cache. Pick the model at the start and switch at natural breaks. Changing the effort level keeps the cache on Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1+.
- **Connecting or removing MCP servers, or adding deny rules mid-task.** Tool definitions are part of the prefix.
- **Running `/compact` mid-task.** It rebuilds the conversation layer. Compact at task boundaries. `/clear` between unrelated tasks costs nothing. `/rewind` out of a dead end reuses an earlier cache entry.
- **Long idle gaps.** The cache expires after 1 hour on plan usage. It expires after 5 minutes once usage credits or API billing apply.

When the user proposes one of these mid-task, name the one-time cost in a sentence, give a recommendation, and let them decide. Never trim or mask earlier history yourself. In one study, masking old tool outputs shrank the prompt by 33% but raised uncached prefill by 608%, and the runs failed the quality gate.

## 3. Keep the per-turn preamble small

The fixed block sent with every call is the system prompt, the tool schemas and CLAUDE.md. That block multiplied by the number of turns sets most of the bill. Differences in this preamble alone produced 3× cost gaps between agent harnesses running the same model. Filtering unused tool schemas, worth 21K-57K tokens per turn, was the one lever that saved money reliably.

- Don't load deferred tool schemas, or start using a server, unless the task needs it.
- Prefer an installed CLI (`git`, `gh`, `jq`) over an equivalent MCP tool when both work.
- Suggest these to the user rather than doing them yourself:
  - Disable unused MCP servers in `/mcp`.
  - Keep CLAUDE.md under ~200 lines and move workflow instructions into skills.
  - Record repo facts you discovered, such as build and test commands and gotchas, in CLAUDE.md. That stops later sessions rediscovering them. Injecting this kind of environment know-how was a main source of an 18-31% cost cut in one study.

## 4. Big outputs: capture once, query many times

Most tool outputs are small, so leave them alone. For output you can predict will be huge, such as full test or build logs, large JSON or generated files, write it to a file once and query the file:

```bash
make > /tmp/build.log 2>&1; echo "exit=$?"; wc -l < /tmp/build.log; tail -n 30 /tmp/build.log
grep -n -i -m 20 "error" /tmp/build.log
```

You never have to re-run the expensive command to look at another part. Claude Opus and Sonnet 4.6 showed no detectable accuracy loss when reading large tool output from files instead of inline.

Don't blanket-truncate output (for example `| head -20`) when you can't predict where the important part is. In Claude Code, aggressive compression of tool output cut tokens by 38% but raised the billed cost by 7% and lowered patch success, because the agent had to fetch again what was cut.

## 5. Output and thinking

Output, including hidden thinking, costs 5× input.

- Answer directly. Don't restate the request, narrate each tool call, or paste code the user can already see in the diff.
- End with a short summary: what changed, what was verified, and what is left.
- The effort level sets reasoning depth. Prompting yourself to think less is not the lever. For routine work, suggest the user lower `/effort`: in one study, low effort used about 43% fewer output tokens with no change in outcomes on routine agent tasks. Keep full effort for hard debugging and design.

## 6. Subagents and agent teams: only to isolate noise

Each subagent starts cold, re-reads context and pays for its own turns. Agent teams use about 7× the tokens of a normal session. The research points the same way:

- A single agent matched a multi-agent pipeline's quality with 86% fewer tokens.
- Self-consistency matched or beat multi-agent debate in 93% of settings.
- Delegating turns to a cheaper model raised the total cost in half the settings tested.

Spawn a subagent only when it will absorb a large, noisy exploration whose raw output you would otherwise carry for the rest of the session, and its answer fits in a short summary. Give it a smaller model when the job is simple. Otherwise, do the work inline.

## 7. Continue rather than restart

Abandoning a run to start fresh rarely pays. Across 147,000 traces, plain continuation beat restart policies, with a higher solve rate at lower cost, in 216 of 224 settings. Course-correct in place, or `/rewind` to the last good checkpoint.

## Measured to backfire: don't bother

- **Minifying code or stripping comments to save tokens.** It cut input tokens by 42% but lost 12 points of solve rate.
- **Compact data formats (TOON, TRON) instead of JSON or plain text.** They cost 9-14 points of accuracy, and TOON broke parallel tool calls.
- **Blanket truncation of tool output, or compression proxies.** Token reduction barely tracks cost reduction (r = 0.15).
- **Editing or masking old history in a cached session.**
- **Kill-and-restart heuristics.**
- **Local-model routing or prompt-compression middleware.** These need extra infrastructure, so a session cannot do them by itself.

## Measure, don't guess

`scripts/session_cost.py` in this skill's directory reads a Claude Code transcript and reports:

- the number of model calls, and the share that batched tool calls
- the cache-hit share and full cache rebuilds
- output and thinking tokens
- repeated reads of the same file and repeated commands
- an estimate at list prices

```bash
python3 <this-skill-dir>/scripts/session_cost.py            # newest transcript under ~/.claude/projects
python3 <this-skill-dir>/scripts/session_cost.py path/to/session.jsonl
```

Run it when the user asks where their usage went, or to compare two ways of working. For sources, numbers and caveats, read `references/evidence.md`, but only when the user asks for justification.
