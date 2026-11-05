"""Fit the Waves-ON model: M/S parametric EQ (biquads) + 5-band downward compressor.

Chain (matches the EasyEffects preset built later):
  L/R -> M/S -> EQ(Mid | Side) -> L/R -> 5-band compressor -> limiter
Everything is fitted on the 18 Windows captures (6 tracks x 3 levels).
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from scipy import signal, optimize
from common import *

OUT = ROOT / 'model'
CURVES = json.loads((OUT / 'curves.json').read_text())
F3 = np.array(CURVES['freqs'], float)
EQ_FREQS = [50, 70, 90, 110, 135, 160, 190, 225, 270, 330, 450, 630, 900, 1300, 2000, 3000, 4500, 6500, 9500, 14000]
EQ_Q = [2.0] * 10 + [1.2] * 10
SPLITS = [120, 500, 2000, 6000]            # 5 compression bands
MACRO = [(40, 120), (120, 500), (500, 2000), (2000, 6000), (6000, 16000)]
BLOCK = 480                                 # 10 ms
ATTACK_MS, RELEASE_MS, KNEE_DB = 20.0, 200.0, 6.0
SMOOTH = float(__import__('os').environ.get('EQ_SMOOTH', '0.25'))   # penalty on 2nd difference of band gains


# ------------------------------------------------------------------ EQ
def bell_sos(f0, g, q):
    A = 10 ** (g / 40); w0 = 2 * np.pi * f0 / RATE; al = np.sin(w0) / (2 * q); c = np.cos(w0)
    b = np.array([1 + al * A, -2 * c, 1 - al * A]); a = np.array([1 + al / A, -2 * c, 1 - al / A])
    return np.hstack([b / a[0], a / a[0]])


def eq_db(freqs, gains):
    tot = np.zeros(len(freqs))
    for f0, g, q in zip(EQ_FREQS, gains, EQ_Q):
        sos = bell_sos(f0, g, q)[None, :]
        _, h = signal.sosfreqz(sos, worN=2 * np.pi * np.asarray(freqs) / RATE)
        tot += 20 * np.log10(np.abs(h))
    return tot


def fit_eq(target, weight):
    x0 = np.interp(np.log(EQ_FREQS), np.log(F3), target)
    reg, smooth_w = 0.03, SMOOTH
    def res(g):
        return np.concatenate([(eq_db(F3, g) - target) * weight, reg * g, smooth_w * np.diff(g, 2)])
    sol = optimize.least_squares(res, x0, bounds=(-30, 30), max_nfev=60)
    return sol.x, float(np.sqrt(np.mean(((eq_db(F3, sol.x) - target)) ** 2)))


def apply_eq(x, gm, gs):
    m, s = ms(x)
    for f0, g, q in zip(EQ_FREQS, gm, EQ_Q):
        m = signal.sosfilt(bell_sos(f0, g, q)[None, :], m)
    for f0, g, q in zip(EQ_FREQS, gs, EQ_Q):
        s = signal.sosfilt(bell_sos(f0, g, q)[None, :], s)
    return lr_from_ms(m, s)


# ------------------------------------------------------------------ crossover / compressor
def lr4(fc, kind):
    sos = signal.butter(2, fc, kind, fs=RATE, output='sos')
    return np.vstack([sos, sos])


def split_bands(x):
    bands, rest = [], x
    for fc in SPLITS:
        bands.append(signal.sosfilt(lr4(fc, 'low'), rest, axis=0))
        rest = signal.sosfilt(lr4(fc, 'high'), rest, axis=0)
    bands.append(rest)
    return bands


def block_power(b):
    n = len(b) // BLOCK
    return (b[:n * BLOCK] ** 2).reshape(n, BLOCK, 2).mean(axis=(1, 2))


def gain_reduction(pdb, thr, ratio):
    x = pdb - thr
    k = KNEE_DB
    s = 1 - 1 / ratio
    gr = np.where(x < -k / 2, 0.0, np.where(x > k / 2, s * x, s * (x + k / 2) ** 2 / (2 * k)))
    return -gr                                           # negative dB


def smooth(g_target):
    ca, cr = 1 - np.exp(-10 / ATTACK_MS), 1 - np.exp(-10 / RELEASE_MS)
    out = np.zeros_like(g_target); s = 0.0
    for i, t in enumerate(g_target):
        s += (ca if t < s else cr) * (t - s)
        out[i] = s
    return out


def band_gain_db(pdb, thr, ratio):
    return smooth(gain_reduction(pdb, thr, ratio))


# ------------------------------------------------------------------ data
def caches(gm, gs):
    data = {}
    for t in TRACKS:
        for L in (30, 23, 16):
            base = f'{t}_L{L}'
            eq = apply_eq(source(base), gm, gs)
            on = capture(base, 'on')
            data[base] = dict(
                P=[block_power(b) for b in split_bands(eq)],
                meas=[10 * np.log10(np.mean(block_power(b)) + 1e-30) for b in split_bands(on)],
                src=[10 * np.log10(np.mean(block_power(b)) + 1e-30) for b in split_bands(source(base))])
    return data


def predict(data, params):
    thr, rat = params[:5], params[5:]
    err, rows = [], {}
    for base, d in data.items():
        pred, grs = [], []
        for b in range(5):
            pdb = 10 * np.log10(d['P'][b] + 1e-30)
            g = band_gain_db(pdb, thr[b], rat[b])
            pred.append(10 * np.log10(np.mean(d['P'][b] * 10 ** (g / 10)) + 1e-30))
            grs.append(float(np.mean(g)))
        e = np.array(pred) - np.array(d['meas'])
        err.append(e); rows[base] = dict(pred=pred, gr_mean=grs, err=e.tolist())
    return np.concatenate(err), rows


def fit_dyn(data, x0):
    f = lambda p: predict(data, p)[0]
    lo = [-90] * 5 + [1.0] * 5; hi = [0] * 5 + [8.0] * 5
    sol = optimize.least_squares(f, x0, bounds=(lo, hi), diff_step=0.02, max_nfev=40)
    return sol.x


def main():
    mid_t, side_t = np.array(CURVES['mid_db']), np.array(CURVES['side_db'])
    w_m = 1 / (np.array(CURVES['spread_mid']) + 0.7); w_s = 1 / (np.array(CURVES['spread_side']) + 0.7)
    offset_m = np.zeros(5); offset_s = np.zeros(5)
    params = np.array([-45, -45, -45, -50, -55] + [1.4, 1.4, 1.2, 1.2, 1.1], float)
    for it in range(3):
        tm, ts = mid_t.copy(), side_t.copy()
        for b, (lo, hi) in enumerate(MACRO):
            m = (F3 >= lo) & (F3 < hi)
            tm[m] += offset_m[b]; ts[m] += offset_m[b]
        gm, rm = fit_eq(tm, w_m); gs, rs = fit_eq(ts, w_s)
        print(f'iter {it}: EQ residual RMS mid {rm:.2f} dB side {rs:.2f} dB')
        data = caches(gm, gs)
        # thresholds start from the band level distribution at L23
        if it == 0:
            for b in range(5):
                lv = np.concatenate([10 * np.log10(data[f'{t}_L23']['P'][b] + 1e-30) for t in TRACKS])
                params[b] = np.percentile(lv, 55)
        params = fit_dyn(data, params)
        e, rows = predict(data, params)
        print('  thr', np.round(params[:5], 1), 'ratio', np.round(params[5:], 2), f'| band error RMS {np.sqrt(np.mean(e**2)):.2f} dB')
        gr30 = np.mean([rows[f'{t}_L30']['gr_mean'] for t in TRACKS], axis=0)
        print('  mean gain reduction at -30 LUFS (dB) per band', np.round(gr30, 2))
        offset_m = offset_m - gr30 * 1.0 if it else -gr30   # restore static gain lost to compression at L30
    json.dump(dict(eq_freqs=EQ_FREQS, eq_q=EQ_Q, mid_gains=gm.tolist(), side_gains=gs.tolist(), splits=SPLITS,
                   thresholds_db=params[:5].tolist(), ratios=params[5:].tolist(), attack_ms=ATTACK_MS,
                   release_ms=RELEASE_MS, knee_db=KNEE_DB, eq_rms=[rm, rs]),
              open(OUT / 'model.json', 'w'), indent=1)
    print('per-file band errors (dB):')
    for base, r in rows.items():
        print(f'  {base:18s}', ' '.join(f'{v:+5.1f}' for v in r['err']))


if __name__ == '__main__':
    main()
