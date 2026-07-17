# SKILLS_FEEDBACK — Asta Skills on the blind neuron-model-recovery task

An honest reflection on how the **Asta Skills** performed while I solved this challenge. This is
about the *tools and the experience*, not the science, and it is not compared against anything else.
Written by the solving agent immediately after finishing the run.

## What I actually invoked

| Skill | Role on this task | Worked? |
|---|---|---|
| `asta-assistant:run` | Router to bootstrap/drive the project via `project.md`. | Partially |
| `asta-assistant` (brainstorm / plan-work / do-work / review-* / save-work) | The project state machine I was asked to drive with. | Partially — I read them and adopted the `project.md` + `work/<slug>/README.md` structure, but drove the actual work directly. |
| `asta-tools:analyze-data` (DataVoyager) | Independent EDA / passive-parameter estimation on the four training CSVs. | Yes, as a cross-check — but returned an incomplete answer. |
| `asta-dev:research-challenge` | This reflection. | Yes (as a router → `reflect`). |
| `asta-tools:generate-theories`, `asta-tools:experiment`, `asta-tools:find-literature` | Suggested by the task. | **Not used** — see "Skills I skipped" below. |

The `asta` CLI itself was frictionless: already installed (v0.101.1), token valid, `analyze-data
submit/poll` just worked, uploads and background polling behaved exactly as the skill described.

## What worked well

- **DataVoyager's submit → background-poll → notify flow.** The CLI minted a session, uploaded four
  gzipped CSVs, and the backgrounded `poll` subcommand exited on completion and pinged me. This maps
  cleanly onto the agent harness (no foreground blocking). Auth was invisible.
- **DataVoyager as a corroboration tool.** Asked to estimate passive membrane parameters by
  regressing dV/dt on V and I, it independently reproduced my own fit almost exactly (τ_m = 8.4 / 6.0
  / 6.6 / 9.9 ms; C = 86 / 73 / 72 / 63 pF across conditions) and confirmed low-pass behavior via
  I→V cross-correlation lags. That independent agreement genuinely increased my confidence in the
  membrane fit.
- **The `asta-assistant` artifact convention.** `project.md` (Goal / Background / Completed /
  Pending) plus `work/<slug>/README.md` (Goal / Instructions / Results / Assessment) is a tidy,
  legible way to structure a research project, and it produced clean, self-documenting artifacts.
- **`asta-dev:research-challenge` routing** was clear and pointed me straight at the right workflow.

## What was clunky, slow, or incomplete

1. **The `asta-assistant` loop assumes a human in the loop, which fights an autonomous run.**
   `run` requires a pre-existing `project.md`; the only bootstrap is `brainstorm`, which is explicitly
   conversational ("Confirm before writing… wait for explicit approval"). `plan-work` → `review-plan`
   and `do-work` → `review-work` are gated review loops. With interviews/approvals disabled, every
   gate is a no-op that only adds ceremony. I ended up authoring `project.md` and the work READMEs
   myself and doing the work directly, then reconciling the READMEs afterward — the framework
   described a process I had to route around rather than drive.

