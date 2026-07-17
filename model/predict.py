"""
predict.py — Generalized Integrate-and-Fire (GIF) predictor for a single neuron.

Maps an injected current trace I(t) (picoamps, sampled at dt = 1e-4 s) to the
predicted membrane potential V(t) (millivolts), for the cell recorded in ../data.

================================  THE MODEL  ================================
Subthreshold membrane dynamics (leaky integrator + spike-triggered adaptation):

    C dV/dt = -g_L (V - E_L) + I(t) - I_adapt(t)

    I_adapt(t) = sum_k  w_k * z_k(t),      z_k decays with time constant tau_k
                 (each spike at time t_hat adds 1 to every z_k; between spikes
                  z_k(t) = sum_{t_hat < t} exp(-(t - t_hat)/tau_k) )

Spike generation with a DYNAMIC threshold:

    a spike is emitted at t_hat when   V(t) >= V_T(t)
    V_T(t) = V_T0 + a_theta * theta(t),   theta decays with time constant tau_theta
             (each spike adds 1 to theta)

Reset / refractoriness:

    immediately after a spike:  V -> V_r  and V is clamped for a refractory
    period t_ref;  the adaptation states z_k and the threshold state theta are
    each incremented by 1.

The rendered output pastes a stereotyped action-potential waveform (the
training spike-triggered average) at each emitted spike time, so the returned
trace looks like a real recording (subthreshold trajectory + spikes).

Parameters are in model/params.json (fitted on all training trials). Units:
C [pF], g_L [nS], E_L, V_T0, V_r, a_theta [mV], tau_* [ms], w_k [pA], I [pA],
V [mV], t [s]. See index.qmd for the fitting method and held-out metrics.
============================================================================
"""
import json
import os
import numpy as np

DT = 1e-4  # s, sampling interval of the recordings (10 kHz)

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "params.json")) as _f:
    PARAMS = json.load(_f)


def _p(params):
    """Unpack params dict into simulation constants (SI-ish working units)."""
    C = params["C_pF"] * 1e-3            # nF  (so I[pA]/C -> mV/s with dt in s)
    tau_m = params["tau_m_ms"] * 1e-3    # s
    EL = params["E_L_mV"]
    w = np.asarray(params["eta_w_pA"], float)          # pA
    taus = np.asarray(params["eta_taus_ms"], float) * 1e-3   # s
    VT0 = params["V_T0_mV"]
    Vr = params["V_r_mV"]
    t_ref = int(round(params["t_ref_ms"] * 1e-3 / DT))
    a_th = params["a_theta_mV"]
    tau_th = params["tau_theta_ms"] * 1e-3   # s
    return C, tau_m, EL, w, taus, VT0, Vr, t_ref, a_th, tau_th


def simulate(current_pA, params=PARAMS, dt=DT, v0=None):
    """Forward-integrate the GIF. Returns (V_sub, spike_idx).

    V_sub  : subthreshold membrane trace (mV), NO action-potential waveform
             (voltage is reset to V_r at each spike).
    spike_idx : sample indices at which a spike was emitted.
    """
    I = np.asarray(current_pA, float)
    n = I.shape[0]
    C, tau_m, EL, w, taus, VT0, Vr, t_ref, a_th, tau_th = _p(params)
    decay = np.exp(-dt / taus)
    dth = np.exp(-dt / tau_th)
    K = w.shape[0]
    z = np.zeros(K)
    th = 0.0
    V = np.empty(n)
    V[0] = EL if v0 is None else v0
    spikes = []
    ref = 0
    for t in range(n - 1):
        z = z * decay
        th = th * dth
        eta = float(w @ z)
        if ref > 0:
            V[t + 1] = Vr
            ref -= 1
            continue
        dV = dt * (-(V[t] - EL) / tau_m + (I[t] - eta) / C)
        Vn = V[t] + dV
        if Vn >= VT0 + a_th * th:
            spikes.append(t + 1)
            V[t + 1] = Vr
            z = z + 1.0
            th = th + 1.0
            ref = t_ref
        else:
            V[t + 1] = Vn
    return V, np.array(spikes, dtype=int)


def _render_spikes(V_sub, spike_idx, params=PARAMS):
    """Paste the stereotyped AP waveform (training STA) at each spike time."""
    template = np.asarray(params["template"], float)
    onset = int(params["template_onset_idx"])
    V = V_sub.copy()
    n = len(V)
    L = len(template)
    for s in spike_idx:
        a = s - onset
        b = a + L
        ta, tb = max(0, a), min(n, b)
        if tb > ta:
            V[ta:tb] = template[(ta - a):(tb - a)]
    return V


def predict_voltage(current_pA, params=PARAMS, dt=DT, render_spikes=True, v0=None):
    """I(t) -> V(t).  The predictor required by the mission.

    current_pA : 1-D array of injected current (picoamps) for ONE trial,
                 sampled at dt = 1e-4 s. State is reset per call (each trial is
                 an independent episode).
    render_spikes : if True, paste the stereotyped AP waveform at spike times so
                    the returned trace includes realistic action potentials;
                    if False, return the bare subthreshold trace.
    returns : predicted membrane potential V(t) (mV), same length as input.
    """
    V_sub, spikes = simulate(current_pA, params=params, dt=dt, v0=v0)
    return _render_spikes(V_sub, spikes, params) if render_spikes else V_sub


# --------------------------------------------------------------------------
# CLI: generate held-out predictions for every condition.
#   python model/predict.py                 -> writes predictions/pred_cond*.csv.gz
# --------------------------------------------------------------------------
def _predict_file(in_path, out_path):
    import pandas as pd
    df = pd.read_csv(in_path)
    rows = []
    for tid, tr in df.groupby("trial_id", sort=True):
        tr = tr.sort_values("t_s")
        V = predict_voltage(tr["current_pA"].values)
        rows.append(pd.DataFrame({"trial_id": int(tid),
                                   "t_s": tr["t_s"].values,
                                   "voltage_mV": V}))
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(out_path, index=False, compression="gzip")
    return len(out), df["trial_id"].nunique()


if __name__ == "__main__":
    repo = os.path.dirname(_HERE)
    os.makedirs(os.path.join(repo, "predictions"), exist_ok=True)
    for c in (25, 100, 200, 400):
        ip = os.path.join(repo, "data", f"heldout_inputs_cond{c}Hz.csv.gz")
        op = os.path.join(repo, "predictions", f"pred_cond{c}Hz.csv.gz")
        nrow, ntr = _predict_file(ip, op)
        print(f"cond{c}Hz: {ntr} trials, {nrow} rows -> {op}")
