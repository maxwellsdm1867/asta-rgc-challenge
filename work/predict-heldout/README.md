---
slug: predict-heldout
status: done
---

# Goal

Build the runnable predictor `model/predict.py` (`I(t) → V(t)`) and write held-out predictions for the
input-only files.

# Instructions

1. Port the fitted GIF to a self-contained pure-numpy predictor that loads `model/params.json`.
2. Expose `predict_voltage(current_pA) -> voltage_mV` (state reset per trial); render a stereotyped AP
   waveform at each spike.
3. Run over `data/heldout_inputs_cond*Hz.csv.gz` → `predictions/pred_cond*Hz.csv.gz`
   (`trial_id, t_s, voltage_mV`, one row per input sample).

# Results

## Summary
`model/predict.py` implements the predictor and CLI. Generated all four prediction files (validated:
correct columns, row counts match inputs, physiological voltage ranges).

## Artifacts
- `model/predict.py` — the predictor.
- `predictions/pred_cond{25,100,200,400}Hz.csv.gz` — held-out predictions (45/15/30/30 trials).

# Assessment
Pure-numpy output verified identical to the numba fitting simulator (spike times equal). Files
conform to the mission's required schema.
