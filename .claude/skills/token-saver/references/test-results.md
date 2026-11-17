# token-saver test results (Nov 2026)

## Method

- Headless `claude -p` (Claude Code 2.1.326), model `claude-sonnet-5-5`, 3 runs per configuration.
- Each run starts in a fresh folder holding that case's input files.
- The baseline arm has no skill. The skill arm has a copy of the skill, without its evals folder.
- Correctness was graded by script. For example, the hidden CLI checks for the currency task re-run the program on new data.
- Turns, tokens and cost are taken from Claude Code's own JSON output.
- The whole test cost about $2.10 at list price.

## Results

| Case | Configuration | Pass | Turns | Prompt tok | Output tok | Cost/run |
|---|---|---|---|---|---|---|
| Small bug fix (5 files) | no skill | 100% | 5.0 | 158K | 861 | $0.073 |
| | skill present, never invoked | 100% | 4.0 | 158K | 709 | $0.070 |
| | skill invoked explicitly | 100% | 6.3 | 202K | 731 | $0.075 |
| Huge build log | no skill | 100% | 3.0 | 115K | 548 | $0.053 |
| | skill present, never invoked | 100% | 2.7 | 103K | 720 | $0.056 |
| Currency feature (11 files, hidden checks) | no skill | 100% | 3.0 | 121K | 3,396 | $0.100 |
| | skill invoked explicitly | 100% | 5.0 | 163K | 2,627 | $0.099 |
| "Should I /model to Haiku mid-task?" | no skill | 89% | 1.0 | 38K | 755 | $0.044 |
| | v1 skill (long SKILL.md) | 67% | 3.0 | 80K | 768 | $0.063 |
| | v2 skill (checklist) | 100% | 3.0 | 78K | 531 | $0.052 |

## Findings

1. **The baseline already works efficiently.** On every coding task, the run without the skill already did what the skill teaches:
   - read files in one batched step
   - ran the tests once or a few times
   - never re-read a file after editing it
   - saved the 4,000-line build log to a file once and searched it

   There was little waste left to remove.
2. **The skill doesn't trigger on coding tasks.** Its "while working" advice only applies if the user invokes it explicitly.
3. **Loading the skill has a fixed cost.** Each invocation took 1-2 extra turns and about 40K more prompt tokens, mostly cache reads.
   - On coding tasks this roughly cancelled the small savings in output tokens: cost changed by -1% to +3%.
   - On a quick cost question it added 18% (v2) or 43% (v1).
4. **The advice in answers is more precise with the skill.** For example, it says that changing effort keeps the cache on 5.5 models. The v2 checklist also brought answer length under 250 words.
5. **These tests can't say anything about long sessions.** A 100+ turn session, where failure loops and re-reading build up, is outside what was tested. The tasks here took 3-6 turns.

## Verdict

As an always-on "work efficiently" guide, the skill is not practical with Claude Code and Sonnet 5.5. The model already behaves this way, and invoking the skill costs about as much as it saves.

Two parts are still useful:

- the transcript meter, `scripts/session_cost.py`
- short, accurate answers to "how do I spend less" questions
