# Asta Research Challenge — submission form (draft)

Copy each field into the submission form. Fields marked **[confirm]** need your input — I won't
guess personal details. Everything else is grounded in this project's data and results.

---

## Project Title

Blind neuron-model recovery: a Generalized Integrate-and-Fire equation for V(t) from injected current

---

## Project Summary  *(short — for judges)*

**Goal.** From an injected current `I(t)` and the recorded membrane voltage `V(t)` of a single neuron
(four current-bandwidth conditions, no answer key), find one explicit equation for `V(t)` and predict
held-out inputs.

**Result.** The data selected a **Generalized Integrate-and-Fire** model — a linear leaky membrane
driven by `I(t)`, plus a spike-triggered adaptation current, a dynamic (spike-triggered) threshold,
and a reset — fit as one parameter set across all four conditions. On a 20 % held-out split (never
used for fitting): mean **Victor–Purpura distance = 2.91 / s (q = 4)**, subthreshold **RMSE = 2.48 mV**,
**R² = 0.87**, with firing rates matched to within a few Hz. *Full equation, fitted parameters, and
per-condition metrics are in the report and the data.*

**Time.** This is a **~2-year experimental project** — most of that time is **data collection**
(intracellular recordings); the **data-analysis** portion is roughly **6–8 months** of human work. In
this challenge, the equation was recovered by the AI agent in a **single automated session**
(≈15 min of compute — local model fits plus one ~3-min cloud DataVoyager run).

---

## Reflections  *(what went well? what went badly?)*

**What went well.**
- The model form was *discovered from the data* (three independent signatures), not assumed, and each
  was backed by a figure; DataVoyager independently corroborated the passive parameters.
- Closed-form regression for the membrane + a small direct search for the spike parameters gave
  stable, physiological values and strong held-out metrics across all four conditions.
- Recovered cleanly when a mid-run repo reset removed the environment: verified the data was
  unchanged, rebuilt, and moved deliverables into the tracked tree so they'd survive.
- Grounded the written feedback with an adversarial review run against the actual session history.

**What went badly / lessons.**
- Wrong turns cost iterations: the first spike detector landed on the AP peak (bad threshold), and
  the first model badly under-fired the 25 Hz condition until I switched to a dynamic threshold.
- I optimized the coincidence factor Γ first and had to re-fit for the Victor–Purpura distance (q = 4)
  once that was identified as the grading metric — I should have pinned the scoring metric up front.
- A first draft of the tools feedback misreported that a git reset had wiped my working code; it had
  survived. The adversarial grounding pass caught it.

---

## Name(s) of people involved

**[confirm]** — the environment shows two identities: git author **Arthur Hong** (arthurh@allenai.org,
from the Asta CLI login) and GitHub account **maxwellsdm1867**. Please put the correct name(s).
The research agent was Claude (Claude Code, Opus 4.8).

---

## Email for communication

**[confirm]** — candidates seen in the environment: `arthurh@allenai.org` (Asta login) or
`maxwellsdm1867@gmail.com`. Use whichever you prefer.

---

## (optional) Supporting file(s) for judges

- **`trace.tar.gz`** — the **full conversation trajectory** (pier-captured; the structured format the
  challenge accepts, including the agent's reasoning and tool usage at each step). ~11 MB; committed
  at the repo root — **upload this with the entry**.
- **Rendered report** (GitHub Pages): https://maxwellsdm1867.github.io/asta-rgc-challenge/report.html
  — the equation, data→model derivation, fitted parameters, and per-condition held-out metrics.
  (Source: `index.qmd`.)
- **Rendered visual brief** (GitHub Pages): https://maxwellsdm1867.github.io/asta-rgc-challenge/brief.html
  — one-page, inline-SVG traces from a real held-out trial. (Source: `brief.html`; also an Artifact:
  https://claude.ai/code/artifact/a97d1da4-61a2-42d9-a248-79aaab487a62)
- `SKILLS_FEEDBACK.md` — tools-only reflection on the Asta skills, with per-claim citations in
  `FEEDBACK_AUDIT.md` (each claim traced to the exact moment in `trace.tar.gz`).

---

## (optional) Pointer to final research environment

GitHub: **https://github.com/maxwellsdm1867/asta-rgc-challenge** (public) ·
rendered pages: **https://maxwellsdm1867.github.io/asta-rgc-challenge/**
Judges can open either directly. A tidied zip of the working directory can be provided as an alternative.

---

*A fuller narrative version of this submission is in `RESEARCH_CHALLENGE.md`. The structured
conversation trajectory has already been generated (`pier capture` → `pier traces`) and committed as
`trace.tar.gz` at the repo root — ready to upload with the entry.*
