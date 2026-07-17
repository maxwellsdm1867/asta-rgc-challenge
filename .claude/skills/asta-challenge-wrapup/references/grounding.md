# Grounding pass — the fork prompt (phase 4)

The point: check every feedback claim against the **real conversation**, not the files or your memory.
A context-inheriting fork (`Agent` tool, `subagent_type: "fork"`) is the mechanism — it sees what
actually happened. Spawn it with a prompt like this (adapt the file paths and the distinctive
numbers/strings to your run):

```
You inherited this session's FULL conversation/chat history — use it as the source of truth for what
ACTUALLY happened. Do NOT trust the documents' self-description; verify each claim against the real
sequence of events.

Audit every claim in <path>/SKILLS_FEEDBACK.md:
1. Break it into individual factual/experiential claims (the skill-invocation table, each "what
   worked / what was clunky" item, every number, the environment/CLI claims, any git/tooling events).
2. For EACH claim, find the supporting evidence in the inherited conversation and CITE it concretely:
   which tool call produced it and the KEY OUTPUT SNIPPET (quote the actual line — a CLI version, the
   exact numbers a tool printed, a git-state line, a verbatim quote). Point to the specific moment.
3. Verdict each claim:
   - GROUNDED — happened in the conversation; cite the evidence.
   - DOC — grounded, but as skill/tool documentation text that was shown here, not as an event.
   - OVERSTATED — some basis, but the wording claims more than the evidence shows.
   - UNSUPPORTED — no evidence it happened (the important category: plausible but unverifiable).
4. Be adversarial: distinguish "I can cite this happening" from "this is a reasonable inference."
   Pay special attention to numeric claims that must trace to a real printed output.

Write the audit to <path>/FEEDBACK_AUDIT.md as a table:
| # | Claim | Verdict | Evidence in this conversation (tool call -> quoted snippet) |
Then report the counts (GROUNDED / DOC / OVERSTATED / UNSUPPORTED) and list every OVERSTATED and
UNSUPPORTED item with what's wrong. Do NOT edit SKILLS_FEEDBACK.md and do NOT commit — report only.
```

After it returns: fix the flagged claims in `SKILLS_FEEDBACK.md`, add a short **Resolution** note to
the audit, and cross-link the two by claim number (so a reader goes feedback claim → audit row +
quote → `trace.tar.gz`). Then commit both.

Notes:
- If you're **not** in the original session (no real context to inherit), the fork can't help. Fall
  back to auditing against the captured `trace.tar.gz` transcript — still the real record, just read
  from disk instead of inherited.
- Keep the audit honest as a record: don't rewrite its findings, just append the Resolution.
