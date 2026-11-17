---
name: token-saver
description: Checklist for lower cost per successful task in Claude Code - fewer model turns, cache-safe choices, lean context, short output, no needless subagents or restarts - based on 2025-2026 measurements of coding-agent cost. Use when the user asks to save tokens, usage or credits, asks why a session cost so much, or asks whether to switch models, compact, clear, restart or spawn subagents to save money; and when the user invokes it for a long, many-file task.
---

# Token Saver

Aim for the lowest cost per **successful** task. Never drop the verification that correctness needs. In Claude Code, almost all of the context is re-read from the prompt cache on every model call, so the bill grows with the **number of turns** much more than with the size of each output. Output, including hidden thinking, costs 5× input.

## While working

1. **Batch.** Put independent reads, greps and commands in one message. Read the files you know you'll need together, up front.
2. **Chain** shell steps whose result won't change your next move: `cmd1 && cmd2`.
3. **Plan, then verify the plan.** Locate the code, state the change, then edit. Check it with the narrowest test, and run the full suite once at the end. Don't re-read a file to confirm an edit.
4. **Have a done-criterion and stop when it's met.** Skip open-ended polish passes.
5. **If the same error survives two different fixes, stop.** Re-diagnose from the actual error, or ask the user.
6. **For output you can predict is huge** (logs, big JSON), write it to a file once and use `grep` or `tail` on the file. Don't re-run the command, and don't blindly `| head` output whose important part you can't predict. Most outputs are small: leave them alone.
7. **Do it inline.** Spawn a subagent only to absorb a large, noisy exploration whose raw output you would otherwise carry, and whose answer fits in a short summary.
8. **Keep going.** Course-correct rather than restarting from scratch; restarting rarely pays.
9. **Keep replies short:** what changed, what was verified, what is left.

## When the user asks how to spend less

Answer in a few sentences with one clear recommendation. Quote research figures only if asked; they are in `references/evidence.md`. The facts you need:

- **`/model` switch mid-session:** the next call re-reads the whole context without cache hits, a one-time cost. Best done at a task boundary, right after `/clear` or `/compact`.
- **`/effort`:** lowering it for routine work cuts thinking tokens, and on Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1+ it keeps the cache. This is usually the first lever.
- **`/compact`:** worth it when the context is large and plenty of work remains. While the cache is warm it costs little, and every later turn re-reads less. Run it at a sub-task boundary and say what to keep (`/compact keep the API decisions and failing tests`), because dropped details get re-read later.
- **`/clear`:** free. Use it between unrelated tasks.
- **`/rewind`:** use it to drop a dead end, not a restart.
- **MCP servers and CLAUDE.md:** every turn re-sends the tool definitions and CLAUDE.md. Disable unused servers in `/mcp`, prefer CLIs like `gh`, and keep CLAUDE.md short. Recording build and test commands in CLAUDE.md saves later sessions from rediscovering them.
- **Cache lifetime:** the cache expires after about 1 hour of idle time on plan usage, and after about 5 minutes on usage credits or API billing.

## Not worth it (measured to backfire)

- minifying code or stripping comments
- TOON-style compact formats
- blanket truncation or compression proxies
- trimming old history in a cached session
- kill-and-restart heuristics

## Measure

`python3 <this-skill-dir>/scripts/session_cost.py [transcript.jsonl]` reports turns, cache-hit share, cache rebuilds, batching, repeated reads and commands, and a list-price estimate for a session. Without an argument it reads the newest transcript.
