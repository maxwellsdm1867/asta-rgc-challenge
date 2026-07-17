"""
glif_fit.py — fit the Generalized Integrate-and-Fire (GIF) model for this cell.

Pipeline (all derived from data/ only):
  1. detect spikes (elbow / spike-initiation method v2),
  2. estimate the subthreshold membrane filter + spike-triggered adaptation
     current by linear regression of dV/dt (Badel/Mensi/Pozzorini method),
  3. optimise the discrete spike-generation parameters (baseline threshold,
     dynamic-threshold jump/decay, reset, refractory, adaptation scale) to
     MINIMISE the Victor-Purpura spike distance (q = 4 s^-1) between model and
     data, pooled across the four current-bandwidth conditions,
  4. extract a stereotyped action-potential waveform (spike-triggered average),
  5. write model/params.json and model/heldout_metrics.json.

Run:  python model/glif_fit.py
Uses numba if available (≈10x faster optimisation); falls back to pure numpy.
"""
import json, os, time
import numpy as np
import pandas as pd
from scipy.optimize import minimize

DT = 1e-4
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONDS = [25, 100, 200, 400]
Q_GRADE = 4.0   # Victor-Purpura cost (1/s) used for grading

# ----------------------------- data -----------------------------
def load_trials(path):
    df = pd.read_csv(path)
    return [(tr.voltage_mV.values.astype(float), tr.current_pA.values.astype(float), int(tid))
            for tid, tr in df.groupby("trial_id")]

# ----------------------- spike detection ------------------------
def detect_spikes_elbow(v, dt=DT, peak_thr=-10.0, min_sep_ms=2.0, look_ms=4.0, dvdt_min=8000.0):
    """Elbow method v2: AP onset = spike-initiation 'kink', located by the
    maximum of the 2nd derivative d2V/dt2 on the rising phase before each peak."""
    v = np.asarray(v, float)
    dv = np.gradient(v) / dt
    ddv = np.gradient(dv) / dt
    n = len(v)
    minsep = int(round(min_sep_ms * 1e-3 / dt)); look = int(round(look_ms * 1e-3 / dt))
    cand = np.where((v[1:-1] > peak_thr) & (v[1:-1] >= v[:-2]) & (v[1:-1] > v[2:]))[0] + 1
    peaks = []; last = -10**9
    for p in cand:
        if p - last < minsep:
            if peaks and v[p] > v[peaks[-1]]:
                peaks[-1] = p; last = p
            continue
        peaks.append(p); last = p
    onsets = []; keep = []
    for p in peaks:
        lo = max(1, p - look); seg = dv[lo:p]
        if seg.size == 0 or seg.max() < dvdt_min: continue
        rise = np.where(seg > 0)[0]
        if rise.size == 0: continue
        a = lo + rise[0]
        o = a + int(np.argmax(ddv[a:p])) if p > a else a
        onsets.append(o); keep.append(p)
    return np.array(keep, int), np.array(onsets, int)

