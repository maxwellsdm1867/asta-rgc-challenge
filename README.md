# Blind neuron-model recovery

Recover an explicit equation for a single neuron's membrane potential `V(t)` from an injected
current `I(t)`, using only the recordings in [`data/`](data/) — then predict held-out inputs.
Four stimulus conditions (current bandwidth 25 / 100 / 200 / 400 Hz) are the **same cell**; one
equation is fit across all four. The full write-up is [`index.qmd`](index.qmd); a one-page visual
brief is [`brief.html`](brief.html).

## The equation — a Generalized Integrate-and-Fire (GIF) model

The model form was **discovered from the data** (a linear dynamic I–V curve, a phase-plane
spike-initiation elbow, and a spike-triggered average — see the report), not assumed.

```
# subthreshold membrane (leaky integrator + spike-triggered adaptation current)
C·dV/dt = −g_L·(V − E_L) + I(t) − Σ_k w_k·z_k(t)      # z_k decays with τ_k; +1 at each spike

# spike with a dynamic (spike-triggered) threshold
spike when V(t) ≥ V_T0 + a_θ·θ(t)                     # θ decays with τ_θ; +1 at each spike

# reset
V → V_r, held for t_ref
```

**Fitted parameters (this cell):**

| membrane | value | | spike | value |
|---|---|---|---|---|
| C | 66.3 pF | | V_T0 | −55.3 mV |
| g_L (R) | 9.88 nS (101 MΩ) | | a_θ / τ_θ | 4.12 mV / 30.5 ms |
| τ_m | 6.71 ms | | V_r | −61.8 mV |
| E_L | −65.2 mV | | t_ref | 3.45 ms |

Spike-triggered adaptation current: `τ_k = [3, 10, 30, 100, 300] ms`,
`w_k = [35.0, −11.9, 23.3, −3.4, 0.22] pA`. Exact values in [`model/params.json`](model/params.json).

## Held-out performance

Metrics on a 20 % held-out split of the training trials (never used for fitting). Spike parameters
were optimized to minimize the **Victor–Purpura distance (q = 4 s⁻¹)**; spikes are detected with an
elbow (2nd-derivative) initiation-point method applied identically to measured and predicted traces.

| condition | VP dist / s (q=4) | Γ (±2 ms) | subthr. RMSE | subthr. R² | rate meas/pred |
|---|---:|---:|---:|---:|---:|
| 25 Hz  | 2.63 | 0.642 | 2.23 mV | 0.875 | 25.0 / 24.1 |
| 100 Hz | 4.45 | 0.564 | 3.11 mV | 0.860 | 41.4 / 45.4 |
| 200 Hz | 2.37 | 0.807 | 1.94 mV | 0.886 | 34.3 / 34.3 |
| 400 Hz | 2.21 | 0.751 | 2.64 mV | 0.870 | 40.0 / 40.3 |
| **mean** | **2.91** | **0.691** | **2.48 mV** | **0.873** | — |

## Repo layout

| path | what |
|---|---|
| [`mission.md`](mission.md) | the task spec |
| [`data/`](data/) | training + held-out-input recordings (gzipped CSV, 10 kHz) |
| [`model/predict.py`](model/predict.py) | the deliverable predictor: `predict_voltage(I) → V` |
| [`model/params.json`](model/params.json) | fitted equation (the parameters above) |
| [`model/glif_fit.py`](model/glif_fit.py) | reproducible fit (regression + VP optimization) |
| [`model/make_report_figures.py`](model/make_report_figures.py) | regenerates `figures/` |
| `predictions/pred_cond*.csv.gz` | held-out predictions (`trial_id, t_s, voltage_mV`) |
| [`index.qmd`](index.qmd) | full report (renders with Quarto) · [`references.bib`](references.bib) |
| [`brief.html`](brief.html) | one-page visual science brief (inline SVG) |
| [`work/`](work/) | project notebook (`project.md` + per-unit READMEs) |
| [`SKILLS_FEEDBACK.md`](SKILLS_FEEDBACK.md) | reflection on the Asta skills (tools, not science) |

## Reproduce

```bash
python3 -m venv venv && source venv/bin/activate
pip install "numpy<2" "pandas>=2" scipy matplotlib numba   # numba optional (speeds the fit)

python model/glif_fit.py             # refit → model/params.json, model/heldout_metrics.json
python model/predict.py              # write predictions/pred_cond*.csv.gz
python model/make_report_figures.py  # regenerate figures/
quarto render                        # build the report into _site/  (optional; needs Quarto)
```

```python
from model.predict import predict_voltage   # I(t) [pA] -> V(t) [mV], one trial, state reset per call
```

> Note: the system Anaconda has a broken numpy/pandas ABI — use the clean `venv` above.
