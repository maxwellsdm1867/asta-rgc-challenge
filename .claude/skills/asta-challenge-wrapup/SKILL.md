---
name: asta-challenge-wrapup
description: >-
  Wrap up and package an Asta research-challenge run (or any autonomous research
  run) for submission — built around NOT hallucinating the write-up. Its core is
  (1) grounding every feedback/submission claim against the REAL conversation
  context — via a context-inheriting fork that sees what actually happened, not
  just the files or a from-memory summary — and (2) capturing the full session
  trace (trace.tar.gz) so every claim is verifiable against the raw source. Use
  this whenever the user is finishing a challenge and says things like "wrap up
  the challenge", "prepare/package the submission", "write the skills feedback",
  "ground the feedback", "make sure the feedback is true", "cite where that
  happened", "generate the trace", "set up the submission", or "we just finished
  a job, package it". It also verifies deliverables, sets up a clean env,
  scaffolds the submission form fields + RESEARCH_CHALLENGE.md, and optionally
  publishes to GitHub + Pages so the HTML renders. Reach for it even if the user
  names only one piece — the trace and the real-context citation are the
  non-negotiable parts; run it in the session that did the work so the real
  context is available.
---

# Asta research-challenge wrap-up

This skill packages a finished research run into a clean, verifiable submission. Its reason to exist
is **anti-hallucination**: a wrap-up written from memory or from the files alone drifts from what
actually happened (files get edited by linters/resets; summaries invent plausible tool behavior). The
two phases that fix this — **cite-check against the real conversation context (phase 4)** and
**capture the full trace (phase 5)** — are the point of the skill. Everything else is scaffolding
around them.

Run the phases in order, but skip any the user has already done. Each phase says *why* it matters so
you can adapt rather than follow blindly.

## Inputs and outputs

**Inputs**
- The finished run: the repo with its deliverables, and `mission.md` (the required-deliverables spec).
- **The live conversation/session context** — the source of truth for the feedback. The grounding
  pass and the trace both draw on it, so run this skill **in the same session that did the work**. If
  you must run it fresh, the captured trace/transcript becomes the source of truth instead of memory.

**Outputs**
- Verified, **committed** deliverables (equation/params, predictor, predictions, report, references).
- `SKILLS_FEEDBACK.md` — honest, tools-only reflection.
- `FEEDBACK_AUDIT.md` — **per-claim citations to the real session** (the anti-hallucination artifact:
  each claim → the exact tool call/output that backs it; verdicts GROUNDED / DOC / OVERSTATED /
  UNSUPPORTED).
- `trace.tar.gz` — the full session trajectory (every tool call + reasoning; the raw source the audit
  quotes).
- `SUBMISSION.md` (copy-paste form fields) + `RESEARCH_CHALLENGE.md` (fuller narrative).
- Optional: rendered HTML on GitHub Pages; the visual brief as an Artifact.

## 0. Orient

- Read `mission.md` (or the task spec) so you know the **required deliverables** for this challenge.
- `pwd`, `git log --oneline -10`, `git status` — know what exists and what's committed.
- Identify **which Asta skills were actually invoked** this session (look back through the
  conversation: `Skill(...)` calls, `asta ...` CLI calls). You'll reflect on exactly those, not a
  guess.

## 1. Environment (only if you need to run code)

The system Anaconda commonly has a broken numpy/pandas ABI (`import pandas` crashes with
`numpy.dtype size changed`). Use a clean venv, created **outside** the tracked tree or gitignored:

```bash
python3 -m venv venv && source venv/bin/activate
pip install "numpy<2" "pandas>=2" scipy matplotlib numba   # numba optional, speeds fits
```

Add `venv/` (and any `scratch/`) to `.gitignore`.

## 2. Verify deliverables — and COMMIT them

