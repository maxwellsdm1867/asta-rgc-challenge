"""Generate report figures into figures/ (committed). Run after glif_fit.py."""
import os, json, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glif_fit import (load_trials, detect_spikes_elbow, victor_purpura,
                      gamma_coincidence, run_fit, sim, DT, CONDS, REPO)
import predict as P

FIG = os.path.join(REPO, "figures"); os.makedirs(FIG, exist_ok=True)
p = P.PARAMS
COL = {25: "#1f77b4", 100: "#2ca02c", 200: "#ff7f0e", 400: "#d62728"}

# same split as glif_fit for held-out illustration
alltr = {c: load_trials(os.path.join(REPO, "data", f"train_cond{c}Hz.csv.gz")) for c in CONDS}
rng = np.random.default_rng(0); test = {}
for c in CONDS:
    idx = np.arange(len(alltr[c])); rng.shuffle(idx); test[c] = [alltr[c][i] for i in idx[int(0.8*len(alltr[c])):]]

# ---------- Fig 1: prediction overlays (held-out test trial per condition) ----------
fig, axes = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
for ax, c in zip(axes, CONDS):
    v, I, tid = test[c][0]
    Vp = P.predict_voltage(I)
    t = np.arange(len(v)) * DT
    ax.plot(t, v, color="0.4", lw=0.7, label="measured V")
    ax.plot(t, Vp, color=COL[c], lw=0.7, alpha=0.9, label="GIF prediction")
    _, ont = detect_spikes_elbow(v); _, onp = detect_spikes_elbow(Vp)
    ax.plot(ont*DT, np.full(len(ont), 12), "k|", ms=9, label="measured spikes")
    ax.plot(onp*DT, np.full(len(onp), 18), "|", color=COL[c], ms=9, label="predicted spikes")
    ax.set_ylabel(f"{c} Hz\nV (mV)"); ax.set_ylim(-100, 25)
    if c == 25: ax.legend(fontsize=7, ncol=4, loc="lower right")
axes[-1].set_xlabel("time (s)")
axes[0].set_title("Held-out prediction: measured vs. GIF-predicted membrane potential")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_predictions.png"), dpi=110); plt.close()
print("fig_predictions.png")

# ---------- Fig 2: fitted kernels (adaptation current + dynamic threshold) ----------
taus = np.array(p["eta_taus_ms"]); w = np.array(p["eta_w_pA"])
tt = np.linspace(0, 200, 2000)  # ms
eta = np.sum([w[k]*np.exp(-tt/taus[k]) for k in range(len(w))], axis=0)
thr = p["a_theta_mV"]*np.exp(-tt/p["tau_theta_ms"])
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].plot(tt, eta, "k"); ax[0].axhline(0, color="0.7", lw=0.5)
ax[0].set_title("Spike-triggered adaptation current $\\eta(t)$"); ax[0].set_xlabel("ms since spike"); ax[0].set_ylabel("pA (hyperpolarising +)")
ax[1].plot(tt, p["V_T0_mV"]+thr, "purple"); ax[1].axhline(p["V_T0_mV"], color="0.7", ls="--", lw=0.7, label=f"$V_{{T0}}$={p['V_T0_mV']:.1f}")
ax[1].set_title("Dynamic threshold $V_T(t)$ after a spike"); ax[1].set_xlabel("ms since spike"); ax[1].set_ylabel("mV"); ax[1].legend(fontsize=8)
tpl = np.array(p["template"]); ttt = (np.arange(len(tpl))-p["template_onset_idx"])*DT*1000
ax[2].plot(ttt, tpl, "k"); ax[2].axvline(0, color="0.7", lw=0.5)
ax[2].set_title("Stereotyped AP waveform (rendered at spikes)"); ax[2].set_xlabel("ms from initiation"); ax[2].set_ylabel("mV")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_kernels.png"), dpi=110); plt.close()
print("fig_kernels.png")

