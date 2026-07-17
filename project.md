# Goal

Discover, fit, and validate an explicit equation for the membrane potential `V(t)` of a single
neuron driven by an injected current `I(t)`, using only the recordings in `data/`. The equation
must be one model that holds across all four stimulus-bandwidth conditions (25/100/200/400 Hz),
generalize to a held-out split of the training trials, and produce predictions for the held-out
input files. Deliverables (per `mission.md`): the explicit equation with defined terms, fitted
numeric parameters with units, a runnable predictor `model/predict.py` (`I(t) → V(t)`),
`predictions/pred_cond{25,100,200,400}Hz.csv.gz`, and the `index.qmd` report with per-condition
held-out metrics.

# Background

- Intracellular current-clamp, 10 kHz (`dt = 1e-4 s`), 5000 samples per 0.5 s trial; four gzipped
  CSV conditions are the SAME cell at different current bandwidths. Each `trial_id` is an
  independent episode — reset model state per trial.
- First-look statistics + traces: the cell rests near −60 mV, fires stereotyped action potentials
  peaking at ~+10 mV with a post-spike afterhyperpolarization to ~−80 mV, at ~25–42 Hz across
  conditions. Subthreshold voltage tracks a low-pass-filtered version of `I(t)`. This is the regime
  the Generalized / Leaky Integrate-and-Fire (GIF / GLIF) family of models was built for.
- Environment: system Anaconda numpy/pandas ABI is broken; use the repo-local `venv/`
  (numpy<2, pandas>=2, scipy, matplotlib). Work only inside this directory.

# Completed Work

# Pending Work

- [explore-data](work/explore-data/README.md) (status: ready) — characterize I(t)/V(t): subthreshold I–V, spike statistics, membrane time constant, post-spike dynamics across the four conditions.
- [derive-equation](work/derive-equation/README.md) (status: pending-plan) — enumerate candidate governing equations and select the model form (GLIF-family) from the data.
- [fit-model](work/fit-model/README.md) (status: pending-plan) — fit one model's parameters across all conditions (subthreshold membrane filter + spike-triggered current + threshold/reset), on a train split.
- [predict-heldout](work/predict-heldout/README.md) (status: pending-plan) — build `model/predict.py` and write `predictions/pred_cond*.csv.gz` for the held-out inputs.
- [write-report](work/write-report/README.md) (status: pending-plan) — write `index.qmd`: the equation, method, fitted params, per-condition held-out metrics, and failure modes.
