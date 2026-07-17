---
slug: derive-equation
status: done
---

# Goal

Enumerate candidate governing equations for `V(t)` given `I(t)` and select the model form from the
data (not from a lookup).

# Instructions

1. From `explore-data`, use three model-free views to constrain the form: the dynamic I–V curve
   (`I - C dV/dt` vs `V`), the phase plot (`dV/dt` vs `V`), and the spike-triggered average.
2. Compare candidate forms: pure leaky-integrate-and-fire; exponential-IF; GIF (leak + spike-triggered
   adaptation current + dynamic threshold); conductance-based (Hodgkin–Huxley).
3. Select the simplest form consistent with the data across all four conditions.

# Results

## Summary
The dynamic I–V curve is **linear below ≈ −50 mV** (a pure leak crossing zero at `E_L ≈ −65 mV`) and
turns sharply inward above threshold (regenerative spike current); the phase plot shows a sharp
spike-initiation elbow and a stereotyped AP loop; the spike-triggered average shows a reset plus a
slow after-hyperpolarisation and spike-frequency adaptation. Together these select a **Generalized
Integrate-and-Fire (GIF/GLIF)** model: linear leaky membrane + spike-triggered adaptation current +
dynamic (spike-triggered) threshold + reset. Hodgkin–Huxley is unnecessary (no continuous
subthreshold nonlinearity is needed); pure LIF is insufficient (misses adaptation/AHP). See
`../../index.qmd` §1, §3.

# Assessment
Form selected from data; consistent across all four bandwidth conditions.
