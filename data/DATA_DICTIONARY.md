# Data dictionary

Intracellular current-clamp recordings from one neuron. On each trial a fluctuating current was
injected and the membrane voltage was recorded simultaneously at 10 kHz.

## Files
- `train_cond{25,100,200,400}Hz.csv.gz` — training trials (inputs **and** measured voltage).
- `heldout_inputs_cond{25,100,200,400}Hz.csv.gz` — held-out trials, **inputs only** (predict the
  voltage for these).

## Columns
| column | units | meaning |
|---|---|---|
| `trial_id` | — | integer id of an independent trial (episode). Reset state per trial. |
| `t_s` | seconds | time within the trial (0 … 0.4999 s, step `1e-4`). |
| `current_pA` | picoamps | injected current `I(t)` (the input). |
| `voltage_mV` | millivolts | recorded membrane potential `V(t)` (train files only). |

## Conditions
The four files differ only in the **temporal bandwidth** of the injected current (nominal cutoff
25 / 100 / 200 / 400 Hz). Higher cutoff = faster current fluctuations. All four are the **same
cell**; fit one model across all conditions.

## Notes
- `dt = 1e-4 s`, 5000 samples per trial (0.5 s).
- Trials within a file are independent recordings, concatenated in long format (one row per
  time-point). Use `trial_id` to separate them.