2. **`asta-tools:analyze-data` mandates a chat confirmation before submitting.** Step 2 ("Confirm
   with one chat question… Wait for the user's response") is incompatible with a no-interview
   autonomous run. I had to knowingly skip it. There is no documented `--yes`/non-interactive path.

3. **DataVoyager gave up on a multi-part question.** I asked for (1) passive params, (2) spike
   metrics, (3) low-pass consistency. It answered (1) and (3) and then returned:
   *"I'm sorry, but I can't fully answer your question right now… you will need to add that step."*
   It ran only ~15 notebook cells and stopped before the spike detection it had itself planned.
   A single, tightly-scoped question would likely have completed; the skill could warn that
   multi-part asks are fragile, or itself decompose them and loop until all parts are covered.

4. **Getting the answer out of DataVoyager wasn't turnkey.** The task result is a raw
   `DATAVOYAGER` notebook-log JSON (here ~140 KB); the human-readable findings and the numbers I
   wanted were buried in `programmer`/`data_expert`/`dv_answer` cells that I had to parse by hand.
   The skill's Step 6 ("hand off to the Asta Artifacts skill to export") is a *separate* skill I had
   to know to invoke; a completed `analyze-data` run does not, by itself, drop a readable summary or
   the figures next to my project.

5. **Skill outputs are fragile if they live in untracked/ignored files.** Mid-run, the repo's
   untracked/ignored files were cleaned (a maintainer reset), which removed my virtualenv and my
   scratch working code. Not an Asta bug, but it argues that skills which generate working artifacts
   should prefer a committed, discoverable location (or say so), because "it's in scratch/" is not
   durable.

## Skills I skipped, and why (honest)

- **`asta-tools:generate-theories` / `find-literature`.** The model form was over-determined by
  three model-free views of the data (a linear dynamic I–V curve, a phase-plane spike-initiation
  elbow, and a spike-triggered average showing reset + adaptation). Those point unambiguously to the
  Generalized Integrate-and-Fire family. Generating literature-grounded *theories* wasn't the
  bottleneck — recognizing the signatures in the data was — so invoking the theorizer would have been
  ceremony, not signal. For a task where the mechanism is genuinely unknown these would matter more.
- **`asta-tools:experiment` (Panda).** It's framed for software experiments / investigations. My
  "experiment" was a numerical fit (closed-form regression for the membrane + Nelder–Mead for the
  spike parameters against a Victor–Purpura objective) that is faster and more controllable inline
  than as a dispatched agent run. I didn't find a natural seam to hand a tight fit-and-score loop to
  it.

## Concrete suggestions

### `asta-assistant:run` / `brainstorm`
- **Observation:** the only path to a first `project.md` is a conversational `brainstorm`, which
  blocks on approval; `run` can't start without it.
- **Suggested change:** add a non-interactive bootstrap (e.g. `run --autonomous` or
  `brainstorm --from-context`) that drafts `project.md` from the mission file + current context and
  proceeds, and an "autonomous profile" that collapses `plan → do → review` into a single pass when
  no reviewer is present. As written, the review gates are dead weight in a solo/autonomous run.

### `asta-tools:analyze-data`
- **Observation:** Step 2 forces a chat confirmation; multi-part questions can bail; the result is a
  raw notebook log; export is a second skill.
- **Suggested changes:** (a) document a `--yes`/`--non-interactive` submit path; (b) either warn that
  multi-part questions are fragile or have the agent decompose-and-loop until every requested part is
  answered (it planned the spike step and then skipped it); (c) on `completed`, auto-emit a short
  `answer.md` + extracted figures alongside the task JSON so the findings are readable without
  hand-parsing `logs`, rather than requiring a separate Artifacts export.

### `asta-tools:experiment` / `generate-theories`
- **Observation:** neither fit a tight, data-driven system-identification loop (fit parameters →
  score against a spike-train metric → refine).
- **Suggested change:** a lighter "fit-and-score" or "model-selection" entry point (given data + a
  candidate equation family + an objective, fit and cross-validate) would slot into this kind of task
  where the science is a numerical fit, not a literature-driven hypothesis.

### `asta-dev:research-challenge`
- **Observation:** `reflect` is conversational (interview + confirm) and writes
  `RESEARCH_CHALLENGE.md`; this task explicitly wanted a non-interactive `SKILLS_FEEDBACK.md`.
- **Suggested change:** support a non-interactive reflection mode and an output-filename override, so
  an autonomous run can produce the requested file without an interview.

## Bottom line

The **DataVoyager** path (CLI, auth, submit/poll, remote execution) is the strongest piece — it
worked, and its independent estimates were genuinely useful — but it under-delivered on a compound
question and left the findings in a form I had to dig through. The **`asta-assistant`** structure is
a good scaffold whose control flow is built around human review; without a reviewer it becomes
paperwork to route around rather than a driver. The most valuable single improvement across the suite
would be first-class **non-interactive / autonomous modes** (skip confirmations, collapse review
gates, override output names), since every skill I touched assumed a human was waiting to approve the
next step.