# --------------------- Victor-Purpura distance ------------------
def victor_purpura(s1, s2, q, dt=DT):
    s1 = np.sort(np.asarray(s1, float)) * dt; s2 = np.sort(np.asarray(s2, float)) * dt
    n, m = len(s1), len(s2)
    if n == 0: return float(m)
    if m == 0: return float(n)
    G = np.zeros((n + 1, m + 1)); G[:, 0] = np.arange(n + 1); G[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        s1i = s1[i-1]
        for j in range(1, m + 1):
            G[i, j] = min(G[i-1, j] + 1, G[i, j-1] + 1, G[i-1, j-1] + q*abs(s1i - s2[j-1]))
    return float(G[n, m])

def gamma_coincidence(true_sp, pred_sp, n, dt=DT, dw_ms=2.0):
    dw = int(round(dw_ms*1e-3/dt))
    used = np.zeros(len(pred_sp), bool); nc = 0
    for ts in true_sp:
        d = np.abs(pred_sp - ts); j = np.where((d <= dw) & (~used))[0]
        if len(j): used[j[0]] = True; nc += 1
    Nt, Np = len(true_sp), len(pred_sp)
    rate = Np/(n*dt); norm = 1 - 2*dw*dt*rate; exp = 2*dw*dt*rate*Nt
    return (nc - exp)/(0.5*(Nt+Np)*norm) if (Nt > 0 and norm > 0) else 0.0

# ----------------- subthreshold + eta regression ----------------
ETA_TAUS_MS = np.array([3.0, 10.0, 30.0, 100.0, 300.0])

def build_eta_regressors(onsets, n, dt=DT, taus_ms=ETA_TAUS_MS):
    taus = taus_ms*1e-3; K = len(taus); decay = np.exp(-dt/taus)
    Z = np.zeros((n, K)); z = np.zeros(K); spk = set(int(s) for s in onsets)
    for t in range(n):
        z = z*decay; Z[t] = z
        if t in spk: z = z + 1.0
    return Z

def fit_subthreshold(trials, dt=DT, taus_ms=ETA_TAUS_MS, t_skip_ms=4.0, v_ceiling=-40.0):
    skip = int(round(t_skip_ms*1e-3/dt)); Xs, ys = [], []
    for v, I in trials:
        n = len(v); pk, on = detect_spikes_elbow(v)
        Z = build_eta_regressors(on, n, dt, taus_ms); dv = np.gradient(v)/dt
        mask = np.ones(n, bool)
        for p in pk:
            a = max(0, p-20); b = min(n, p+skip); mask[a:b] = False
        mask &= (v < v_ceiling); mask[0] = mask[-1] = False
        idx = np.where(mask)[0]
        Xs.append(np.column_stack([v[idx], np.ones(len(idx)), I[idx], -Z[idx]])); ys.append(dv[idx])
    X = np.vstack(Xs); y = np.concatenate(ys)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b, c = coef[0], coef[1], coef[2]; d = coef[3:]
    C = 1.0/c
    return dict(C_nF=C, C_pF=C*1000, gL_nS=-a*C, R_MOhm=1000.0/(-a*C), tau_ms=-1000.0/a,
                EL_mV=-b/a, eta_w_pA=d/c, taus_ms=np.asarray(taus_ms))

# --------------------------- simulate ---------------------------
def simulate_np(I, C_nF, tau_s, EL, w, taus_s, VT0, Vr, t_ref, a_th, tau_th_s, v0):
    n = len(I); K = len(w); decay = np.exp(-DT/taus_s); dth = np.exp(-DT/tau_th_s)
    z = np.zeros(K); th = 0.0; V = np.empty(n); V[0] = v0; spikes = []; ref = 0
    for t in range(n-1):
        z = z*decay; th = th*dth; eta = float(w @ z)
        if ref > 0: V[t+1] = Vr; ref -= 1; continue
        Vn = V[t] + DT*(-(V[t]-EL)/tau_s + (I[t]-eta)/C_nF)
        if Vn >= VT0 + a_th*th:
            spikes.append(t+1); V[t+1] = Vr; z = z+1.0; th = th+1.0; ref = t_ref
        else: V[t+1] = Vn
    return V, np.array(spikes, int)

try:
    from numba import njit
    @njit(cache=True, fastmath=True)
    def _sim_nb(I, C, tau, EL, w, taus, VT0, Vr, t_ref, a_th, tau_th, v0):
        n = I.shape[0]; K = w.shape[0]; decay = np.exp(-DT/taus); dth = np.exp(-DT/tau_th)
        z = np.zeros(K); th = 0.0; V = np.empty(n); V[0] = v0
        spk = np.zeros(n, np.int64); ns = 0; ref = 0
        for t in range(n-1):
            for k in range(K): z[k] *= decay[k]
            th *= dth; eta = 0.0
            for k in range(K): eta += w[k]*z[k]
            if ref > 0: V[t+1] = Vr; ref -= 1; continue
            Vn = V[t] + DT*(-(V[t]-EL)/tau + (I[t]-eta)/C)
            if Vn >= VT0 + a_th*th:
                spk[ns] = t+1; ns += 1; V[t+1] = Vr
                for k in range(K): z[k] += 1.0
                th += 1.0; ref = t_ref
            else: V[t+1] = Vn
        return V, spk[:ns]
    HAVE_NUMBA = True
except Exception:
    HAVE_NUMBA = False

def sim(I, p):
    tref = int(round(p['t_ref_ms']*1e-3/DT)); v0 = p.get('v0', p['EL_mV'])
    args = (np.ascontiguousarray(I), p['C_nF'], p['tau_s'], p['EL_mV'],
            np.ascontiguousarray(p['eta_w_pA'], float), np.ascontiguousarray(p['taus_s'], float),
            p['VT0'], p['Vr'], tref, p['a_th'], p['tau_th_s'], v0)
    return _sim_nb(*args) if HAVE_NUMBA else simulate_np(*args)

# ----------------------------- fit ------------------------------
def run_fit(trainset, conds=CONDS):
    pool = [(v, I) for c in conds for v, I, tid in trainset[c]]
    fit = fit_subthreshold(pool)
    trsp = {c: [detect_spikes_elbow(v)[1] for v, I, tid in trainset[c]] for c in conds}
    base = dict(C_nF=fit['C_nF'], tau_s=fit['tau_ms']/1000, EL_mV=fit['EL_mV'],
                taus_s=fit['taus_ms']*1e-3)
    def mkp(x):
        VT, Vr, tref, keta, a_th, tau_th = x
        return {**base, 'eta_w_pA': fit['eta_w_pA']*keta, 'VT0': VT, 'Vr': Vr,
                't_ref_ms': tref, 'a_th': a_th, 'tau_th_s': tau_th*1e-3}
    if HAVE_NUMBA: sim(trainset[conds[0]][0][1], mkp([-52, -58, 3.5, 0.5, 4, 30]))
    def cond_vp_per_s(p, trials, tsp, q):
        Tsec = 0.0; vp = 0.0
        for (v, I, tid), ton in zip(trials, tsp):
            _, psp = sim(I, p); Tsec += len(v)*DT; vp += victor_purpura(ton, psp, q)
        return vp/Tsec
    def obj(x):
        VT, Vr, tref, keta, a_th, tau_th = x
        if not(-58 < VT < -42 and -62 <= Vr <= -50 and 1 <= tref <= 6 and 0 <= keta <= 1.5
               and 0 <= a_th <= 20 and 5 <= tau_th <= 120): return 1e3
        p = mkp(x)
        # primary: VP@q=4 (grading); light timing regulariser: small weight on VP@q=200
        prim = np.mean([cond_vp_per_s(p, trainset[c], trsp[c], Q_GRADE) for c in conds])
        reg  = np.mean([cond_vp_per_s(p, trainset[c], trsp[c], 200.0) for c in conds])
        return prim + 0.02*reg
    best = None
    for s in [[-52, -58, 3.5, 0.5, 4, 30.0], [-54, -59, 3.8, 0.5, 4, 26.0],
              [-50, -56, 3, 0.3, 6, 20.0], [-48, -57, 4, 0.8, 2, 50.0]]:
        r = minimize(obj, np.array(s, float), method='Nelder-Mead',
                     options=dict(xatol=0.03, fatol=0.001, maxiter=400))
        if best is None or r.fun < best.fun: best = r
    return fit, mkp(best.x), best.x

def eval_split(p, testset, conds=CONDS):
    out = {}
    for c in conds:
        vp4 = []; vpsweep = {q: [] for q in [0, 50, 200, 500]}; G = []; sub = []; r2 = []; frt = []; frp = []
        Tsum = 0.0; vp4sum = 0.0
        for v, I, tid in testset[c]:
            n = len(v); V, psp = sim(I, p); pk, ton = detect_spikes_elbow(v)
            Tsum += n*DT; vp4sum += victor_purpura(ton, psp, Q_GRADE)
            for q in vpsweep: vpsweep[q].append(victor_purpura(ton, psp, q))
            G.append(gamma_coincidence(ton, psp, n)); frt.append(len(ton)/(n*DT)); frp.append(len(psp)/(n*DT))
            mask = np.ones(n, bool)
            for s in np.concatenate([pk, psp]).astype(int):
                a = max(0, s-30); b = min(n, s+40); mask[a:b] = False
            mask &= (v < -45)
            if mask.sum() > 10:
                sub.append(np.sqrt(np.mean((V[mask]-v[mask])**2)))
                r2.append(1 - np.var(V[mask]-v[mask])/np.var(v[mask]))
        out[c] = dict(VP_q4_per_s=vp4sum/Tsum, Gamma=float(np.mean(G)),
                      subRMSE_mV=float(np.mean(sub)), subR2=float(np.mean(r2)),
                      rate_true=float(np.mean(frt)), rate_pred=float(np.mean(frp)),
                      VP_sweep_per_s={str(q): float(np.sum(vpsweep[q])/Tsum) for q in vpsweep})
    return out

def main():
    t0 = time.time()
    alltr = {c: load_trials(os.path.join(REPO, "data", f"train_cond{c}Hz.csv.gz")) for c in CONDS}
    rng = np.random.default_rng(0); train = {}; test = {}
    for c in CONDS:
        idx = np.arange(len(alltr[c])); rng.shuffle(idx); ntr = int(0.8*len(alltr[c]))
        train[c] = [alltr[c][i] for i in idx[:ntr]]; test[c] = [alltr[c][i] for i in idx[ntr:]]
    print(f"numba={HAVE_NUMBA}")
    # Fit A on train split -> honest held-out metrics
    fitA, pA, xA = run_fit(train)
    metrics = eval_split(pA, test)
    print("\n=== HELD-OUT (20% of train trials) ===")
    for c in CONDS:
        m = metrics[c]
        print(f"{c:4d}Hz: VP@q4/s={m['VP_q4_per_s']:.3f}  Gamma={m['Gamma']:.3f}  "
              f"subRMSE={m['subRMSE_mV']:.2f}mV  R2={m['subR2']:.3f}  rate t/p={m['rate_true']:.1f}/{m['rate_pred']:.1f}Hz")
    print(f"MEAN VP@q4/s={np.mean([metrics[c]['VP_q4_per_s'] for c in CONDS]):.3f}  "
          f"Gamma={np.mean([metrics[c]['Gamma'] for c in CONDS]):.3f}  "
          f"subRMSE={np.mean([metrics[c]['subRMSE_mV'] for c in CONDS]):.2f}mV")
    # Fit B on ALL data -> final predictor
    fitB, pB, xB = run_fit(alltr)
    # spike template from all data (aligned to elbow onset)
    pre, post = 15, 55; temps = []
    for c in CONDS:
        for v, I, tid in alltr[c]:
            pk, on = detect_spikes_elbow(v)
            for o in on:
                if o-pre >= 0 and o+post < len(v): temps.append(v[o-pre:o+post])
    template = np.mean(temps, axis=0)
    params = dict(
        model="GIF: leaky membrane + spike-triggered adaptation current + dynamic threshold + reset",
        C_pF=fitB['C_pF'], C_nF=fitB['C_nF'], gL_nS=fitB['gL_nS'], R_MOhm=fitB['R_MOhm'],
        tau_m_ms=fitB['tau_ms'], E_L_mV=fitB['EL_mV'],
        eta_taus_ms=fitB['taus_ms'].tolist(), eta_w_pA=(fitB['eta_w_pA']*xB[3]).tolist(), k_eta=float(xB[3]),
        V_T0_mV=float(xB[0]), V_r_mV=float(xB[1]), t_ref_ms=float(xB[2]),
        a_theta_mV=float(xB[4]), tau_theta_ms=float(xB[5]),
        dt_s=DT, template=template.tolist(), template_onset_idx=pre,
        units=dict(C="pF", gL="nS", R="MOhm", tau="ms", V="mV", I="pA", t="s", eta_w="pA", a_theta="mV"),
        grading=dict(metric="Victor-Purpura distance per second", q_per_s=Q_GRADE,
                     spike_detection="elbow v2 (2nd-derivative spike-initiation)"))
    json.dump(params, open(os.path.join(HERE, "params.json"), "w"), indent=2)
    json.dump(metrics, open(os.path.join(HERE, "heldout_metrics.json"), "w"), indent=2)
    print(f"\nsaved model/params.json + model/heldout_metrics.json  ({time.time()-t0:.1f}s)")
    print("FINAL:", {k: round(v, 3) for k, v in params.items() if isinstance(v, float)})
    print("eta_w_pA:", np.round(np.array(params['eta_w_pA']), 2))

if __name__ == "__main__":
    main()
