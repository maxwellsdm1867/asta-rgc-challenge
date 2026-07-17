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

- [explore-data](work/explore-data/README.md) — characterized I(t)/V(t): passive params (C≈66 pF, R≈101 MΩ, τ_m≈6.7 ms, E_L≈−65 mV), spike stats (V_th≈−48 mV, 25–42 Hz), dynamic I–V + phase plot; cross-checked with DataVoyager.
- [derive-equation](work/derive-equation/README.md) — selected the Generalized Integrate-and-Fire (GIF/GLIF) form from the data (linear leak + threshold + reset + spike-triggered adaptation).
- [fit-model](work/fit-model/README.md) — fit one GIF across all four conditions (regression for membrane+adaptation; VP@q=4 optimization for spike params). Held-out: mean VP@q4/s=2.91, Γ=0.69, subthreshold RMSE=2.48 mV.
- [predict-heldout](work/predict-heldout/README.md) — built `model/predict.py` (I→V) and wrote `predictions/pred_cond{25,100,200,400}Hz.csv.gz`.
- [write-report](work/write-report/README.md) — wrote and rendered `index.qmd` (equation, params, per-condition held-out metrics, failure modes) + `references.bib`.

# Pending Work

_All mission deliverables complete. Remaining: SKILLS_FEEDBACK.md (reflection on the Asta skills)._