# ---------- Fig 3: rate scatter + VP-vs-q ----------
qs = [0, 4, 25, 100, 250, 500]
rate_t = {c: [] for c in CONDS}; rate_p = {c: [] for c in CONDS}
vpq = {c: {q: 0.0 for q in qs} for c in CONDS}; Tsec = {c: 0.0 for c in CONDS}
for c in CONDS:
    for v, I, tid in test[c]:
        n = len(v); Vp = P.predict_voltage(I)
        _, ont = detect_spikes_elbow(v); _, onp = detect_spikes_elbow(Vp)
        rate_t[c].append(len(ont)/(n*DT)); rate_p[c].append(len(onp)/(n*DT)); Tsec[c] += n*DT
        for q in qs: vpq[c][q] += victor_purpura(ont, onp, q)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for c in CONDS:
    ax[0].scatter(rate_t[c], rate_p[c], s=18, color=COL[c], alpha=0.7, label=f"{c} Hz")
lim = [0, 80]; ax[0].plot(lim, lim, "k--", lw=0.7); ax[0].set_xlim(lim); ax[0].set_ylim(lim)
ax[0].set_xlabel("measured firing rate (Hz)"); ax[0].set_ylabel("predicted firing rate (Hz)")
ax[0].set_title("Per-trial firing rate (held-out)"); ax[0].legend(fontsize=8)
for c in CONDS:
    ax[1].plot(qs, [vpq[c][q]/Tsec[c] for q in qs], "o-", color=COL[c], label=f"{c} Hz")
ax[1].axvline(4, color="k", ls=":", lw=1); ax[1].text(4, ax[1].get_ylim()[1]*0.9, " grading q=4", fontsize=8)
ax[1].set_xlabel("Victor-Purpura cost q (1/s)"); ax[1].set_ylabel("VP distance per second")
ax[1].set_title("VP distance vs. temporal-precision parameter q")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_metrics.png"), dpi=110); plt.close()
print("fig_metrics.png")

# ---------- Fig 4: dynamic I-V + phase plot (model diagnostics) ----------
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
df = load_trials(os.path.join(REPO, "data", "train_cond200Hz.csv.gz"))
Vs = []; Im = []; C = p["C_pF"]*1e-3
for v, I, tid in df[:30]:
    pk, on = detect_spikes_elbow(v)
    m = np.ones(len(v), bool)
    for q in pk:
        a = max(0, q-20); b = min(len(v), q+100); m[a:b] = False
    m &= (v < -40); m[0] = m[-1] = False
    dv = np.gradient(v)/DT
    Vs.append(v[m]); Im.append(I[m]-C*dv[m])
Vs = np.concatenate(Vs); Im = np.concatenate(Im)
bins = np.linspace(-85, -42, 28); bc = 0.5*(bins[1:]+bins[:-1])
idx = np.digitize(Vs, bins); iv = [Im[idx == i].mean() for i in range(1, len(bins))]
ax[0].plot(bc, iv, "o-", color="0.2")
gl = p["gL_nS"]; EL = p["E_L_mV"]
ax[0].plot(bc, gl*(bc-EL), "r--", lw=1, label=f"leak $g_L(V-E_L)$, R={p['R_MOhm']:.0f}MΩ")
ax[0].axhline(0, color="0.7", lw=0.5); ax[0].axvline(EL, color="b", ls=":", lw=0.7, label=f"$E_L$={EL:.1f}")
ax[0].axvline(p["V_T0_mV"], color="purple", ls=":", lw=0.7, label=f"$V_{{T0}}$={p['V_T0_mV']:.1f}")
ax[0].set_xlabel("V (mV)"); ax[0].set_ylabel("$I-C\\,dV/dt$  (pA)"); ax[0].set_title("Dynamic I-V curve (200 Hz): linear leak + spike onset"); ax[0].legend(fontsize=7)
v, I, tid = df[2]; dv = np.gradient(v)/DT/1000
ax[1].plot(v, dv, lw=0.4, color="0.3"); ax[1].axvline(p["V_T0_mV"], color="purple", ls=":", lw=0.8)
ax[1].set_xlabel("V (mV)"); ax[1].set_ylabel("dV/dt (mV/ms)"); ax[1].set_title("Phase plot: spike-initiation 'elbow'")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_ivcurve.png"), dpi=110); plt.close()
print("fig_ivcurve.png")
print("all figures written to figures/")
