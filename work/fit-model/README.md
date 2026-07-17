---
slug: fit-model
status: done
---

# Goal

Fit one GIF parameter set across all four conditions: subthreshold membrane filter + spike-triggered
adaptation current + dynamic threshold + reset, on a train split, and quantify generalization.

# Instructions

1. Detect spikes (elbow v2: max of d²V/dt² on the upstroke).
2. Fit membrane + adaptation current by linear regression of dV/dt on [V, 1, I, z₁..z₅] over
   subthreshold samples (Badel/Mensi/Pozzorini estimator) → C, g_L, E_L, w_k.
3. Optimize spike-generation params (V_T0, a_θ, τ_θ, V_r, t_ref, adaptation scale) by Nelder–Mead
   (multi-start) minimizing pooled Victor–Purpura distance (q = 4 /s).
4. Evaluate on a 20% held-out split; report VP, Γ, subthreshold RMSE/R², firing-rate match.

# Results

## Summary
Fit implemented in `model/glif_fit.py`. Final params (all-data): C=66.3 pF, g_L=9.88 nS (R=101 MΩ),
τ_m=6.71 ms, E_L=−65.2 mV; V_T0=−55.3 mV, a_θ=4.12 mV, τ_θ=30.5 ms; V_r=−61.8 mV, t_ref=3.45 ms;
adaptation τ_k=[3,10,30,100,300] ms, w_k=[35.0,−11.9,23.3,−3.4,0.22] pA. Held-out (20%): mean
VP@q4/s=2.91, Γ=0.69, subthreshold RMSE=2.48 mV, R²=0.87. Metrics in `model/heldout_metrics.json`.

## Artifacts
- `model/params.json` — fitted equation.
- `model/heldout_metrics.json` — per-condition held-out metrics.

# Assessment
Passive params consistent across conditions and corroborated by DataVoyager. Optimizing the grading
metric (VP@q=4) also improved coincidence Γ and fixed 25 Hz under-firing.
