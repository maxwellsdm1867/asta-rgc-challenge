# Research mission — find the equation for a neuron's membrane potential

## The task
`data/` contains recordings from a **single neuron**. On each trial a fluctuating current
`I(t)` was **injected** into the cell and its **membrane potential** `V(t)` was recorded at the
same time.

**This is an injected current. Find the equation that describes the membrane potential `V(t)`
and can predict the data.**

Produce a model — an explicit equation (or system of equations) — for `V(t)` given `I(t)`, fit
it so it matches the recordings **really well**, and show that it generalizes to held-out data.
Discover the equation from the data; you choose the form and the method.

## Data (`data/`)
Gzipped CSVs (`pd.read_csv(path)` reads `.csv.gz` directly):

| file | columns | use |
|---|---|---|
| `train_cond{25,100,200,400}Hz.csv.gz` | `trial_id, t_s, current_pA, voltage_mV` | fit the equation |
| `heldout_inputs_cond{25,100,200,400}Hz.csv.gz` | `trial_id, t_s, current_pA` | predict `V(t)` for these |

- `dt = 1e-4 s` (10 kHz); voltage in mV, current in pA; each trial is 0.5 s.
- The four files are four stimulus conditions differing in the **temporal bandwidth of the
  injected current** (nominal 25 / 100 / 200 / 400 Hz). Fit **one** equation for this cell across
  all four.
- Each `trial_id` is an **independent recording** — treat each as a separate episode.
- Start by **looking at the data** (plot a few `I(t)` and `V(t)` trials) before modeling.

## Deliverables
1. **The equation** — stated explicitly, with every term defined.
2. **Fitted parameters** — numeric values with units.
3. **A runnable predictor** — `model/predict.py`, a function mapping a trial's `I(t)` → predicted
   `V(t)`.
4. **Held-out predictions** — predicted voltage for every held-out-input trial, saved as
   `predictions/pred_cond{25,100,200,400}Hz.csv.gz` (`trial_id, t_s, voltage_mV`).
5. **A report** (`index.qmd`) — **what equation you found**, how you found it, and **how well it
   does on the held-out set** (report metrics per condition), plus where it fails.

## Ground rules
- Fit the held-out data well **and** keep the equation as simple / interpretable as the data
  allow. State your assumptions.
- If you draw on prior literature, cite it, and say clearly what came from the data vs. from prior
  knowledge.