Check every deliverable the mission asks for actually exists and is correct (e.g. an explicit
equation + fitted parameters, a runnable `predict.py`, prediction files with the right schema/row
counts, the report, references). Re-run the predictor on a fresh input to confirm it works
end-to-end, not just that files exist. **Watch out:** re-running the predictor often overwrites the
committed prediction files — write to a temp path, or `git checkout` them back and delete any stray
`__pycache__`, so you verify without dirtying the tree.

**Then commit them.** A maintainer `git clean`/reset can wipe anything untracked or gitignored
mid-run — this actually happens. Deliverables and any code you want to survive must live in the
**tracked** tree and be committed. Commit early and often.

## 3. Write the tools feedback → `SKILLS_FEEDBACK.md`

An honest reflection on **the tools and the experience, not the science**, not compared to anything
else. Cover:
- **What you actually invoked** (a table: skill → role → worked?). Only list skills you truly used.
- **What worked well** (be specific and cite real outcomes — e.g. an independent cross-check that
  agreed with your numbers).
- **What was clunky, slow, or incomplete** (concrete: a mandatory confirmation you had to skip, a
  tool that bailed on a compound request, output that needed hand-parsing).
- **Skills you skipped, and why** (honest — "the answer was over-determined by the data, so the
  theorizer would've been ceremony").
- **Concrete per-skill suggestions** (tie each to a moment it would have changed behavior; propose a
  real change, not "make it smarter").

Ground rule: every experiential claim must be something that **actually happened this session**.
Don't write plausible-sounding tool behavior you didn't observe.

## 4. Ground the feedback adversarially → `FEEDBACK_AUDIT.md`

This is the highest-value phase and the one that prevents hallucination. The failure mode it guards
against is subtle: a feedback claim can be perfectly plausible, well-written, and *false* — a tool
behavior you didn't actually see, a number that drifted, an event that never happened. Neither
re-reading the files nor trusting your own summary can catch that, because both can't tell "this
happened" from "this sounds right."

The fix is to check against the **real conversation context**. **Spawn a reviewer as a
context-inheriting fork** (Agent tool, `subagent_type: "fork"`) — a plain/fresh agent only sees the
files; a fork inherits the actual chat history and can verify whether each claim *actually occurred*
in this session. Tell it to:

- go through `SKILLS_FEEDBACK.md` claim by claim,
- for each, **cite the exact tool call + quoted output** in the conversation that supports it (the
  CLI version string, the specific numbers a tool printed, the git state, etc.),
- verdict each claim GROUNDED / DOC (grounded as skill-doc text that was shown) / OVERSTATED /
  UNSUPPORTED,
- write the citation table to `FEEDBACK_AUDIT.md`, and report every OVERSTATED/UNSUPPORTED item.

**Not in the original session?** If you're wrapping up later or from notes/a trace, a fork adds
nothing — it would only inherit *this* wrap-up session, which never saw the research. In that case
audit against the **captured `trace.tar.gz` transcript** (or the run's notes) as the record — still
the real thing, just read from disk. **Never fall back to your own memory** — that's the exact source
of the hallucination this phase exists to catch. State in the audit which source you used.

Then **fix** the flagged claims in `SKILLS_FEEDBACK.md`, and add a short Resolution note to the
audit. Cross-link the two by claim number so a reader can trace feedback → citation → raw source.
See `references/grounding.md` for a ready-to-use fork prompt.

## 5. Capture the conversation trace → `trace.tar.gz`

**Critical: the trace can only come from the ORIGINAL research session's transcript.** If you're
wrapping up in a fresh/later session, running the helper here captures *this* wrap-up session — not
the research — which is worthless as evidence. So capture the trace from the run that did the work
(that's the main reason to wrap up in-session); if you can't, mark `trace.tar.gz` as `[confirm]` in
`SUBMISSION.md`, to be generated from the original session, and don't ship a wrong-session trace.

The challenge accepts a structured trajectory (every tool call + the agent's reasoning). Generate it
with the bundled helper (it wraps `pier capture` + `pier traces`):

```bash
bash .claude/skills/asta-challenge-wrapup/scripts/make_trace.sh
```

If `pier` isn't installed: `uv tool install "pier @ git+https://github.com/allenai/pier"`. **Verify
the trace is the right session** before trusting it — grep the extracted trajectory for distinctive
content from this run (a metric, a term, the CLI version). Committing an 11 MB trace is fine; it
makes every audit quote verifiable against the raw source.

## 6. Scaffold the submission → `SUBMISSION.md` (+ `RESEARCH_CHALLENGE.md`)

`SUBMISSION.md` holds the form fields, copy-paste ready. Keep each **short**:
- **Project Title**
- **Project Summary** — goal, results (headline metrics), and a **ballpark of human time AND compute
  time**. Distinguish the *real research effort* (e.g. a multi-year experimental project, mostly data
  collection, plus months of analysis) from the *agent run* (minutes of compute). Point to the report
  and data for detail.
- **Reflections** — what went well / what went badly (grounded in real wrong turns this session).
- **Name(s) / Email** — **never fabricate these.** Leave `[confirm]` placeholders and, if useful,
  note the identities visible in the environment (git author, CLI login) for the user to pick.
- **Supporting files** — link the rendered report + brief, and list `trace.tar.gz` as an upload.
- **Research-environment pointer** — the repo URL (and rendered-pages URL if Pages is on).

`RESEARCH_CHALLENGE.md` is the fuller narrative (the `asta-dev:research-challenge` **reflect**
structure: summary, Asta skills used, self-critique, suggested improvements, artifacts). Write it
non-interactively — don't run the conversational interview.

## 7. Render & publish the HTML

GitHub shows committed `.html` as raw source. To make it render, enable **GitHub Pages** and serve
self-contained HTML:
- Render the report to a single self-contained file: `quarto render index.qmd -M embed-resources:true`
  (inlines CSS/JS/images — no `site_libs` dependency), and copy it to `report.html`.
- Ensure any brief/visual HTML is self-contained (inline SVG/CSS, no external CDNs).
- Add a small `index.html` landing that links them; enable Pages from `main`/root:
  `gh api -X POST repos/<owner>/<repo>/pages -f "source[branch]=main" -f "source[path]=/"`.
- Poll `gh api repos/<owner>/<repo>/pages/builds/latest` until `built`, then `curl` each URL to
  confirm `200 text/html`.
- Link the live Pages URLs from `README.md` and `SUBMISSION.md`.

## 8. README as the front door

Make the README a navigation-first landing (hero + CTA links + file map), not a science dump. Then
**match the lead to the audience**: if the readers are the Asta team *developing the skills*, lead
with the tools material — `SKILLS_FEEDBACK.md` → `FEEDBACK_AUDIT.md` → `trace.tar.gz` — and put the
science ("See it, in order: report → the answer → full trace") below.

## Ground rules (carry across every phase)

- **Grounding over polish.** Prefer "I can cite this happening" to a nice-sounding claim. When in
  doubt, verify with a fork against the chat history.
- **Never invent personal or identifying details** (names, emails, affiliations). Use `[confirm]`.
- **Commit deliverables** so a clean/reset can't lose them.
- **Blind-challenge integrity.** If it's a blind challenge, the solution shouldn't be publicly
  reachable until grading. Making a repo public / enabling Pages exposes the answer — only do it when
  the repo owner explicitly directs it, and say so plainly first.
- **Outward-facing actions** (push, make-public, open a PR, publish an Artifact) are the user's call;
  name the consequence, then act on their go-ahead.

## Bundled resources

- `scripts/make_trace.sh` — `pier capture` + `pier traces -o trace.tar.gz`, with a session-content
  sanity check.
- `references/grounding.md` — the fork prompt for the adversarial grounding pass (phase 4).
- `references/submission_template.md` — the `SUBMISSION.md` field skeleton.
