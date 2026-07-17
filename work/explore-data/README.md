---
slug: explore-data
status: ready
---

# Goal

Characterize the `data/` recordings well enough to choose a model form. Quantify, per condition and
pooled: the subthreshold current–voltage relationship, the passive membrane time constant, spike
statistics (rate, threshold voltage, reset/AHP, refractoriness), and how the subthreshold voltage
depends on the recent history of `I(t)`. Produce figures and summary numbers that later steps
(derive-equation, fit-model) can rely on.

# Instructions

1. Load each `data/train_cond{25,100,200,400}Hz.csv.gz` with the venv pandas. Confirm shapes,
   `dt`, per-trial independence.
2. Detect spikes per trial (upward crossing of a high threshold, e.g. −20 mV; refine by dV/dt).
   Report spikes/trial and firing rate per condition. Extract per-spike: threshold voltage (V at
   dV/dt onset), peak, reset voltage, and the post-spike voltage trajectory (spike-triggered
   average AHP).
3. Estimate the passive membrane properties from subthreshold data: regress `dV/dt` on `V` and
   `I(t)` over subthreshold samples (excluding a window around/after each spike) to get an estimate
   of `C`, `g_L` (⇒ `τ_m = C/g_L`, `R = 1/g_L`) and `E_L`. This is the Badel/Mensi dynamic-I–V
   approach.
4. Build the subthreshold I→V linear kernel (STA/Wiener) to show the membrane acts as a low-pass
   filter and estimate its time constant independently of step 3.
5. Save figures under `work/explore-data/data/` and a machine-readable summary
   (`work/explore-data/data/summary.json`) with the fitted numbers.
6. Run `asta-tools:analyze-data` (DataVoyager) on the CSVs to cross-check the exploratory findings.

# Results

# Assessment
