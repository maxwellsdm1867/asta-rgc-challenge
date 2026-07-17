# Asta Research Challenge — submission form (draft)

Copy each field into the submission form. Fields marked **[confirm]** need your input — I won't
guess personal details. Everything else is grounded in this project's data and results.

---

## Project Title

Blind neuron-model recovery: a Generalized Integrate-and-Fire equation for V(t) from injected current

---

## Project Summary  *(research goal, results, how much time it took)*

**Goal.** Given only the injected current I(t) and the recorded membrane potential V(t) of a single
neuron — four stimulus conditions differing in current bandwidth (25/100/200/400 Hz), with no answer
key in the repo — discover an explicit equation for V(t), fit it, and predict held-out current inputs.
One equation had to hold across all four conditions.

**Result.** The data selected the model without any lookup: a dynamic I–V curve that is linear below
threshold, a phase-plane spike-initiation elbow, and a spike-triggered average with reset + slow
after-hyperpolarization all point to a **Generalized Integrate-and-Fire (GIF/GLIF)** neuron — a linear
leaky membrane driven by I(t), a spike-triggered adaptation current, a spike-triggered (dynamic)
threshold, and a reset. One parameter set fits all four conditions (C = 66.3 pF, R = 101 MΩ,
τ_m = 6.71 ms, E_L = −65.2 mV; V_T0 = −55.3 mV, a_θ = 4.12 mV, τ_θ = 30.5 ms; V_r = −61.8 mV,
t_ref = 3.45 ms). The membrane and adaptation current were fit in closed form by regressing dV/dt on
[V, 1, I, adaptation states]; the spike parameters were fit to minimize the **Victor–Purpura spike
distance (q = 4 s⁻¹)** with spikes detected by an elbow (2nd-derivative) initiation method. On a 20 %
held-out split of the training trials (never used for fitting): mean **Victor–Purpura distance =
2.91 / s**, coincidence factor **Γ = 0.69** (±2 ms), subthreshold **RMSE = 2.48 mV**, subthreshold
**R² = 0.87**; predicted and measured firing rates agree within a few Hz per condition. DataVoyager,
run independently, reproduced the passive parameters closely — an independent corroboration.

**Time.** One continuous agent session; wall-clock was not tracked (it included several background
runs — DataVoyager and two model fits — plus recovery from a mid-run repo reset). **[confirm exact duration]**

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
- `index.qmd` — the full written report (renders to `_site/index.html` with Quarto): the equation,
  data→model derivation, fitted parameters, and per-condition held-out metrics.
- `brief.html` — a one-page visual science brief (inline SVG, self-contained). Also viewable as an
  Artifact: https://claude.ai/code/artifact/a97d1da4-61a2-42d9-a248-79aaab487a62
- `SKILLS_FEEDBACK.md` — tools-only reflection on the Asta skills, with per-claim citations in
  `FEEDBACK_AUDIT.md` (each claim traced to the exact moment in `trace.tar.gz`).

---

## (optional) Pointer to final research environment

GitHub: **https://github.com/maxwellsdm1867/asta-rgc-challenge**
**Public** — judges can open the URL directly (the repo was made public after the run). A tidied zip
of the working directory can be provided as an alternative.

---

*A fuller narrative version of this submission is in `RESEARCH_CHALLENGE.md`. The structured
conversation trajectory has already been generated (`pier capture` → `pier traces`) and committed as
`trace.tar.gz` at the repo root — ready to upload with the entry.*
