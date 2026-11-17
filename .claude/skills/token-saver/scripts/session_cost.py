#!/usr/bin/env python3
"""Summarize where a Claude Code session's tokens went.

Usage:
    python3 session_cost.py [transcript.jsonl]

With no argument, reads the newest *.jsonl under ~/.claude/projects.
Reports model calls (turns), cache-hit share, full cache rebuilds, output and
thinking tokens, how often tool calls were batched, repeated file reads and
repeated shell commands, plus an estimate at list prices.

The estimate uses public list prices per million tokens and ignores plan
inclusions, discounts and data-residency multipliers. Within a Pro/Max/Ultra
plan's included usage nothing is billed; the figure shows relative weight.
"""
import collections
import glob
import json
import os
import sys

# $/MTok: input, output, 5m cache write, 1h cache write, cache read
# Source: platform.claude.com/docs/en/about-claude/pricing (Nov 2026)
PRICES = {
    "fable-5-2": (8.00, 40.00, 10.00, 16.00, 0.20),
    "mythos-5-2": (8.00, 40.00, 10.00, 16.00, 0.20),
    "opus-5-5": (4.00, 20.00, 5.00, 8.00, 0.20),
    "sonnet-5-5": (2.00, 10.00, 2.50, 4.00, 0.10),
    "haiku-5-5": (0.10, 0.50, 0.125, 0.20, 0.01),  # prompts <= 100K tokens
    "sonnet-4-6": (3.00, 15.00, 3.75, 6.00, 0.30),
    "opus-5": (5.00, 25.00, 6.25, 10.00, 0.50),
}


def price_for(model):
    model = model or ""
    for key in sorted(PRICES, key=len, reverse=True):
        if key in model:
            return PRICES[key]
    return None


def newest_transcript():
    files = glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
    if not files:
        sys.exit("No transcripts found under ~/.claude/projects; pass a path.")
    return max(files, key=os.path.getmtime)


def load_calls(path):
    """Group assistant entries by API message id (one response can span several lines)."""
    calls = collections.OrderedDict()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "assistant":
                continue
            msg = entry.get("message") or {}
            mid = msg.get("id") or entry.get("requestId") or entry.get("uuid")
            call = calls.setdefault(mid, {"model": msg.get("model"), "usage": {}, "tools": [],
                                          "sidechain": bool(entry.get("isSidechain"))})
            if msg.get("usage"):
                call["usage"] = msg["usage"]  # later lines carry the final usage
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    call["tools"].append((block.get("name"), block.get("input") or {}))
    return list(calls.values())


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest_transcript()
    calls = [c for c in load_calls(path) if c["usage"]]
    if not calls:
        sys.exit(f"No assistant calls with usage data in {path}")

    tot = collections.Counter()
    cost = 0.0
    priced = True
    rebuilds = 0
    batched = with_tools = 0
    reads = collections.Counter()
    commands = collections.Counter()
    tool_names = collections.Counter()

    for c in calls:
        u = c["usage"]
        fresh = u.get("input_tokens", 0) or 0
        cread = u.get("cache_read_input_tokens", 0) or 0
        cwrite = u.get("cache_creation_input_tokens", 0) or 0
        out = u.get("output_tokens", 0) or 0
        think = (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
        split = u.get("cache_creation") or {}
        w5 = split.get("ephemeral_5m_input_tokens", 0) or 0
        w1 = split.get("ephemeral_1h_input_tokens", 0) or 0
        if w5 + w1 == 0:
            w5 = cwrite
        tot.update(fresh=fresh, cache_read=cread, cache_write=cwrite, output=out, thinking=think)
        if cwrite > 20_000 and cread < cwrite:
            rebuilds += 1  # most of the prefix was (re)written instead of read
        p = price_for(c["model"])
        if p:
            cost += (fresh * p[0] + out * p[1] + w5 * p[2] + w1 * p[3] + cread * p[4]) / 1e6
        else:
            priced = False
        if c["tools"]:
            with_tools += 1
            if len(c["tools"]) > 1:
                batched += 1
        for name, inp in c["tools"]:
            tool_names[name] += 1
            if name == "Read" and inp.get("file_path"):
                key = (inp["file_path"], inp.get("offset"), inp.get("limit"))
                reads[key] += 1
            if name == "Bash" and inp.get("command"):
                commands[inp["command"].strip()] += 1

    prompt_total = tot["fresh"] + tot["cache_read"] + tot["cache_write"]
    n = len(calls)
    side = sum(1 for c in calls if c["sidechain"])
    models = collections.Counter(c["model"] for c in calls)

    print(f"Transcript: {path}")
    print(f"Model calls (turns): {n}" + (f"  ({side} in subagents)" if side else ""))
    print("Models: " + ", ".join(f"{m} x{k}" for m, k in models.most_common()))
    print(f"Prompt tokens processed: {prompt_total:,}  (avg {prompt_total // n:,} per call)")
    if prompt_total:
        print(f"  cache reads  {tot['cache_read']:>12,}  ({100 * tot['cache_read'] / prompt_total:.1f}%)")
        print(f"  cache writes {tot['cache_write']:>12,}  ({100 * tot['cache_write'] / prompt_total:.1f}%)")
        print(f"  uncached     {tot['fresh']:>12,}  ({100 * tot['fresh'] / prompt_total:.1f}%)")
    print(f"Output tokens: {tot['output']:,}  (thinking {tot['thinking']:,})")
    print(f"Calls that (re)wrote a large prefix (>20K, more written than read): {rebuilds}")
    if with_tools:
        print(f"Calls with tool use: {with_tools}; batched 2+ tools: {batched} ({100 * batched / with_tools:.0f}%)")
    print("Top tools: " + ", ".join(f"{t} x{k}" for t, k in tool_names.most_common(6)))
    rep_reads = [(k, v) for k, v in reads.items() if v > 1]
    if rep_reads:
        print("Repeated identical reads:")
        for (fp, off, lim), v in sorted(rep_reads, key=lambda x: -x[1])[:8]:
            rng = f" [offset={off}, limit={lim}]" if off or lim else ""
            print(f"  x{v}  {fp}{rng}")
    rep_cmds = [(k, v) for k, v in commands.items() if v > 1]
    if rep_cmds:
        print("Repeated identical commands:")
        for cmd, v in sorted(rep_cmds, key=lambda x: -x[1])[:8]:
            print(f"  x{v}  {cmd[:110]}")
    label = "Estimated cost at list prices" + ("" if priced else " (some calls used unpriced models)")
    print(f"{label}: ${cost:.2f}")
    print("Note: within a plan's included usage nothing is billed; use this to compare sessions.")


if __name__ == "__main__":
    main()
